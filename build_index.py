# build_index.py
import sqlite3, json, os
DB_PATH = "data/poc.db"
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# Create tables: docs and FTS5 index
c.executescript("""
CREATE TABLE docs (
  id INTEGER PRIMARY KEY,
  case_id TEXT,
  title TEXT,
  reporters TEXT,
  source TEXT
);
CREATE VIRTUAL TABLE docs_fts USING fts5(case_id, title, reporters, all_text);
""")

with open("data/records.json", "r", encoding="utf8") as f:
    recs = json.load(f)

for rec in recs:
    case_id = rec["case_ids"][0]
    title = rec["title"]
    reporters = ",".join(rec["reporters"])
    source = rec["source"]
    all_text = rec["all_text"]
    c.execute("INSERT INTO docs (case_id, title, reporters, source) VALUES (?, ?, ?, ?)",
              (case_id, title, reporters, source))
    rowid = c.lastrowid
    c.execute("INSERT INTO docs_fts(rowid, case_id, title, reporters, all_text) VALUES (?,?,?,?,?)",
              (rowid, case_id, title, reporters, all_text))

conn.commit()
conn.close()
print("Built index at", DB_PATH)
