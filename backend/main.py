import os
from typing import Any

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from openai import OpenAI
from pydantic import BaseModel, Field

try:
    from .database import init_db, list_jobs, recent_chats, save_chat, save_resume_profile
    from .recommender import recommender_instance
    from .resume_parser import (
        expand_skills,
        extract_structured_skills,
        extract_text_from_upload,
        flatten_skills,
        skill_frequency,
    )
except ImportError:
    from database import init_db, list_jobs, recent_chats, save_chat, save_resume_profile
    from recommender import recommender_instance
    from resume_parser import (
        expand_skills,
        extract_structured_skills,
        extract_text_from_upload,
        flatten_skills,
        skill_frequency,
    )

USER_ID = 1
is_ready = False

# Initialize OpenAI client - works with OPENAI_API_KEY env var
openai_client: OpenAI | None = None

def get_openai_client() -> OpenAI | None:
    global openai_client
    if openai_client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            openai_client = OpenAI(api_key=api_key)
    return openai_client

SYSTEM_PROMPT = """You are an expert AI career coach specializing in internship recommendations and career guidance. You help users:

1. Understand why specific internships match their profile
2. Identify skill gaps and create learning paths
3. Provide actionable advice on building portfolios
4. Give interview preparation tips
5. Suggest networking strategies

Your responses should be:
- Concise but helpful (2-4 sentences unless user asks for details)
- Specific to the user's skills and recommended jobs
- Encouraging but realistic
- Action-oriented with clear next steps

You have access to the user's skills and current job recommendations. Reference them specifically in your advice."""

app = FastAPI(
    title="AI Resume Job Discovery API",
    description="Resume parsing, hybrid job recommendations, and career chat for the prototype.",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RecommendationRequest(BaseModel):
    skills: list[str] = Field(default_factory=list)
    interests: list[str] = Field(default_factory=list)
    education: str = ""
    structured_skills: dict[str, list[str]] = Field(default_factory=dict)
    limit: int = 8


class ChatMessage(BaseModel):
    role: str
    text: str


class ChatRequest(BaseModel):
    message: str
    skills: list[str] = Field(default_factory=list)
    recommendations: list[dict[str, Any]] = Field(default_factory=list)
    history: list[ChatMessage] = Field(default_factory=list)


@app.on_event("startup")
def startup() -> None:
    ensure_ready()


def ensure_ready() -> None:
    global is_ready
    if is_ready:
        return
    init_db()
    recommender_instance.refresh()
    is_ready = True


@app.get("/health")
def health() -> dict[str, str]:
    ensure_ready()
    return {"status": "ok"}


@app.get("/jobs")
def jobs() -> list[dict[str, Any]]:
    ensure_ready()
    return list_jobs()


@app.post("/upload_resume")
async def upload_resume(file: UploadFile = File(...)) -> dict[str, Any]:
    ensure_ready()
    if not file.filename:
        raise HTTPException(status_code=400, detail="Missing filename.")

    try:
        raw_text = extract_text_from_upload(file.file, file.filename)
    except RuntimeError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=422, detail=f"Could not parse resume: {error}") from error

    structured_skills = extract_structured_skills(raw_text)
    skills = flatten_skills(structured_skills)
    expanded_skills = expand_skills(skills)

    if not raw_text.strip():
        raise HTTPException(status_code=422, detail="The resume appears to be empty or unreadable.")

    resume_id = save_resume_profile(USER_ID, file.filename, raw_text, structured_skills)
    recommendations = recommender_instance.recommend(
        {
            "skills": expanded_skills,
            "structured_skills": structured_skills,
            "interests": [],
            "education": "",
        }
    )

    return {
        "resume_id": resume_id,
        "user_id": USER_ID,
        "filename": file.filename,
        "text_preview": raw_text[:700],
        "structured_skills": structured_skills,
        "skills": skills,
        "expanded_skills": expanded_skills,
        "skill_frequency": skill_frequency(raw_text, expanded_skills),
        "recommendations": recommendations,
    }


@app.post("/recommend")
def recommend(request: RecommendationRequest) -> list[dict[str, Any]]:
    ensure_ready()
    if not request.skills and not flatten_skills(request.structured_skills):
        return []
    return recommender_instance.recommend(request, limit=request.limit)


@app.post("/chat")
def chat(request: ChatRequest) -> dict[str, Any]:
    ensure_ready()
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    client = get_openai_client()
    if client:
        response = build_ai_chat_response(client, request)
    else:
        response = build_chat_response(request)
    
    chat_id = save_chat(USER_ID, request.message, response)
    return {"id": chat_id, "user_id": USER_ID, "response": response}


