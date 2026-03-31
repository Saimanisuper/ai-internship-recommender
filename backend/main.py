from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional

# Import the pre-initialized recommender engine
from recommender import recommender_instance

# Setup the FastAPI application instance
app = FastAPI(
    title="InternMatch AI Engine",
    description="A Machine Learning powered Internship Recommendation Engine.",
    version="1.0.0"
)

# Configure Cross-Origin Resource Sharing (CORS) to accept requests from our React App
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this to specific origins (e.g., frontend domain)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class StudentProfile(BaseModel):
    """
    Pydantic Input Model capturing a User's distinct skillset and preferences.
    Used for schema validation on incoming POST requests.
    """
    skills: List[str] = Field(..., description="A rigorous list of strings reflecting the technical skills a user possesses.", example=["python", "machine learning"])
    interests: Optional[List[str]] = Field(default=[], description="Auxiliary interest areas that might inform future recommendations.", example=["cloud computing", "web dev"])
    education: Optional[str] = Field(default="", description="The user's highest degree or current academic pursuit.", example="B.Tech Computer Science")

@app.post("/recommend", response_model=List[dict], summary="Get Personalized ML Recommendations")
def recommend_internships(profile: StudentProfile):
    """
    Main Endpoint.
    Consumes a StudentProfile, invokes the local TF-IDF model, and returns a JSON 
    array of ranked internship positions with matching explainability contexts.
    """
    try:
        # Pass validated object straight to our recommender
        recommendations = recommender_instance.recommend(profile)
        return recommendations
    except Exception as server_error:
        # Wrap underlying algorithm errors to prevent service crashes
        raise HTTPException(
            status_code=500, 
            detail=f"An error occurred while generating recommendations: {str(server_error)}"
        )

if __name__ == "__main__":
    # Standard entry point when executed sequentially vs `uvicorn backend.main:app`
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
