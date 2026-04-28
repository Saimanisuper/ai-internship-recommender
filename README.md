# AI Resume-Based Job Discovery

Full-stack prototype for resume parsing, hybrid job matching, and conversational career recommendations.

## What Is Implemented

- Fixed prototype user: `user_id = 1`
- Resume upload endpoint for PDF/text files
- Rule-based NLP skill extraction with grouped skills
- Skill expansion and weighted feature engineering
- SQLite database for users, jobs, resume profiles, and chats
- Hybrid recommendation engine using TF-IDF plus skill overlap
- Chat endpoint that explains matches and learning gaps
- React/Vite neo-brutalist chat-first UI
- Kaggle dataset refresh script scaffold

## Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

API runs at `http://localhost:8000`.

Endpoints:

- `GET /health`
- `GET /jobs`
- `POST /upload_resume`
- `POST /recommend`
- `POST /chat`
- `GET /chats`
- `POST /refresh_jobs`

## Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:5173`.

Set `VITE_API_URL` if the backend is not on `http://localhost:8000`.

## Dataset Refresh

Add a Kaggle dataset id to `datasetID.txt`, configure Kaggle credentials, then run:

```bash
cd backend
python update_dataset.py
```

The script downloads the dataset, normalizes likely job columns, extracts skills, and stores rows in SQLite.

## Notes

The current GenAI behavior is implemented as deterministic local assistant logic so the prototype works without external API keys. The backend boundaries are ready for an OpenAI or other LLM call inside resume skill extraction and chat response generation.
