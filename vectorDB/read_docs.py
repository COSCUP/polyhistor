import os
from dotenv import load_dotenv
from getpass import getpass

from langchain_community.embeddings import OllamaEmbeddings

from qdrant_client import QdrantClient

from classes.vector_db import VectorDB
from classes.text_splitter import TextSplitter
from classes.document_loader import DocumentLoader

load_dotenv()

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

if not ACCESS_TOKEN:
    ACCESS_TOKEN = getpass()


def main():
    db = VectorDB(host="http://localhost:6333")
    COLLECTION_NAME = "datav1"

    embedding = OllamaEmbeddings(model="chevalblanc/acge_text_embedding")

    headers = [("#", "Header 1"), ("##", "Header 2"), ("###", "Header 3")]
    splitterConfig = {
        "name": "MarkdownHeaderTextSplitter",
        "headers_to_split_on": headers,
    }
    splitters = TextSplitter()
    splitter = splitters.create(splitterConfig)

    # local files
    documentLoaderConfig = {
        "name": "CustomDirectoryLoader",
        "directory_path": "../testdata",
        "client": QdrantClient("http://localhost:6333/"),
    }
    # github repository # TODO: detect github file changes
    # documentLoaderConfig = {
    #     "name": "GithubFileLoader",
    #     "repo": "COSCUP/COSCUP-Volunteer",
    #     "access_token": ACCESS_TOKEN,
    #     "github_api_url": "https://api.github.com",
    #     "branch": "main",
    #     "file_extension": ".md",
    # }

    loader = DocumentLoader.create(documentLoaderConfig)
    documents = loader.load()

    datas = []
    for doc in documents:
        split_documents = splitter.split_text(doc.page_content)

        for split_doc in split_documents:
            text = split_doc.page_content
            payload = split_doc.metadata
            payload["content"] = text
            payload["metadata"] = DocumentLoader.get_metadata(
                doc, documentLoaderConfig["name"]
            )
            vector = embedding.embed_query(text=text)
            data = {"vector": vector, "payload": payload}

            datas.append(data)

    db.upsert_data(COLLECTION_NAME, datas)


if __name__ == "__main__":
    main()
