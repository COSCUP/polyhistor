import gc
import os
import warnings

import httpx
from dotenv import load_dotenv
from fastapi import APIRouter, Form, status
from fastapi.responses import JSONResponse
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Qdrant
from qdrant_client import QdrantClient

from src.chains.answerChain import answerChain
from src.chains.multiqueryChain import multiqueryChain, parse_fusion_results
from src.models import Query
from src.utils.config import get_config
from src.utils.exp import parse_answer

warnings.filterwarnings("ignore")

router = APIRouter()
load_dotenv()

config = get_config(config_path="config.yaml")
embeddings_model = config.model.embeddings_model
model_kwargs = {"device": "cpu"}
encode_kwargs = {"normalize_embeddings": False}
embeddings = HuggingFaceEmbeddings(
    model_name=embeddings_model,
    model_kwargs=model_kwargs,
    encode_kwargs=encode_kwargs,
)
COLLECTION = config.database.collection


@router.get("/")
def healthCHeck():
    return {"Status": "OK"}


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

    if os.getenv("MODE") == "dev":
        host = config.database.external_host
    else:
        host = config.database.internal_host

    vectorstore = Qdrant(
        client=QdrantClient(host),
        collection_name=COLLECTION,
        embeddings=embeddings,
        content_payload_key="content",
    )

    retriever = vectorstore.as_retriever(search_kwargs={"k": 5}, search_type="mmr")
    answerchain = answerChain(model=config.model.llm)
    multiquerychain = multiqueryChain(retriever=retriever, model=config.model.llm)

    fused_results = parse_fusion_results(multiquerychain.invoke({"original_query": data.query}))
    answer = answerchain.invoke({"question": data.query, "context": "\n\n".join(fused_results["content"])})
    answer = parse_answer(answer, fused_results["metadata"])
    del vectorstore
    del retriever

    return answer


@router.post(
    "/api/v1/chatbot",
    tags=["external"],
)
async def chatbot(text: str = Form(...)):
    if os.getenv("MODE") == "dev":
        print("收到問題囉～請稍等一下")
    else:
        await post_to_mattermost("收到問題囉～請稍等一下")

    data = Query(query=text.lower())
    contents = await askAPI(data)

    ans = "Question: " + text + "\n\n" + "Answer: " + "\n" + contents + "\n\n" + "如果有什麼問題可以直接留言給我們，如果覺得答案不符合需求，也歡迎直接在留言處提供文件並標注 @jefflu 或 @jimmy_hong 或 @irischen"

    gc.collect()
    return JSONResponse(content={"response_type": "in_channel", "text": ans})


async def post_to_mattermost(message: str):
    webhook_url = os.getenv("MATTERMOST_WEBHOOK_URL")
    if not webhook_url:
        print("Mattermost webhook URL is not set")
        return

    payload = {"text": message}

    async with httpx.AsyncClient() as client:
        response = await client.post(webhook_url, json=payload)