@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """Streaming chat endpoint for real-time AI responses."""
    ensure_ready()
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    client = get_openai_client()
    if not client:
        # Fallback to non-streaming response
        response = build_chat_response(request)
        async def single_response():
            yield f"data: {response}\n\n"
            yield "data: [DONE]\n\n"
        return StreamingResponse(single_response(), media_type="text/event-stream")

    return StreamingResponse(
        stream_ai_response(client, request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@app.get("/chats")
def chats() -> list[dict[str, Any]]:
    ensure_ready()
    return recent_chats(USER_ID)


@app.post("/refresh_jobs")
def refresh_jobs() -> dict[str, Any]:
    ensure_ready()
    recommender_instance.refresh()
    return {"status": "refreshed", "jobs": len(recommender_instance.jobs)}


def build_chat_response(request: ChatRequest) -> str:
    message = request.message.lower()
    recommendations = request.recommendations or []
    top_job = recommendations[0] if recommendations else None

    if not top_job:
        return (
            "Upload a resume or add skills first, then I can explain matches, gaps, "
            "and a learning path."
        )

    matched = top_job.get("matched_skills", [])
    missing = top_job.get("missing_skills", [])
    role = top_job.get("role", "this role")
    company = top_job.get("company", "the company")

    if "why" in message or "match" in message:
        return (
            f"{role} at {company} is your best current match because it overlaps with "
            f"{format_list(matched) or 'your strongest profile signals'}. "
            f"The most useful next skills are {format_list(missing) or 'already covered'}."
        )

    if "learn" in message or "improve" in message or "gap" in message:
        gap_skills = missing[:3]
        if not gap_skills:
            return f"You already cover the core listed skills for {role}. Build one portfolio project that proves them together."
        return (
            "Prioritize this learning path: "
            + " -> ".join(skill.title() for skill in gap_skills)
            + f". Then update your resume with a small project using those skills for {role}."
        )

    if "best" in message or "top" in message:
        lines = []
        for index, job in enumerate(recommendations[:3], start=1):
            score = round(job.get("match_score", 0) * 100)
            lines.append(f"{index}. {job['role']} at {job['company']} ({score}%)")
        return "Your top matches are: " + " ".join(lines)

    return (
        f"For {role}, emphasize {format_list(matched) or 'your closest relevant skills'} "
        f"and close gaps around {format_list(missing) or 'project evidence and interview readiness'}."
    )


def format_list(values: list[str]) -> str:
    return ", ".join(value.title() for value in values[:5])


def build_context_message(request: ChatRequest) -> str:
    """Build a context message with user's skills and recommendations."""
    context_parts = []
    
    if request.skills:
        context_parts.append(f"User's skills: {', '.join(request.skills[:15])}")
    
    if request.recommendations:
        jobs_summary = []
        for job in request.recommendations[:5]:
            matched = job.get("matched_skills", [])
            missing = job.get("missing_skills", [])
            score = round(job.get("match_score", 0) * 100)
            jobs_summary.append(
                f"- {job.get('role', 'Unknown')} at {job.get('company', 'Unknown')} "
                f"({score}% match, matches: {', '.join(matched[:3]) or 'none'}, "
                f"gaps: {', '.join(missing[:3]) or 'none'})"
            )
        context_parts.append("Recommended internships:\n" + "\n".join(jobs_summary))
    
    return "\n\n".join(context_parts) if context_parts else "No profile data available yet."


def build_ai_chat_response(client: OpenAI, request: ChatRequest) -> str:
    """Generate an AI response using OpenAI."""
    try:
        context = build_context_message(request)
        
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "system", "content": f"Current user context:\n{context}"},
        ]
        
        # Add conversation history
        for msg in request.history[-10:]:  # Keep last 10 messages
            role = "assistant" if msg.role == "assistant" else "user"
            messages.append({"role": role, "content": msg.text})
        
        # Add current message
        messages.append({"role": "user", "content": request.message})
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=500,
            temperature=0.7,
        )
        
        return response.choices[0].message.content or "I couldn't generate a response. Please try again."
    
    except Exception as e:
        # Fallback to rule-based response on error
        return build_chat_response(request)


async def stream_ai_response(client: OpenAI, request: ChatRequest):
    """Stream AI response using Server-Sent Events."""
    try:
        context = build_context_message(request)
        
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "system", "content": f"Current user context:\n{context}"},
        ]
        
        for msg in request.history[-10:]:
            role = "assistant" if msg.role == "assistant" else "user"
            messages.append({"role": role, "content": msg.text})
        
        messages.append({"role": "user", "content": request.message})
        
        stream = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=500,
            temperature=0.7,
            stream=True,
        )
        
        full_response = ""
        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                full_response += content
                yield f"data: {content}\n\n"
        
        # Save chat after streaming completes
        save_chat(USER_ID, request.message, full_response)
        yield "data: [DONE]\n\n"
        
    except Exception as e:
        # Send error message
        yield f"data: Sorry, I encountered an error. Please try again.\n\n"
        yield "data: [DONE]\n\n"


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
