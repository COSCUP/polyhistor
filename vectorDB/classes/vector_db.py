import uuid

from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import PointStruct


class VectorDB:
    def __init__(self, embeddingConfig: dict = None, host: str = None):

        if embeddingConfig != None:
            self.embeddingConfig = embeddingConfig
            self.embedding = self._initialize_embedding()

        if host != None:
            self.host = host
            self.client = self._initialize_client()

    def _initialize_client(self):
        """
        初始化vectorDB
        """
        try:
            client = QdrantClient(self.host)
            print(f"connect to {self.host}")
        except ConnectionError as e:
            return f"Connection failed: {e}"
        except Exception as e:
            return f"An unexpected error occurred: {e}"

        return client

    def _initialize_embedding(self):
        """
        初始化embedding model
        """
        return HuggingFaceBgeEmbeddings(
            model_name=self.embeddingConfig["name"],
            model_kwargs=self.embeddingConfig["model_kwargs"],
            encode_kwargs=self.embeddingConfig["encode_kwargs"],
        )

    def embedded_query(self, query: str):
        """
        將 query embedded into vector
        """
        return self.embedding.embed_query(query)

    def upsert_data(self, collection_name: str, datas: list):
        """
        插入向量至DB
        """
        for i, data in enumerate(datas):
            uid = str(uuid.uuid1())
            self.client.upsert(
                collection_name=collection_name,
                points=[PointStruct(id=uid, vector=data["vector"], payload=data["payload"])],
            )

    def create_collection(self, collection_name):
        self.client.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(distance=models.Distance.COSINE, size=1792),
            optimizers_config=models.OptimizersConfigDiff(memmap_threshold=20000),
            hnsw_config=models.HnswConfigDiff(on_disk=True, m=16, ef_construct=100),
        )

    def recreate_collection(self, collection_name):
        self.client.recreate_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(distance=models.Distance.COSINE, size=1792),
            optimizers_config=models.OptimizersConfigDiff(memmap_threshold=20000),
            hnsw_config=models.HnswConfigDiff(on_disk=True, m=16, ef_construct=100),
        )

    def search(self, collection_name, vector, k):
        searchResult = self.client.search(
            collection_name=collection_name,
            query_vector=vector,
            limit=k,
            append_payload=True,
        )
        return searchResult
