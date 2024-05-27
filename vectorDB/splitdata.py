import os

from classes.documentLoader import DocumentLoader
from classes.textSplitter import TextSplitter
from classes.vectorDB import VectorDB
from langchain_community.embeddings import OllamaEmbeddings


def read_document(
    splitters: TextSplitter,
    documentLoaders: DocumentLoader,
    splitterConfig: dict,
    documentLoaderConfig: dict,
):
    splitter = splitters.create(splitterConfig)
    documentLoader = documentLoaders.create(documentLoaderConfig)
    documents = documentLoader.load()

    for document in documents:
        split_documents = splitter.split_text(document.page_content)

    return split_documents


def main():
    # 設定TextSplitter參數
    headers = [("#", "Header 1"), ("##", "Header 2"), ("###", "Header 3")]
    splitterConfig = {
        "name": "MarkdownHeaderTextSplitter",
        "headers_to_split_on": headers,
    }

    db = VectorDB(host="http://localhost:6333")
    embedding = OllamaEmbeddings(model="chevalblanc/acge_text_embedding")
    splitters = TextSplitter()
    documentLoaders = DocumentLoader()
    COLLECTION_NAME = "datav1"
    collection_flag = True
    recreation_Flag = True
    # 是否重建collection
    if recreation_Flag:
        print(f"Create collection-{COLLECTION_NAME}")
        db.recreate_collection(COLLECTION_NAME)
    else:
        # 確認collection是否存在
        collections = db.client.get_collections().collections
        for collection in collections:
            if collection.name == COLLECTION_NAME:
                collection_flag = False
                collection_info = db.client.get_collection(collection.name)
                print(f"collection-{collection.name} 存在")
                print(f"---collection info---\n{collection_info}")
        if collection_flag == True:
            print(f"Create collection-{COLLECTION_NAME}")
            db.create_collection(COLLECTION_NAME)

    root_path = "./vectorDB/testdata"
    datas = []
    for root, dirs, files in os.walk(root_path):
        for file in files:
            name, extension = os.path.splitext(file)
            if extension != ".md":
                continue
            file_path = os.path.join(root, file)
            documentLoaderConfig = {
                "name": "TextLoader",
                "file_path": file_path,
            }
            documents = read_document(splitters, documentLoaders, splitterConfig, documentLoaderConfig)
            for doc in documents:
                text = doc.page_content
                payload = doc.metadata
                payload["content"] = text
                payload["metadata"] = {"source": file}
                vector = embedding.embed_query(text=text)
                data = {"vector": vector, "payload": payload}
                datas.append(data)

    db.upsert_data(COLLECTION_NAME, datas)


if __name__ == "__main__":
    main()
