from fastapi import FastAPI
from app.database import connect, init_db, get_metadata

app = FastAPI(title="Stardance API")

@app.on_event("startup")
def startup(): init_db()

@app.get("/")
def home():
  return {
    "name": "Stardance API",
    "endpoints": [
      "/projects",
      "/projects/top/hours",
      "/projects/top/followers",
      "/projects/{project_id}"
    ]
  }

@app.get("/projects")
def get_projects(limit: int = 100, offset: int = 0):
  db = connect()
  db.row_factory = lambda cursor, row: {
    col[0]: row[i] for i, col in enumerate(cursor.description)
  }

  rows = db.execute("""
  SELECT *
  FROM projects
  ORDER BY id ASC
  LIMIT ? OFFSET ?
  """, (limit, offset)).fetchall()

  db.close()
  return rows

@app.get("/projects/top/{field}")
def top_projects(field: str, limit: int = 100):
  allowed = {
    "hours": "hours",
    "followers": "followers",
    "devlogs": "devlogs"
  }

  if field not in allowed:
    return {"error": "Invalid field"}

  db = connect()
  db.row_factory = lambda cursor, row: {
    col[0]: row[i] for i, col in enumerate(cursor.description)
  }

  rows = db.execute(f"""
  SELECT *
  FROM projects
  ORDER BY {allowed[field]} DESC
  LIMIT ?
  """, (limit,)).fetchall()

  db.close()
  return rows

@app.get("/projects/{project_id}")
def get_project(project_id: int):
  db = connect()
  db.row_factory = lambda cursor, row: {
    col[0]: row[i] for i, col in enumerate(cursor.description)
  }

  row = db.execute("""
  SELECT *
  FROM projects
  WHERE id = ?
  """, (project_id,)).fetchone()

  db.close()

  if not row: return {"error": "Project not found"}

  return row

@app.get("/stats")
def stats():
  db = connect()
  metadata = get_metadata()

  project_count = db.execute("""
  SELECT COUNT(*)
  FROM projects
  """).fetchone()[0]

  total_hours = db.execute("""
  SELECT COALESCE(SUM(hours), 0)
  FROM projects
  """).fetchone()[0]

  total_followers = db.execute("""
  SELECT COALESCE(SUM(followers), 0)
  FROM projects
  """).fetchone()[0]

  db.close()

  return {
    "projects_indexed": project_count,
    "total_hours": total_hours,
    "total_followers": total_followers,
    "metadata": metadata
  }
