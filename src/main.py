import os

import requests
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough

from utils.model import llm_model

load_dotenv()


def get_chain(retriever):
    template = """你是一位COSCUP的工作人員，請利用下面的資訊，使用繁體中文回答問題，並且回答的內容要完整且有邏輯。
    #####
    問題: {question}
    #####
    {context}

    #####
    """
    prompt = ChatPromptTemplate.from_template(template)

    # model = ChatOllama(model="qwen:4b", temperature=0)
    model = llm_model("ycchen/breeze-7b-instruct-v1_0")

    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    rag_chain_from_docs = RunnablePassthrough.assign(context=(lambda x: format_docs(x["context"]))) | prompt | model | StrOutputParser()

    chain = RunnableParallel({"context": retriever, "question": RunnablePassthrough()}).assign(answer=rag_chain_from_docs)
    return chain


def parse_answer(answer):
    print(answer["answer"])
    print("Source: ")
    for doc in answer["context"]:
        print(doc.metadata["source"])


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
