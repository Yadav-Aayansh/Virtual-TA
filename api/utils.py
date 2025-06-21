import faiss
import json

def load_index_and_metadata(index_path: str, metadata_path: str):
    index = faiss.read_index(index_path)
    with open(metadata_path, 'r', encoding='utf-8') as f:
        metadata = json.load(f)
    return index, metadata