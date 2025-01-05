from fastapi import FastAPI
from app.api import conversation

# Initialize FastAPI app
app = FastAPI(title="Crust Data Support Agent")

# Include routes
app.include_router(conversation.router)
