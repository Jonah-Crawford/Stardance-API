import re
import time
import requests

from bs4 import BeautifulSoup
from datatime import datetime, timezone
from app.database import init_db, upsert_project, set_metadata

BASE = "https://stardance.hackclub.com/projects/{}"
DELAY = 0.2
MAX_CONSECUTIVE_404S = 30

def get_project(pid):
  url = BASE.format(pid)

  try:
    response = requests.get(url, timeout=8, headers={
      "User-Agent": "Stardance API by @The_Craw"
    })
  except requests.RequestException: return "ERROR"

  if response.status_code == 404: return "404"

  if response.status_code != 200: return "ERROR"

  soup = BeautifulSoup(response.text, "html.parser")
  text = soup.get_text("\n", strip=True)

  title_tag = soup.find("h1")
  title = title_tag.get_text(strip=True) if title_tag else None

  if not title: return "ERROR"

  author_match = re.search(r"By\s+(@[\w.-]+)", text)
  devlog_match = re.search(r"(\d+)\s+Devlogs", text)
  hours_match = re.search(r"([\d.]+)\s+Total hours", text)
  followers_match = re.search(r"(\d+)\s+followers", text)

  return {
    "id": pid,
    "title": title,
    "author": author_match.group(1) if author_match else None,
    "devlogs": int(devlog_match.group(1)) if devlog_match else 0,
    "hours": float(hours_match.group(1)) if hours_match else 0,
    "followers": int(followers_match.group(1)) if followers_match else 0,
    "url": url
  }

def run_scrape(start_id=1, end_id=20000):
  init_db()

  consecutive_404s = 0

  projects_found = 0

  for pid in range(start_id, end_id + 1):
    result = get_project(pid)

    if result == "404":
      consecutive_404s += 1
      print(f"[{pid}] 404 ({consecutive_404s}/{MAX_CONSECUTIVE_404S})")

      if consecutive_404s >= MAX_CONSECUTIVE_404S: break

    elif result == "ERROR": print(f"[{pid}] Error")

    else:
      projects_found += 1
      consecutive_404s = 0
      upsert_project(result)
      print(f"[{pid}] {result['title']}")

    time.sleep(DELAY)

  set_metadata("last_scrape_finished", datetime.now(timezone.utc).isoformat())
  set_metadata("highest_project_id_checked", pid)
  set_metadata("projects_found_this_run", projects_found)

if __name__ == "__main__": run_scrape()
