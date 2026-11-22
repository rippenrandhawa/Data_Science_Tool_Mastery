"""Build Git_GitHub_Lab as a REAL git repository with genuine history.

Creates a small demo repository that exercises init, staging, committing, branching,
merging, tagging and a .gitignore, then writes the evidence files.
"""

import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
LAB = os.path.join(ROOT, "Git_GitHub_Lab")
DEMO = os.path.join(LAB, "demo_repo")


def run(cmd, cwd):
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"{cmd} failed: {result.stderr}")
    return result.stdout.strip()


def write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        fh.write(content)


def main():
    os.makedirs(DEMO, exist_ok=True)
    run(["git", "init", "-b", "main"], DEMO)
    run(["git", "config", "user.name", "Data Analyst"], DEMO)
    run(["git", "config", "user.email", "analyst@example.com"], DEMO)

    write(os.path.join(DEMO, ".gitignore"),
          "__pycache__/\n*.pyc\n.ipynb_checkpoints/\n.env\n*.log\n")

    write(os.path.join(DEMO, "README.md"),
          "# Demo repository for Lab 8\n\n"
          "A small repository used to demonstrate Git fundamentals: init, staging,\n"
          "committing, branching, merging, tagging and ignoring files.\n")

    write(os.path.join(DEMO, "analysis.py"),
          '"""Small analysis script."""\n\n'
          "import pandas as pd\n\n\n"
          "def load(path):\n"
          '    """Load a CSV file into a DataFrame."""\n'
          "    return pd.read_csv(path)\n")

    run(["git", "add", "."], DEMO)
    run(["git", "commit", "-m",
         "Initial commit: README, .gitignore and analysis.py"], DEMO)

    # branch + merge
    run(["git", "checkout", "-b", "feature/sql-queries"], DEMO)
    write(os.path.join(DEMO, "queries.sql"),
          "-- monthly revenue\n"
          "SELECT DATE_FORMAT(invoice_date, '%Y-%m') AS month,\n"
          "       SUM(line_total) AS revenue\n"
          "FROM order_items\n"
          "GROUP BY month;\n")
    run(["git", "add", "queries.sql"], DEMO)
    run(["git", "commit", "-m", "Add monthly revenue query"], DEMO)
    run(["git", "checkout", "main"], DEMO)
    run(["git", "merge", "--no-ff", "feature/sql-queries",
         "-m", "Merge feature/sql-queries into main"], DEMO)

    # second commit on main, then a tag
    write(os.path.join(DEMO, "analysis.py"),
          '"""Small analysis script."""\n\n'
          "import pandas as pd\n\n\n"
          "def load(path):\n"
          '    """Load a CSV file into a DataFrame."""\n'
          "    return pd.read_csv(path)\n\n\n"
          "def total(df, column):\n"
          '    """Return the sum of a numeric column."""\n'
          "    return float(df[column].sum())\n")
    run(["git", "add", "analysis.py"], DEMO)
    run(["git", "commit", "-m", "Add total() helper to analysis.py"], DEMO)
    run(["git", "tag", "-a", "v0.1", "-m", "First working version"], DEMO)

    # evidence
    os.makedirs(os.path.join(LAB, "evidence"), exist_ok=True)
    log = run(["git", "log", "--oneline", "--graph", "--decorate", "--all"], DEMO)
    status = run(["git", "status"], DEMO)
    branches = run(["git", "branch", "-a"], DEMO)
    tags = run(["git", "tag", "-l"], DEMO)
    write(os.path.join(LAB, "evidence", "git_log.txt"), log + "\n")
    write(os.path.join(LAB, "evidence", "git_status.txt"), status + "\n")
    write(os.path.join(LAB, "evidence", "git_branches.txt"), branches + "\n")
    write(os.path.join(LAB, "evidence", "git_tags.txt"), tags + "\n")
    print(log)
    print("---")
    print(f"demo repo: {DEMO}")


if __name__ == "__main__":
    main()
