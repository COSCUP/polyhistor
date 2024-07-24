import os
import sys

import requests

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(project_root)

from classes.vector_db import VectorDB
from dotenv import load_dotenv

from src.utils.config import get_config

load_dotenv()

MATTERMOST_TOKEN = os.getenv("MATTERMOST_TOKEN")

api_url = "https://chat.coscup.org/api/v4"
target_user_ids = ("8774n1zebtds9rc5fkm56ywmmo", "rqoq5f36tp8xdrjog6gewp7k3e", "cgbaxag3upypzdccoz3pec4q9r")
test_channel_id = "jp71k3ztbbbqdqfrunaeqd1aph"  # COSCUP 2024


class Post:
    def __init__(self, user_id: str, message: str, create_at: int, username: str, post_id: str) -> None:
        self.user_id = user_id
        self.message = message
        self.create_at = create_at
        self.username = username
        self.post_id = post_id

    def __repr__(self) -> str:
        return f"Post(user_id='{self.user_id}', message='\n{self.message}\n', create_at={self.create_at})"


class UserCache:
    def __init__(self) -> None:
        self.cache = {}

    def get_username(self, user_id: str) -> str:
        if user_id in self.cache:
            return self.cache[user_id]
        else:
            username = self.fetch_username(user_id)
            self.cache[user_id] = username
            return username

    def fetch_username(self, user_id: str) -> str:
        url = f"{api_url}/users/{user_id}"
        headers = {"Authorization": f"Bearer {MATTERMOST_TOKEN}"}

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            res = response.json()
            return res["username"]
        else:
            print(f"Failed to get username for user_id {user_id}. Status code: {response.status_code}, Error: {response.text}")
            return user_id


def get_posts(user_cache: UserCache) -> list[Post]:
    url = f"{api_url}/channels/{test_channel_id}/posts"
    headers = {"Authorization": f"Bearer {MATTERMOST_TOKEN}"}

    response = requests.get(url, headers=headers)
    context_size = 3

    if response.status_code == 200:
        res = response.json()
        post_ids = res["order"]
        posts = res["posts"]

        result: list[Post] = []
        for i, post_id in enumerate(post_ids):
            post = posts[post_id]
            if post["user_id"] in target_user_ids:
                username = user_cache.get_username(post["user_id"])
                context_ids = post_ids[max(0, i - context_size) : i + context_size + 1]
                combined_message = "\n".join([f"{user_cache.get_username(posts[_post_id]['user_id'])}: {posts[_post_id]['message']}" for _post_id in context_ids[::-1]])
                result.append(Post(post["user_id"], combined_message, post["create_at"], username, post_id))

        return result
    else:
        print(f"Failed to get posts. Status code: {response.status_code}, Error: {response.text}")
        return []


def upload_to_qdrant(posts: list[Post], config) -> None:
    embeddingConfig = {"model_name": config.model.embeddings_model, "model_kwargs": {"device": "cpu"}, "encode_kwargs": {"normalize_embeddings": False}}
    db = VectorDB(embeddingConfig=embeddingConfig, host=config.database.external_host)
    COLLECTION_NAME = config.database.collection

    vectors = []
    for post in posts:
        vector = db.embedded_query(post.message)
        payload = {
            "content": post.message,
            "metadata": {
                "user_id": post.user_id,
                "source": post.username,
            },
            "create_at": post.create_at,
            "post_id": post.post_id,
        }
        data = {"vector": vector, "payload": payload}
        vectors.append(data)

    db.upsert_data(collection_name=COLLECTION_NAME, datas=vectors)


def main():
    user_cache = UserCache()
    posts = get_posts(user_cache)
    config = get_config(config_path=f"{project_root}/config.yaml")

    upload_to_qdrant(posts, config)


if __name__ == "__main__":
    main()
