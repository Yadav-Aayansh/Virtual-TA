from bs4 import BeautifulSoup
import json
import re
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Dict
import faiss

def clean_text(text: str) -> str:
    soup = BeautifulSoup(text, "html.parser")
    cleaned = soup.get_text()
    cleaned = re.sub(r'@\w+', '', cleaned)
    cleaned = re.sub(r'[\U0001F600-\U0001F6FF]', '', cleaned)
    return cleaned.strip()

def chunk_text(text: str, max_tokens: int = 512, overlap: int = 50) -> List[str]:
    words = text.split()
    chunks = []
    for i in range(0, len(words), max_tokens - overlap):
        chunk = " ".join(words[i:i + max_tokens])
        chunks.append(chunk)
    return chunks

def preprocess_course_data(json_path: str) -> List[Dict]:
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    processed_data = []

    for section in data["course"]:
        section_title = section.get("title", "")
        section_url = section.get("url", "")
        section_text = clean_text(section.get("content", ""))

        for i, chunk in enumerate(chunk_text(section_text)):
            processed_data.append({
                "text": chunk,
                "metadata": {
                    "source_type": "course_cleaned",
                    "section_title": section_title,
                    "subsection_title": None,
                    "chunk_id": i,
                    "url": section_url
                }
            })

        for subsection in section.get("subsections", []):
            sub_title = subsection.get("title", "")
            sub_url = subsection.get("url", "")
            sub_text = clean_text(subsection.get("content", ""))

            for i, chunk in enumerate(chunk_text(sub_text)):
                processed_data.append({
                    "text": chunk,
                    "metadata": {
                        "source_type": "course_cleaned",
                        "section_title": section_title,
                        "subsection_title": sub_title,
                        "chunk_id": i,
                        "url": sub_url
                    }
                })

    return processed_data

def embed_texts(texts: List[str], model_name: str = "intfloat/multilingual-e5-large-instruct") -> np.ndarray:
    model = SentenceTransformer(model_name)
    embeddings = model.encode(texts, normalize_embeddings=True, show_progress_bar=True)
    return embeddings


def store_embeddings(processed_data: List[Dict], index_path: str = "../data/course_index.faiss", metadata_path: str = "../data/course_metadata.json"):
    embeddings = np.array([item["embedding"] for item in processed_data], dtype=np.float32)
    metadata = [{k: v for k, v in item.items() if k != "embedding"} for item in processed_data]

    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)

    faiss.write_index(index, index_path)
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    json_path = "../raw-data/course.json"
    processed_data = preprocess_course_data(json_path)
    texts = [item["text"] for item in processed_data]
    embeddings = embed_texts(texts)
    for i, item in enumerate(processed_data):
        item["embedding"] = embeddings[i].tolist()

    with open("../extra/processed_course.json", "w", encoding="utf-8") as f:
        json.dump(processed_data, f, ensure_ascii=False, indent=2)

    store_embeddings(processed_data)
    
