from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from nlp_engine import NLPEngine

app = FastAPI(title="Election Campaign Assistant API")

# Mount the static directory for images
app.mount("/static", StaticFiles(directory="static"), name="static")

# Allow CORS for Flutter app (which might run on an emulator or device)
# In production, restrict this to specific origins.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

nlp = NLPEngine()

class ChatRequest(BaseModel):
    user_message: str

class ChatResponse(BaseModel):
    response_text: str
    detected_intent: str
    # data field is optional and can be arbitrary dict or None, 
    # but for simplicity we'll just omit typing strictness here or use dict
    data: dict | None = None

@app.get("/")
def read_root():
    return {"message": "Election Assistant API is running"}

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """
    Endpoint to process user message and return election-related response.
    """
    user_message = request.user_message.strip()
    if not user_message:
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    result = nlp.get_response(user_message)
    
    return ChatResponse(
        response_text=result["response_text"],
        detected_intent=result["intent"],
        data=result.get("data")
    )

@app.get("/suggestions")
def suggestions(q: str = ""):
    """
    Endpoint to get auto-suggestions based on partial text.
    """
    if not q:
        return {"suggestions": []}
    
    results = nlp.get_suggestions(q)
    return {"suggestions": results}

if __name__ == "__main__":
    import uvicorn
    # Host 0.0.0.0 is important for Android emulator to access via 10.0.2.2 or local IP
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
