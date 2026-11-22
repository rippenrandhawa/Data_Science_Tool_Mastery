"""Create the schema, load the data and execute all 15 SQL exercises.

Evidence: each query's real result set is written to SQL_Lab/outputs/query_nn.txt.

    python run_sql_lab.py
"""

import os
import re
import subprocess
import sys

import pymysql

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT_DIR = os.path.join(HERE, "outputs")
os.makedirs(OUT_DIR, exist_ok=True)

DB = {
    "host": os.environ.get("DB_HOST", "127.0.0.1"),
    "port": int(os.environ.get("DB_PORT", "3306")),
    "user": os.environ.get("DB_USER", "analyst"),
    "password": os.environ.get("DB_PASSWORD", "Analyst@2026"),
    "database": "retail_analytics",
    "charset": "utf8mb4",
}


def run_schema():
    """Execute schema.sql through the mysql command-line client."""
    cmd = ["mysql", f"--host={DB['host']}", f"--port={DB['port']}",
           f"--user={DB['user']}", f"--password={DB['password']}",
           "--default-character-set=utf8mb4"]
    with open(os.path.join(HERE, "schema.sql"), "rb") as handle:
        result = subprocess.run(cmd, stdin=handle, capture_output=True)
    if result.returncode != 0:
        print(result.stderr.decode())
        sys.exit("schema.sql failed")
    print("schema.sql executed")


def load_data():
    result = subprocess.run([sys.executable, os.path.join(HERE, "load_data.py")],
                            capture_output=True, text=True, cwd=ROOT)
    print(result.stdout.strip())
    if result.returncode != 0:
        print(result.stderr)
        sys.exit("load_data.py failed")


def parse_queries(path):
    """Split exercises.sql on `-- @Qnn` markers."""
    text = open(path, encoding="utf-8").read()
    parts = re.split(r"^-- @Q(\d+)\s*$(.*?)(?=^-- @Q\d+\s*$|\Z)",
                     text, flags=re.M | re.S)
    queries = []
    for i in range(1, len(parts), 3):
        number, body = parts[i], parts[i + 1]
        lines = body.strip().splitlines()
        title_lines = []
        while lines and lines[0].strip().startswith("--"):
            title_lines.append(lines.pop(0).strip().lstrip("- ").strip())
        sql = "\n".join(lines).strip()
        title = " ".join(title_lines) if title_lines else sql.splitlines()[0]
        if sql:
            queries.append((number, sql, title))
    return queries


def format_table(cursor, rows):
    """Render a result set as an aligned text table (no third-party deps)."""
    columns = [d[0] for d in cursor.description]
    cells = [[str(c) if c is not None else "NULL" for c in row] for row in rows]
    widths = [len(c) for c in columns]
    for row in cells:
        for i, value in enumerate(row):
            widths[i] = max(widths[i], len(value))
    header = " | ".join(c.ljust(widths[i]) for i, c in enumerate(columns))
    rule = "-+-".join("-" * w for w in widths)
    lines = [header, rule]
    lines += [" | ".join(v.ljust(widths[i]) for i, v in enumerate(row)) for row in cells]
    lines.append(f"\n({len(rows)} row(s))")
    return "\n".join(lines)


def run_queries():
    queries = parse_queries(os.path.join(HERE, "exercises.sql"))
    print(f"exercises parsed: {len(queries)}")
    conn = pymysql.connect(**DB)
    try:
        for number, sql, title in queries:
            with conn.cursor() as cur:
                cur.execute(sql)
                rows = cur.fetchall()
                table = format_table(cur, rows)
            path = os.path.join(OUT_DIR, f"query_{int(number):02d}.txt")
            with open(path, "w", encoding="utf-8") as handle:
                handle.write(f"-- Q{number}: {title}\n\n")
                handle.write(table + "\n")
            print(f"  Q{number}: {len(rows)} rows -> {os.path.basename(path)}")
    finally:
        conn.close()


def main():
    print("=" * 70)
    print("LAB 2 - SQL AND DATABASE ANALYSIS")
    print("=" * 70)
    run_schema()
    load_data()
    print("\nexecuting exercises...")
    run_queries()
    print(f"\nLAB 2 COMPLETE - {len(os.listdir(OUT_DIR))} output files in {OUT_DIR}")


if __name__ == "__main__":
    main()
