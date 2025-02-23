from api.routers import direct_chat, rag_copilot
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

# Setup FastAPI app
app = FastAPI(title="API Server", description="API Server", version="v1")


# Enable CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=False,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# Routes
@app.get("/")
async def get_index():
    return {"message": "Welcome to Sales Mate!"}

app.include_router(rag_copilot.router, prefix="/rag-copilot")
app.include_router(direct_chat.router, prefix="/direct-chat")
