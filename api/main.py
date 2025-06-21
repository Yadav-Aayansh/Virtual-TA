from typing import List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from core import query_search, generate_response, create_llm_prompt
from fastapi.middleware.cors import CORSMiddleware
from utils import load_index_and_metadata

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Preload indices and metadata at startup
DISCOURSE_INDEX, DISCOURSE_METADATA = load_index_and_metadata("../data/discourse_index.faiss", "../data/discourse_metadata.json")
COURSE_INDEX, COURSE_METADATA = load_index_and_metadata("../data/course_index.faiss", "../data/course_metadata.json")

class QueryRequest(BaseModel):
    question: str
    image: Optional[str] = None

class Link(BaseModel):
    text: str
    url: str

class LLMResponse(BaseModel):
    answer: str
    links: List[Link]


@app.post("/generate-answer", response_model=LLMResponse)
async def generate_answer(request: QueryRequest):
    try:
        query = request.question
        discourse_context, course_context = await query_search(query, COURSE_INDEX, COURSE_METADATA, DISCOURSE_INDEX, DISCOURSE_METADATA)
        prompt = create_llm_prompt(query, discourse_context, course_context, request.image)
        result = await generate_response(prompt)
        return result
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e) or "Unknown server error")


