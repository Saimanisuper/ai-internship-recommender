import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "app.db"
SEED_JOBS_PATH = DATA_DIR / "internships.json"


def get_connection() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db() -> None:
    with get_connection() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT NOT NULL,
                company TEXT NOT NULL,
                description TEXT DEFAULT '',
                skills TEXT NOT NULL,
                location TEXT DEFAULT 'remote',
                date_posted TEXT NOT NULL,
                source TEXT DEFAULT 'seed',
                UNIQUE(role, company)
            );

            CREATE TABLE IF NOT EXISTS resume_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                filename TEXT NOT NULL,
                raw_text TEXT DEFAULT '',
                structured_skills TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id)
            );

            CREATE TABLE IF NOT EXISTS chats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                message TEXT NOT NULL,
                response TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id)
            );
            """
        )
        connection.execute(
            "INSERT OR IGNORE INTO users (id, name) VALUES (?, ?)",
            (1, "Prototype User"),
        )
        connection.commit()
    seed_jobs_if_needed()


def seed_jobs_if_needed() -> None:
    with get_connection() as connection:
        count = connection.execute("SELECT COUNT(*) AS count FROM jobs").fetchone()["count"]
        if count:
            return

        if not SEED_JOBS_PATH.exists():
            return

        with open(SEED_JOBS_PATH, "r", encoding="utf-8") as file:
            jobs = json.load(file)

        today = datetime.utcnow().date().isoformat()
        rows = []
        for job in jobs:
            skills = job.get("skills_required", job.get("skills", []))
            description = job.get("description") or " ".join(skills)
            rows.append(
                (
                    job.get("role", "Untitled Role"),
                    job.get("company", "Unknown Company"),
                    description,
                    json.dumps(skills),
                    job.get("location", "remote"),
                    job.get("date_posted", today),
                    job.get("source", "seed"),
                )
            )

        connection.executemany(
            """
            INSERT OR IGNORE INTO jobs
            (role, company, description, skills, location, date_posted, source)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            rows,
        )
        connection.commit()


def row_to_job(row: sqlite3.Row) -> dict[str, Any]:
    skills = json.loads(row["skills"]) if row["skills"] else []
    return {
        "id": row["id"],
        "role": row["role"],
        "company": row["company"],
        "description": row["description"],
        "skills_required": skills,
        "location": row["location"],
        "date_posted": row["date_posted"],
        "source": row["source"],
    }


def list_jobs(limit: int = 100) -> list[dict[str, Any]]:
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT * FROM jobs ORDER BY date_posted DESC, id DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return [row_to_job(row) for row in rows]


def save_resume_profile(
    user_id: int,
    filename: str,
    raw_text: str,
    structured_skills: dict[str, list[str]],
) -> int:
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO resume_profiles
            (user_id, filename, raw_text, structured_skills, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                user_id,
                filename,
                raw_text,
                json.dumps(structured_skills),
                datetime.utcnow().isoformat(),
            ),
        )
        connection.commit()
        return int(cursor.lastrowid)


def save_chat(user_id: int, message: str, response: str) -> int:
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO chats (user_id, message, response, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (user_id, message, response, datetime.utcnow().isoformat()),
        )
        connection.commit()
        return int(cursor.lastrowid)


def recent_chats(user_id: int = 1, limit: int = 25) -> list[dict[str, Any]]:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, user_id, message, response, created_at
            FROM chats
            WHERE user_id = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (user_id, limit),
        ).fetchall()

    return [dict(row) for row in reversed(rows)]
