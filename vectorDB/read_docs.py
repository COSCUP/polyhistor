import os
import sys
from argparse import ArgumentParser, Namespace
from getpass import getpass

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(project_root)

from classes.document_loader import DocumentLoader
from classes.text_splitter import TextSplitter
from classes.vector_db import VectorDB
from dotenv import load_dotenv
from langchain_community.embeddings import HuggingFaceEmbeddings
from qdrant_client import QdrantClient

from src.utils.config import get_config

load_dotenv()

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

if not ACCESS_TOKEN:
    ACCESS_TOKEN = getpass()


def get_doc_config(source: str, host: str | None = None):
    print(f"source: {source}")
    if source == "local":
        assert host is not None
        documentLoaderConfig = {
            "name": "CustomDirectoryLoader",
            "directory_path": f"{project_root}/testdata",
            "client": QdrantClient(host),
        }
    else:
        documentLoaderConfig = {
            "name": "GithubFileLoader",
            "repo": "COSCUP/COSCUP-Volunteer",
            "access_token": ACCESS_TOKEN,
            "github_api_url": "https://api.github.com",
            "branch": "main",
            "file_extension": ".md",
        }
    return documentLoaderConfig


def main(args):
    config = get_config(config_path=f"{project_root}/config.yaml")
    db = VectorDB(host=config.database.external_host)
    COLLECTION_NAME = config.database.collection

    embeddings_model = config.model.embeddings_model
    model_kwargs = {"device": "cpu"}
    encode_kwargs = {"normalize_embeddings": False}
    embedding = HuggingFaceEmbeddings(
        model_name=embeddings_model,
        model_kwargs=model_kwargs,
        encode_kwargs=encode_kwargs,
    )

    headers = [("#", "Header 1"), ("##", "Header 2"), ("###", "Header 3")]
    splitterConfig = {
        "name": "MarkdownHeaderTextSplitter",
        "headers_to_split_on": headers,
    }
    splitters = TextSplitter()
    splitter = splitters.create(splitterConfig)

    documentLoaderConfig = get_doc_config(args.source, config.database.external_host)

    loader = DocumentLoader.create(documentLoaderConfig)
    documents = loader.load()

    datas = []
    for doc in documents:
        split_documents = splitter.split_text(doc.page_content)

        for split_doc in split_documents:
            text = split_doc.page_content
            payload = split_doc.metadata
            payload["content"] = text
            payload["metadata"] = DocumentLoader.get_metadata(doc, documentLoaderConfig["name"])
            vector = embedding.embed_query(text=text)

            data = {"vector": vector, "payload": payload}

            datas.append(data)

    db.upsert_data(COLLECTION_NAME, datas)


def parse_args() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument("--source", type=str, help="local, github", default="local")

    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = parse_args()
    main(args)
