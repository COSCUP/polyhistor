from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Qdrant
from qdrant_client import QdrantClient

from src.chains.answerChain import answerChain
from src.chains.multiqueryChain import multiqueryChain, parse_fusion_results
from src.models import Query
from src.utils.exp import parse_answer
from src.utils.config import get_config

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

    config = get_config(config_path="config.yaml")
    embeddings_model = config.model.embeddings_model
    embeddings = OllamaEmbeddings(model=embeddings_model)
    COLLECTION = config.database.collection
    host = config.database.host

    vectorstore = Qdrant(
        client=QdrantClient(host),
        collection_name=COLLECTION,
        embeddings=embeddings,
        content_payload_key="content",
    )

    retriever = vectorstore.as_retriever(search_kwargs={"k": 5}, search_type="mmr")
    answerchain = answerChain()
    multiquerychain = multiqueryChain(retriever)

    fused_results = parse_fusion_results(multiquerychain.invoke({"original_query": data.query}))
    answer = answerchain.invoke({"question": data.query, "context": "\n\n".join(fused_results["content"])})
    answer = parse_answer(answer, fused_results["metadata"])
    print(answer)

    return answer
