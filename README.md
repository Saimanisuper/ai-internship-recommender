# InternMatch AI Engine 🚀

**InternMatch AI** is a fully functional, personalized Internship Recommendation system built to accurately map a student’s skillset with real-world job postings using Machine Learning, rather than basic string-matching logic.

This codebase provides an authentic full-stack application leveraging **FastAPI** (Python backend), a custom **TF-IDF & Cosine Similarity ML Engine**, and a dynamic, glassmorphism-styled **React / Vite** frontend.

## ✨ Features

- **🎓 Student Profiling:** Submit your technical skills, interests, and academic background via a dedicated portal.
- **🧠 Machine Learning Engine:** Utilizes Scikit-Learn's `TfidfVectorizer` to calculate precise mathematical `cosine_similarity` between your search queries and internship required skills. 
- **📈 Explainable AI:** Beyond simply generating rankings, the algorithm explicitly parses intersection datasets to provide natural-language reasoning behind its match choices. For example: *"You match this role due to Python and SQL; learning AWS will improve your chances."*
- **🎨 Premium UI/UX:** A robust Vanilla CSS dark-gradient application built entirely without templates, displaying animated routes, active states, and custom responsive component grids.

---

## 🏗️ Architecture Stack

- **Backend:** Python 3, FastAPI, Uvicorn, Pydantic, Scikit-Learn (TF-IDF model).
- **Frontend:** React, Vite, React-Router-DOM, Lucide-React (Icons), optimized Vanilla CSS.
- **Data:** Clean, localized JSON mocked structured datasets representing real-world roles.

---

## ⚙️ How to Run Locally

If you'd like to experience the application on your own machine, simply boot up the two development servers.

### 1. The Backend (ML Engine + API)

Navigate into the `backend` directory, install requirements, and spin up the ASGI server:
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```
The REST API will launch at `http://localhost:8000`. You can access automated Swagger UI documentation at `http://localhost:8000/docs`.

### 2. The Frontend (React Development Server)

Open a new terminal window, traverse into the `frontend` folder, instantiate `node_modules`, and run Vite:
```bash
cd frontend
npm install
npm run dev
```
The User Interface will be exposed at `http://localhost:5173`. Open this URL in any modern browser!

---

## 👩‍💻 Understanding the Recommendation Logic

Inside `backend/recommender.py`, you'll find an intelligent, modularized algorithm:
1. When the server launches, the system prepares a document corpus based strictly on the required skills mapping for every available mock dataset application.
2. A `TfidfVectorizer` matrix is fitted against this entire corpus. 
3. When you submit your skills via the React UI, your query is injected directly into this established matrix space to generate dense intersection vectors. 
4. The engine blends high-confidence ML ranking strings with distinct keyword tracking variables to ensure the final explanation generated is consistently interpretable and reliable.
