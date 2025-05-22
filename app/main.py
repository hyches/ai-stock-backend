from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="AI Stock Portfolio API",
    description="Backend API for AI-driven stock portfolio management",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://preview--alpha-ai-portfolio-pro.lovable.app"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "Welcome to AI Stock Portfolio API",
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    } 