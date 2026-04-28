# PROJECT: AI Resume-Based Job Discovery & Conversational Recommendation System

## 1. Objective

Build a full-stack AI system that:

- Accepts user login/signup
- Allows resume upload
- Extracts structured skills using NLP + GenAI
- Retrieves relevant jobs from an auto-updating dataset
- Matches jobs using advanced feature engineering + hybrid ML
- Displays results in a chat-based UI
- Allows follow-up queries using GenAI
- Stores chats and results in SQL database

## 2. System Flow

User -> Signup/Login
-> Upload Resume
-> Resume Parsing (NLP + GenAI)
-> Feature Engineering Engine
-> Job Dataset Pipeline (auto-updated)
-> Matching Engine (Hybrid ML)
-> Chat Interface (GenAI-powered)
-> Store results + chat in SQL

## 3. Auth System

For the MVP, skip full authentication and use a fixed user id.

```python
user_id = 1
```

Optional later improvement:

- Add JWT-based authentication.

## 4. Resume Upload and Parsing

### 4.1 Extract Text

Use `pdfplumber` or PyMuPDF.

```python
import pdfplumber

with pdfplumber.open(file) as pdf:
    text = "".join(page.extract_text() for page in pdf.pages)
```

### 4.2 GenAI Skill Extraction

Prompt:

```text
Extract all relevant skills from this resume.
Group into:
- core_skills
- tools
- technologies
- soft_skills

Return JSON.
```

### 4.3 Normalize Output

```python
skills = [s.lower().strip() for s in extracted_skills]
```

## 5. Feature Engineering

### 5.1 Skill Expansion

Examples:

- ML -> machine learning, deep learning
- Backend -> APIs, databases

Use a synonym dictionary or GenAI-based expansion.

### 5.2 Skill Weighting

```python
weights = {
    "core_skills": 1.0,
    "tools": 0.7,
    "soft_skills": 0.3,
}
```

### 5.3 Embedding Generation

Use `sentence-transformers`.

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")
embeddings = model.encode(skills)
```

### 5.4 Final Feature Vector

Combine:

- Embeddings
- Weighted scores
- Skill frequency

## 6. Job Dataset Pipeline

### 6.1 Dataset Source

Use a Kaggle tech jobs dataset with `date_posted`.

### 6.2 Download Script

Install Kaggle CLI:

```bash
pip install kaggle
```

Set up the Kaggle API key, then download:

```bash
kaggle datasets download -d <dataset-name>
unzip dataset.zip
```

### 6.3 Data Preprocessing

```python
df["description"] = df["description"].str.lower()
df["date_posted"] = pd.to_datetime(df["date_posted"])
```

### 6.4 Skill Extraction From Jobs

```python
def extract_skills(text):
    return [skill for skill in SKILLS if skill in text]
```

### 6.5 Time Filtering

Simulate real-time relevance by filtering recent jobs.

```python
from datetime import datetime, timedelta

df = df[df["date_posted"] >= datetime.now() - timedelta(days=7)]
```

### 6.6 Store in Database

Convert processed jobs to JSON or SQL rows.

### 6.7 Automation

Option A: Cron job

```bash
0 0 * * * python update_dataset.py
```

Option B: Manual trigger

- Add a "Refresh Jobs" button.

## 7. Matching Engine

### 7.1 TF-IDF

```python
vectorizer = TfidfVectorizer()
```

### 7.2 Embedding Similarity

```python
cosine_similarity(user_vec, job_vec)
```

### 7.3 Skill Overlap

```python
len(matched_skills) / len(required_skills)
```

### 7.4 Final Score

```python
score = 0.5 * embedding + 0.3 * tfidf + 0.2 * overlap
```

## 8. Chat System

### 8.1 Behavior

- Jobs are displayed as AI messages.
- Users can ask follow-up questions.

### 8.2 Prompt

```text
You are a career assistant.
Given user skills and job:
- Explain match
- Suggest improvements
- Recommend learning path
```

Example:

User:

```text
Why this job?
```

AI:

```text
You match due to Python, SQL. Learn Docker.
```

## 9. Database Design

### 9.1 Users

- `id`
- `name`

### 9.2 Jobs

- `id`
- `role`
- `company`
- `skills`
- `date_posted`

### 9.3 Chats

- `id`
- `user_id`
- `message`
- `response`
- `timestamp`

## 10. Frontend

Use a neo-brutalist UI style.

Colors:

- Background: `#2B1B12`
- Primary: `#1F3D2B`
- Accent: `#E6D3A3`

Components:

- Chat UI
- Resume upload box
- Job cards inside chat
- Skill tags

Behavior:

- AI messages display jobs.
- User messages display user queries.

## 11. Backend

Use FastAPI.

Endpoints:

- `/upload_resume`
- `/recommend`
- `/chat`
- `/jobs`

## 12. Testing

Cases:

- Full match
- Partial match
- No match
- Invalid resume

## 13. Edge Cases

- Empty skills
- No jobs found
- Duplicate entries
- Broken resume

## 14. Deployment

Later deployment options:

- Render
- Railway
- PostgreSQL database

## Final Note

This system combines:

- NLP resume parsing
- Advanced feature engineering
- Hybrid ML ranking
- GenAI conversational interface
