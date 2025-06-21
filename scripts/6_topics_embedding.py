from bs4 import BeautifulSoup
import json
import re
from sentence_transformers import SentenceTransformer
from typing import List, Dict
import numpy as np
import faiss

def clean_text(text: str) -> str:
    """Clean HTML, mentions, and emojis from text."""
    # Remove HTML tags
    soup = BeautifulSoup(text, "html.parser")
    cleaned = soup.get_text()
    # Remove mentions (e.g., @username)
    cleaned = re.sub(r'@\w+', '', cleaned)
    # Remove emojis (basic regex, can be extended)
    cleaned = re.sub(r'[\U0001F600-\U0001F6FF]', '', cleaned)
    return cleaned.strip()

def chunk_text(text: str, max_tokens: int = 512, overlap: int = 50) -> List[str]:
    """Split text into chunks with overlap."""
    words = text.split()
    chunks = []
    for i in range(0, len(words), max_tokens - overlap):
        chunk = " ".join(words[i:i + max_tokens])
        chunks.append(chunk)
    return chunks

def preprocess_discourse_data(json_path: str) -> List[Dict]:
    """Preprocess JSON data and extract text for embedding."""
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    processed_data = []
    base_url = "https://discourse.onlinedegree.iitm.ac.in/t/"

    for topic in data['topics']:
        topic_id = topic['id']
        topic_slug = topic['slug']
        topic_url = f"{base_url}{topic_slug}/{topic_id}"

        # Process question
        question_text = clean_text(topic['question'])
        question_chunks = chunk_text(question_text)
        for i, chunk in enumerate(question_chunks):
            processed_data.append({
                'text': chunk,
                'metadata': {
                    'topic_id': topic_id,
                    'type': 'question',
                    'chunk_id': i,
                    'url': topic_url
                }
            })

        # Process replies
        for reply in topic.get('replies', []):
            reply_text = clean_text(reply['cooked'])
            reply_chunks = chunk_text(reply_text)
            for i, chunk in enumerate(reply_chunks):
                processed_data.append({
                    'text': chunk,
                    'metadata': {
                        'topic_id': topic_id,
                        'type': 'reply',
                        'post_number': reply['post_number'],
                        'chunk_id': i,
                        'url': f"{topic_url}/{reply['post_number']}"
                    }
                })

        # Process accepted answer
        if topic.get('accepted_answer'):
            answer_text = clean_text(topic['accepted_answer'])
            answer_chunks = chunk_text(answer_text)
            for i, chunk in enumerate(answer_chunks):
                processed_data.append({
                    'text': chunk,
                    'metadata': {
                        'topic_id': topic_id,
                        'type': 'accepted_answer',
                        'chunk_id': i,
                        'url': topic_url
                    }
                })

    return processed_data

def embed_texts(texts: List[str], model_name: str = "intfloat/multilingual-e5-large-instruct") -> np.ndarray:
    """Generate embeddings using the specified model."""
    model = SentenceTransformer(model_name)
    embeddings = model.encode(texts, normalize_embeddings=True, show_progress_bar=True)
    return embeddings

def store_embeddings(processed_data: List[Dict], index_path: str = "../data/discourse_index.faiss", metadata_path: str = "../data/discourse_metadata.json"):
    """Store embeddings in a Faiss index and save metadata."""
    embeddings = np.array([item['embedding'] for item in processed_data], dtype=np.float32)
    metadata = [{k: v for k, v in item.items() if k != 'embedding'} for item in processed_data]

    # Create Faiss index
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)

    # Save index and metadata
    faiss.write_index(index, index_path)
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    json_path = "../raw-data/discussion.json"
    processed_data = preprocess_discourse_data(json_path)
    texts = [item['text'] for item in processed_data]
    embeddings = embed_texts(texts)
    for i, item in enumerate(processed_data):
        item['embedding'] = embeddings[i].tolist()

    # Save processed data with embeddings
    with open("../extra/processed_discussion.json", 'w', encoding='utf-8') as f:
        json.dump(processed_data, f, ensure_ascii=False, indent=2)
    
    store_embeddings(processed_data)
    