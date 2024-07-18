import gc
import os
import re
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

    retriever = vectorstore.as_retriever(search_kwargs={"k": 3, "score_threshold": 0.6}, search_type="mmr")
    answerchain = answerChain(model=config.model.llm)
    multiquerychain = multiqueryChain(retriever=retriever, model=config.model.llm)

    fused_results = parse_fusion_results(multiquerychain.invoke({"original_query": data.query}))
    answer = answerchain.invoke({"question": data.query, "context": "\n\n".join(fused_results["content"])})
    answer = parse_answer(answer, fused_results["metadata"])
    del vectorstore
    del retriever

    return {"result": answer}


@router.post(
    "/api/v1/chatbot",
    tags=["external"],
)
async def chatbot(user_name: str = Form(...), text: str = Form(...), response_url: str = Form(...)):
    if os.getenv("MODE") == "dev":
        print("收到問題囉～請稍等一下")
    else:
        await send_wait_response(response_url)

    data = Query(query=text.lower())
    contents = await askAPI(data)
    gc.collect()

    match = re.search(r"(.*)Source: \n(.*)", contents, re.DOTALL)

    if match:
        llm_answer = match.group(1).strip()
        source = match.group(2).strip()
    else:
        llm_answer = contents
        source = "No source available"

    return JSONResponse(
        content={
            "response_type": "in_channel",
            "text": f"Hi @{user_name}",
            "attachments": [
                {
                    "fields": [
                        {"short": False, "title": "Question", "value": text},
                        {"short": False, "title": "Answer", "value": llm_answer},
                        {"short": False, "title": "Source", "value": source},
                        {"short": False, "title": " ", "value": "如果有什麼問題可以直接留言給我們，如果覺得答案不符合需求，也歡迎直接在留言處提供文件並標注 @jefflu 或 @jimmy_hong 或 @irischen"},
                    ]
                }
            ],
        }
    )


async def send_wait_response(response_url: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            response_url,
            json={
                "response_type": "in_channel",
                "text": "收到問題囉～請稍等一下",
            },
        )
