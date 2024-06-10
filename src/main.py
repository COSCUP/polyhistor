import os

import requests
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from utils.model import llm_model

load_dotenv()


def reciprocal_rank_fusion(results: list[list], k=60):
    fused_scores = {}
    for docs in results:
        for rank, doc in enumerate(docs):
            doc_str = dumps(doc)
            if doc_str not in fused_scores:
                fused_scores[doc_str] = 0
            fused_scores[doc_str] += 1 / (rank + k)

    reranked_results = [(loads(doc), score) for doc, score in sorted(fused_scores.items(), key=lambda x: x[1], reverse=True)]
    return reranked_results


def rag_fusion(query, retriever):

    template = """
        You are a helpful assistant that generates multiple search queries based on a single input query.
        Generate multiple search queries related to: {original_query}
        OUTPUT (4 queries):
    """
    prompt = ChatPromptTemplate.from_template(template)
    model = llm_model("ycchen/breeze-7b-instruct-v1_0")

    generate_queries = prompt | model | StrOutputParser() | (lambda x: x.split("\n"))
    chain = generate_queries | retriever.map() | reciprocal_rank_fusion
    return chain.invoke({"original_query": query})


def parse_fusion_results(results):
    content = []
    metadata = set()
    for res in results:
        content.append(res[0].page_content)
        metadata.add(res[0].metadata["source"])
    return {"content": content, "metadata": list(metadata)}


def get_chain():
    template = """你是一位COSCUP的工作人員，請利用下面的資訊，使用繁體中文回答問題，並且回答的內容要完整且有邏輯。
    #####
    問題: {question}
    #####
    {context}

    #####
    """
    prompt = ChatPromptTemplate.from_template(template)
    model = llm_model("ycchen/breeze-7b-instruct-v1_0")
    chain = prompt | model | StrOutputParser()

    return chain


def parse_answer(answer, metadata):
    print(answer)
    print("Source: ")
    for source in metadata:
        print(source)


def main():
    url = os.environ.get("BACKEND_URL")

    input_text = input(">>> ")
    while input_text.lower() != "bye":
        data = {"query": input_text.lower()}
        response = requests.post(url=url, json=data, headers={"Content-Type": "application/json"})
        contents = response.text.split("\\n")
        for content in contents:
            print(content)
        input_text = input(">>> ")


if __name__ == "__main__":
    main()
