from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Qdrant
from qdrant_client import QdrantClient

from src.chains.answerChain import answerChain
from src.models import Query
from src.utils.exp import parse_answer

router = APIRouter()


@router.get("/health")
def healthCHeck():
    return {"Status": "OK"}


@router.post(
    "/api/v1/ask",
    tags=["external"],
)
async def askAPI(data: Query):
    if data.query is None or data.query == "":
        print(data)
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"message": "empty query is not allowed"},
        )

    embeddings_model = "chevalblanc/acge_text_embedding"
    embeddings = OllamaEmbeddings(model=embeddings_model)
    print("Embeddings loaded")
    COLLECTION = "datav1"
    host = "http://localhost:6333"

    vectorstore = Qdrant(
        client=QdrantClient(host),
        collection_name=COLLECTION,
        embeddings=embeddings,
        content_payload_key="content",
    )

    retriever = vectorstore.as_retriever(search_kwargs={"k": 5}, search_type="mmr")
    chain = answerChain(retriever)

    answer = parse_answer(chain.invoke(data.query))
    print(answer)
    return answer
