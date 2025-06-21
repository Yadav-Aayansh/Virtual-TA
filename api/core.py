import os, re, json, base64, io, asyncio, time, requests
from PIL import Image, UnidentifiedImageError
import numpy as np
import pytesseract
import httpx
from dotenv import load_dotenv
from discourse import discourse_query_search
from course import course_query_search
from typing import Optional

load_dotenv()

AIPROXY_API_KEY = os.getenv("AIPROXY_API_KEY")
TOGETHER_AI_API_KEY = os.getenv("TOGETHER_AI_API_KEY")

# reuse clients globally
_LLM_CLIENT = httpx.AsyncClient(http2=True, timeout=30.0)

async def get_together_embedding(text: str) -> np.ndarray:
    start = time.perf_counter()
    resp = await _LLM_CLIENT.post(
        "https://api.together.xyz/v1/embeddings",
        headers={"Authorization": f"Bearer {TOGETHER_AI_API_KEY}", "Content-Type": "application/json"},
        json={"model": "intfloat/multilingual-e5-large-instruct", "input": text}
    )
    resp.raise_for_status()
    emb = np.array(resp.json()["data"][0]["embedding"], dtype=np.float32)
    elapsed = (time.perf_counter() - start)*1000
    return emb

async def query_search(query: str, COURSE_INDEX, COURSE_METADATA, DISCOURSE_INDEX, DISCOURSE_METADATA):
    emb = await get_together_embedding(query)
    # parallel CPU-bound searches
    start = time.perf_counter()
    d_task = asyncio.to_thread(discourse_query_search, emb, DISCOURSE_INDEX, DISCOURSE_METADATA)
    c_task = asyncio.to_thread(course_query_search,   emb, COURSE_INDEX,   COURSE_METADATA)
    d_res, c_res = await asyncio.gather(d_task, c_task)
    elapsed = (time.perf_counter() - start)*1000
    disc_ctx = "\n\n".join(f"{r['text']}\nURL: {r['metadata']['url']}" for r in d_res)
    course_ctx = "\n\n".join(f"{r['text']}\nURL: {r['metadata']['url']}" for r in c_res)
    return disc_ctx, course_ctx


def extract_text_from_base64(img_b64: str) -> str | None:
    try:
        if "," in img_b64:
            base64_data = img_b64.split(",", 1)[1]
        else:
            base64_data = img_b64

        data = base64.b64decode(base64_data)
        img = Image.open(io.BytesIO(data))
        return pytesseract.image_to_string(img)
    except (base64.binascii.Error, UnidentifiedImageError, OSError, ValueError) as e:
        return ""


async def create_llm_prompt(query: str, topic_context: str, course_context: str, base64_image: Optional[str] = None) -> str:
    image_section = ""
    if base64_image:
        base64_image_text = await asyncio.to_thread(extract_text_from_base64, base64_image)
        if base64_image_text.strip():
            image_section = f"\n\nThe student also provided an image with the following text:\n{base64_image_text}"
        elif base64_image_text == "":
            image_section = ""
        else:
            image_section = "\n\nThe student provided an image, but no text could be extracted."

    prompt = f"""
You are a Virtual Teaching Assistant for Tools in Data Science course. A student asked:

"{query}"{image_section}

Use **ONLY** the provided context — Forum Posts, Course Material, and any extracted image text to answer the question clearly, briefly cite excerpts with URLs.
If you cannot answer the question based on the context or are uncertain, respond with a clear refusal and set `"sources": []`.

Respond **ONLY** in this JSON format:

```json
{{
  "answer": "<a comprehensive yet concise answer, or a clear refusal>",
  "links": [
    {{
      "url": "<exact_url_1>",
      "text": "<brief quote or description>"
    }},
    {{
      "url": "<exact_url_2>",
      "text": "<brief quote or description>"
    }}
    // …add more entries if you used more sources
  ]
}}
```

Requirements:
Don’t invent or infer—stick strictly to what’s in the context.
Copy URLs exactly as they appear in the context.

———————————————
Forum Posts:
{topic_context}

Course Material:
{course_context}

"""
    return prompt


async def generate_response(prompt):
    # Send request
    system_prompt = "You are a Virtual TA of Tools in Data Science (TDS) course. Answer based ONLY on the provided context. Do not search anything else!"
    response = await _LLM_CLIENT.post(
        "https://aiproxy.sanand.workers.dev/openai/v1/chat/completions",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {AIPROXY_API_KEY}"
        },
        json={
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
        }
    )

    raw = response.json()['choices'][0]['message']['content']
    clean = re.sub(r"^```json|```$", "", raw.strip(), flags=re.MULTILINE).strip()
    return json.loads(clean)
