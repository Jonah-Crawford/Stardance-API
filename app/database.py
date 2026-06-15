import sqlite3

DB_PATH = "data/stardance.db"

def connect(): return sqlite3.connect(DB_PATH)

def init_db():
  db = connect()

  db.execute("""
  CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY,
    title TEXT,
    author TEXT,
    devlogs INTEGER,
    hours REAL,
    followers INTEGER,
    url TEXT,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
  )
  """)

  db.commit()
  db.close()

def upsert_project(project):
  db = connect()

  db.execute("""
  INSERT INTO projects (
    id, title, author, devlogs, hours, followers, url, updated_at
  )
  VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
  ON CONFLICT(id) DO UPDATE SET
    title = excluded.title,
    author = excluded.author,
    devlogs = excluded.devlogs,
    hours = excluded.hours,
    followers = excluded.followers,
    url = excluded.url,
    updated_at = CURRENT_TIMESTAMP
  """, (
    project["id"],
    project["title"],
    project["author"],
    project["devlogs"],
    project["hours"],
    project["followers"],
    project["url"]
  ))

  db.commit()
  db.close()
