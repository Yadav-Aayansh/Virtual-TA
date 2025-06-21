import numpy as np
from typing import List, Dict

def get_topic_replies(topic_id: str, metadata: List[Dict], matched_post_number: int, max_replies: int = 17) -> List[Dict]:
    topic_chunks = [item for item in metadata if item['metadata']['topic_id'] == topic_id]
    topic_chunks = sorted(topic_chunks, key=lambda x: x['metadata'].get('post_number', 0))
    
    question_chunks = [chunk for chunk in topic_chunks if chunk['metadata']['type'] == 'question']
    
    if len(topic_chunks) <= max_replies + len(question_chunks):
        return question_chunks + [chunk for chunk in topic_chunks if chunk['metadata']['type'] != 'question']
    
    reply_chunks = [chunk for chunk in topic_chunks if chunk['metadata']['type'] != 'question']
    for i, chunk in enumerate(reply_chunks):
        if chunk['metadata'].get('post_number', 0) >= matched_post_number:
            return question_chunks + reply_chunks[i:i + max_replies]
    
    return question_chunks + reply_chunks[:max_replies]


def discourse_query_search(embedding, index, metadata, k: int = 3, max_replies: int = 17) -> List[Dict]:
    embedding = np.array(embedding, dtype=np.float32)
    if embedding.ndim == 1:
        embedding = embedding.reshape(1, -1)

    distances, indices = index.search(embedding, k)

    results = []
    seen_topics = set()
    
    for idx, distance in zip(indices[0], distances[0]):
        matched_chunk = metadata[idx].copy()
        matched_chunk['similarity'] = float(1 / (1 + distance))
        
        topic_id = matched_chunk['metadata']['topic_id']
        if topic_id in seen_topics:
            continue
        
        topic_results = get_topic_replies(topic_id, metadata, matched_chunk['metadata'].get('post_number', 0), max_replies)
        for result in topic_results:
            result['similarity'] = matched_chunk['similarity']
        results.extend(topic_results)
        seen_topics.add(topic_id)
    
    results = sorted(results, key=lambda x: x.get('similarity', 0), reverse=True)
    return results[:k * (max_replies + 1)]