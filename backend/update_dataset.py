import json
import os
import subprocess
import zipfile
from datetime import datetime
from pathlib import Path

import pandas as pd

try:
    from .database import get_connection, init_db
    from .resume_parser import SKILL_GROUPS, extract_structured_skills, flatten_skills
except ImportError:
    from database import get_connection, init_db
    from resume_parser import SKILL_GROUPS, extract_structured_skills, flatten_skills

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DOWNLOAD_DIR = DATA_DIR / "kaggle"
DATASET_ID_FILE = BASE_DIR.parent / "datasetID.txt"


def main() -> None:
    init_db()
    dataset_id = read_dataset_id()
    if not dataset_id:
        raise SystemExit("Add a Kaggle dataset id to datasetID.txt before refreshing jobs.")

    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["kaggle", "datasets", "download", "-d", dataset_id, "-p", str(DOWNLOAD_DIR)],
        check=True,
    )

    archives = list(DOWNLOAD_DIR.glob("*.zip"))
    if not archives:
        raise SystemExit("Kaggle download did not produce a zip file.")
    archive = archives[0]
    with zipfile.ZipFile(archive) as zip_file:
        zip_file.extractall(DOWNLOAD_DIR)

    data_file = find_data_file()
    if data_file is None:
        raise SystemExit("No CSV/JSON dataset file found after download.")

    frame = load_frame(data_file)
    rows = normalize_jobs(frame)
    save_jobs(rows)
    print(f"Imported {len(rows)} jobs from {data_file.name}.")


def read_dataset_id() -> str:
    if not DATASET_ID_FILE.exists():
        return os.getenv("KAGGLE_DATASET_ID", "")
    return DATASET_ID_FILE.read_text(encoding="utf-8").strip()


def find_data_file() -> Path | None:
    candidates = list(DOWNLOAD_DIR.glob("*.csv")) + list(DOWNLOAD_DIR.glob("*.json"))
    return candidates[0] if candidates else None


def load_frame(path: Path) -> pd.DataFrame:
    if path.suffix.lower() == ".json":
        return pd.read_json(path)
    return pd.read_csv(path)


def normalize_jobs(frame: pd.DataFrame) -> list[tuple[str, str, str, str, str, str, str]]:
    columns = {column.lower(): column for column in frame.columns}
    role_col = pick(columns, ["role", "title", "job_title", "position"])
    company_col = pick(columns, ["company", "company_name", "organization"])
    description_col = pick(columns, ["description", "job_description", "details"])
    location_col = pick(columns, ["location", "city"])
    date_col = pick(columns, ["date_posted", "posted_date", "created_at", "date"])

    rows = []
    today = datetime.utcnow().date().isoformat()
    known_skills = sorted({skill for group in SKILL_GROUPS.values() for skill in group})

    for _, item in frame.iterrows():
        description = str(item.get(description_col, "") if description_col else "")
        structured = extract_structured_skills(description)
        skills = flatten_skills(structured)
        if not skills:
            lowered = description.lower()
            skills = [skill for skill in known_skills if skill in lowered]

        role = str(item.get(role_col, "Untitled Role") if role_col else "Untitled Role")
        company = str(item.get(company_col, "Unknown Company") if company_col else "Unknown Company")
        location = str(item.get(location_col, "remote") if location_col else "remote")
        date_posted = str(item.get(date_col, today) if date_col else today)

        rows.append(
            (
                role[:200],
                company[:200],
                description,
                json.dumps(sorted(set(skills))),
                location[:120],
                date_posted[:40],
                "kaggle",
            )
        )

    return rows


def pick(columns: dict[str, str], choices: list[str]) -> str | None:
    for choice in choices:
        if choice in columns:
            return columns[choice]
    return None


def save_jobs(rows: list[tuple[str, str, str, str, str, str, str]]) -> None:
    with get_connection() as connection:
        connection.executemany(
            """
            INSERT OR REPLACE INTO jobs
            (role, company, description, skills, location, date_posted, source)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            rows,
        )
        connection.commit()


if __name__ == "__main__":
    main()
