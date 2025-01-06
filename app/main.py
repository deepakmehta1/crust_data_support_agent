from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import conversation, knowledge_base

# Initialize FastAPI app
app = FastAPI(title="Crust Data Support Agent")

# Allow CORS for all origins or specify the allowed origins (e.g., ["http://localhost:3000"])
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*"
    ],  # Allows all origins (you can specify a list of allowed origins)
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

# Include routes
app.include_router(conversation.router)
app.include_router(
    knowledge_base.router, prefix="/knowledge_base", tags=["Knowledge Base"]
)
