import csv

from ollama import chat
from ollama import ChatResponse

from pathlib import Path

from constants import SYSTEM_PROMPT
from models import Addicted


_SRC_DIR = Path(__file__).parent.parent

def run_program(
    output_file: Path = _SRC_DIR / "relevant_posts.csv"
) -> dict:
    
    reddit_posts = collect_reddit_posts()

    relevant_posts: list[str] = []

    for idx, rp in enumerate(reddit_posts):
        if is_addicted(reddit_post=rp):
            entry = {
                "id": idx,
                "reddit_post_text": rp
            }

            print("Relevant Post:", str(entry))

            relevant_posts.append(entry)

            if len(relevant_posts) >= 50:
                print("Reached 50 relevant posts, stopping.")
                break

    with open(output_file, "w") as f:
        fieldnames = ["id", "reddit_post_text"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(relevant_posts)

    return {
        "status": "ok"
    }
                


def is_addicted(
    reddit_post: str
) -> bool:

    response: ChatResponse = chat(
        model='gemma4:e2b', 
        messages=[
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        },
        {
            'role': 'user',
            'content': reddit_post,
        },
    ],
    format=Addicted.model_json_schema(),
    )

    val = Addicted.model_validate_json(response.message.content).is_addicted
    print(val)

    if val:
        return True
    else:
        return False


def collect_reddit_posts(
    csv_path: Path = _SRC_DIR / "reddit_posts.csv"
) -> list[str]:
    
    reddit_posts: list[str] = []
    
    with open(csv_path, "r") as f:
        reader = csv.DictReader(f=f)
        for row in reader:
            reddit_posts.append(row["selftext"])

    return reddit_posts


run_program()