import requests
import json
import uuid
import time

DISCOURSE_API_URL = "https://discourse.onlinedegree.iitm.ac.in/t/"

COOKIE = "_forum_session=xktb2XEPZWIHJt4PpTz1gpEaZ6BRZcj%2FDuCgHMVTF0R71BQHAdvbDMdZDwVOtRixI4Bfn9fP7DYmk9ujkcL7tta4DkDO5ot%2B9wgg8YumTjxQnsHS4xeP668Niw4%2Fpb5fzzve7zxqV23colMfXsRslnbRACCmcN83nidJH7k4fD%2BoZtebJEWagR5VNRwiU4LIWhmmJpgvP3hgsUlMBvaisKLo32bXlIo48RD1XRSPFY23RlmXzKJBHy%2BUWRJZTDpfuge4OFu8Zhlkdkzi4tSEyFJT4x32Xe6lT%2BXSYY91H%2B1%2FXfaIOIRK7oaN%2FEr3g%2BN7sCd0QpbRomV%2FhLuYqfaROqSQ2aNxOn1u8W%2FJjWo00yaY1OP4hDQ6G%2FkB8JdpqMHJIbDMiteWld0jDgb4XBRMb6U%2FvBoNavHjVKv3QAtmDXCspyvxiTHxxpST0OmEX%2BEVPOcCsu17G%2FIc9No43kR9oC%2BxJdLEAbvYPS1LKSnAIdFboxCAk2Gz%2BH%2B7VzjoY9s%2FhmpBpRdGP0Z0bn1%2B6UPpyKuQWsxGmJsC3x6drIf9BFBFV%2B71jApRSHSly%2FWOJw%3D%3D--6hb8Ul88tupxKyWf--%2FPZnQW1%2BHSkudQOdEffeDA%3D%3D; _t=QODRSXCaFELJ3x4CYA2YhQgx%2BZWQN0hevsdpRlolFdnpwzLgJ92yIgWNuIJ7kXR2piH2vB7D4QxTpzUL72XqKZQvv2DQaMuByhNgwbXFQPA1ozlW8NbzxTtETnVsLv1RUipi%2F9nTlSeirxc08rEjY196GJt4%2FiMvZPge0s6bzOycdPe1g5ijoFnyUMzSlhTfkb15yWb1cu%2FTUYrgGJY1%2BhW3ZRE1WIjgG%2BxIb5oeTpMG5MxHzV1kwicQv1kN3yvqncy3fqf68xU814QeQkXez2gdeWjaecAmcV%2B4Nxqyzs9cBXn0QS%2BTxsBkz3GSAydd7YmuPw%3D%3D--ta%2FyxyTHYOYCrTw9--IqVd7OM%2Fg0ESI5QTEpPbLw%3D%3D"

def fetch_topic_data(topic_id, cookie):
    base_url = f"{DISCOURSE_API_URL}{topic_id}"
    headers = {"Cookie": cookie}
    try:
        url = f"{base_url}.json"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        topic_json = response.json()
        fetched_posts = topic_json.get("post_stream", {}).get("posts", [])
        fetched_post_ids = {post["id"] for post in fetched_posts}
        all_post_ids = topic_json.get("post_stream", {}).get("stream", [])
        missing_post_ids = [pid for pid in all_post_ids if pid not in fetched_post_ids]
        while missing_post_ids:
            batch = missing_post_ids[:20]
            missing_post_ids = missing_post_ids[20:]
            post_ids_param = "&".join([f"post_ids%5B%5D={pid}" for pid in batch])
            posts_url = f"{base_url}/posts.json?{post_ids_param}"
            posts_resp = requests.get(posts_url, headers=headers)
            posts_resp.raise_for_status()
            posts_json = posts_resp.json()
            topic_json["post_stream"]["posts"].extend(posts_json.get("post_stream", {}).get("posts", []))
        return topic_json
    except requests.RequestException as e:
        print(f"Error fetching topic {topic_id}: {e}")
        return None

def parse_topic_data(data, topic_info):
    question = None
    accepted_answer = None
    answers = []
    topic_info = topic_info.copy()
    posts = data.get("post_stream", {}).get("posts", [])
    for post in posts:
        if post.get("post_number") == 1:
            question = post.get("cooked")
            break
    for post in posts:
        if post.get("post_number") > 1:
            answers.append({
                "post_number": post.get("post_number"),
                "cooked": post.get("cooked")
            })
        if post.get("accepted_answer") == True:
            accepted_answer = post.get("cooked")
    if question:
        topic_info["question"] = question
        topic_info["accepted_answer"] = accepted_answer
        topic_info["replies"] = answers if answers else []
    return topic_info

def update_json_file(topic_info, filename="../raw-data/discussion.json"):
    try:
        with open(filename, 'r') as f:
            existing_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        existing_data = {"topics": []}
    if topic_info.get("question"):
        existing_data["topics"].append(topic_info)
    with open(filename, 'w') as f:
        json.dump(existing_data, f, indent=2)
    print(f"Updated {filename} with topic {topic_info['id']}")

def topics_answer(input_file):
    try:
        with open(input_file, 'r') as f:
            data = json.load(f)
        topics = data.get("topics", [])
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error reading input JSON file: {e}")
        return
    for topic in topics:
        topic_id = topic.get("id")
        topic_data = fetch_topic_data(topic_id, COOKIE)
        if not topic_data:
            print(f"No data for topic {topic_id}")
            continue
        topic_info = parse_topic_data(topic_data, topic)
        if topic_info.get("question"):
            update_json_file(topic_info)
        else:
            print(f"Missing question for topic {topic_id}")

if __name__ == "__main__":
    topics_answer("../raw-data/topics.json")
