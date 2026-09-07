from fastapi import FastAPI, Header, HTTPException
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("API_KEY")


app = FastAPI(
    title="GramSwaram Secure API",
    description="API with authentication",
    version="1.0.0",
)


@app.get("/")
def home():
    return {"message": "GramSwaram Secure API is running"}


@app.get("/farmer-info")
def farmer_info(x_api_key: str | None = Header(default=None)):

    if x_api_key != API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key",
        )

    return {
        "farmer": "Ravi",
        "location": "Telangana",
        "crops": ["Paddy", "Cotton"],
    }