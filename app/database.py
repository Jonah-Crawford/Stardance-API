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

  db.execute("""
  CREATE TABLE IF NOT EXISTS project_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    scraped_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    hours REAL,
    followers INTEGER,
    devlogs INTEGER
  )
  """)

  db.execute("""
  CREATE INDEX IF NOT EXISTS idx_snapshots_project_time
  ON project_snapshots(project_id, scraped_at)
  """)

  db.execute("""
  CREATE INDEX IF NOT EXISTS idx_snapshots_time
  ON project_snapshots(scraped_at)
  """)

  db.execute("""
  CREATE TABLE IF NOT EXISTS metadata (
    key TEXT PRIMARY KEY,
    value TEXT
  )
  """)

  db.commit()
  db.close()

def insert_snapshot(project):
  db = connect()

  db.execute("""
  INSERT INTO project_snapshots (
    project_id,
    hours,
    followers,
    devlogs
  )
  VALUES (?, ?, ?, ?)
  """, (
    project["id"],
    project["hours"],
    project["followers"],
    project["devlogs"]
  ))

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

def set_metadata(key, value):
  db = connect()

  db.execute("""
  INSERT INTO metadata (key, value)
  VALUES (?, ?)
  ON CONFLICT(key) DO UPDATE SET
    value = excluded.value
  """, (key, str(value)))

  db.commit()
  db.close()

def get_metadata():
  db = connect()

  rows = db.execute("""
  SELECT key, value
  FROM metadata
  """).fetchall()

  db.close()

  return {key: value for key, value in rows}
