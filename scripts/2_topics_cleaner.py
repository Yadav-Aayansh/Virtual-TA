import os
import json
from datetime import datetime

os.makedirs("../raw-data/cleaned", exist_ok=True)

def topics_cleaner(page=30):
    for i in range(page):
        with open(f"../raw-data/fetched/{i}.json", "r") as f:
            data = json.load(f)

        # Filter dates
        start_date = datetime(2024, 9, 1)
        end_date = datetime(2025, 4, 14)

        filtered_topics = []

        for topic in data["topic_list"]["topics"]:
            created_at = datetime.fromisoformat(topic["created_at"].replace("Z", ""))
            if start_date <= created_at <= end_date:
                filtered_topics.append({
                    "id": topic["id"],
                    "title": topic["title"],
                    "slug": topic["slug"],
                    "tags": topic["tags"]
                })

        # Output to file
        with open(f"../raw-data/cleaned/{i}.json", "w") as f:
            json.dump(filtered_topics, f, indent=2)

        print(f"[{i+1}/{page}] Cleaned and saved: raw-data/cleaned/{i}.json")


if __name__ == "__main__":
    topics_cleaner()