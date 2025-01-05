from fastapi import FastAPI
from app.api import conversation, knowledge_base

# Initialize FastAPI app
app = FastAPI(title="Crust Data Support Agent")

# Include routes
app.include_router(conversation.router)
app.include_router(
    knowledge_base.router, prefix="/knowledge_base", tags=["Knowledge Base"]
)
