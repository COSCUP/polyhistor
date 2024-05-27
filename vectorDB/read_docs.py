from langchain_community.embeddings import OllamaEmbeddings

from qdrant_client import QdrantClient

from classes.vectorDB import VectorDB
from classes.textSplitter import TextSplitter
from classes.documentLoader import DocumentLoader


def read_document(
    documentLoaders: DocumentLoader,
    documentLoaderConfig: dict,
):
    documentLoader = documentLoaders.create(documentLoaderConfig)
    documents = documentLoader.load()

    return documents


def main():
    db = VectorDB(host="http://localhost:6333")
    COLLECTION_NAME = "test"
    
    embedding = OllamaEmbeddings(model="chevalblanc/acge_text_embedding")

    headers = [("#", "Header 1"), ("##", "Header 2"), ("###", "Header 3")]
    splitterConfig = {
        "name": "MarkdownHeaderTextSplitter",
        "headers_to_split_on": headers,
    }
    splitters = TextSplitter()
    
    documentLoaders = DocumentLoader()
    documentLoaderConfig = {
        "name": "CustomDirectoryLoader",
        "dir_path": "../testdata",
        "client": QdrantClient("http://localhost:6333/"),
    }

    # documentLoaderConfig = {
    #     "name": "GithubFileLoader",
    #     "repo_url": "kt-cheng/shap-e-docker",
    #     # "repo_url": "COSCUP/COSCUP-Volunteer",
    #     "branch": "main",
    #     "file_extension": ".md",
    # }

    splitter = splitters.create(splitterConfig)
    documents = read_document(documentLoaders, documentLoaderConfig)

    datas = []
    for doc in documents:
        split_documents = splitter.split_text(doc.page_content)

        for split_doc in split_documents:
            text = split_doc.page_content
            payload = split_doc.metadata
            payload["content"] = text

            payload["metadata"] = {
                "source": doc.metadata["source"],
                "hash": doc.metadata["hash"],
            }
            # payload["metadata"] = {
            #     "source": doc.metadata["source"],
            #     "sha": doc.metadata["sha"],
            # }
            vector = embedding.embed_query(text=text)
            data = {"vector": vector, "payload": payload}

            datas.append(data)

    db.upsert_data(COLLECTION_NAME, datas)


if __name__ == "__main__":
    main()
