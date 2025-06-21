import json

merged = []

def topics_merger(page=30):
    for i in range(page):
        with open(f"../raw-data/cleaned/{i}.json", "r") as f:
            data = json.load(f)
            merged.extend(data)

    # Wrap into same structure if needed
    output = {
        "topics": merged
    }

    # Save it
    with open("../raw-data/topics.json", "w") as f:
        json.dump(output, f, indent=2)

    print(f"Merged {len(merged)} topics into ../raw-data/topics.json")

if __name__ == "__main__":
    topics_merger()
