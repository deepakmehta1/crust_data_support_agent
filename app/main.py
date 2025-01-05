from fastapi import FastAPI
from .api import conversation

# Initialize FastAPI app
app = FastAPI(title="Crust Data Support Agent")

# Include routes
app.include_router(conversation.router)
