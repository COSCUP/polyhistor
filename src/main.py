from dotenv import load_dotenv
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Qdrant
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from qdrant_client import QdrantClient

from model import llm_model

load_dotenv()


def get_chain(retriever):
    template = """根據下列內容回答問題，請使用繁體中文回答:
    {context}

    問題: {question}
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

    chain = get_chain(retriever)

    input_text = input(">>> ")
    while input_text.lower() != "bye":
        parse_answer(chain.invoke(input_text))
        input_text = input(">>> ")


if __name__ == "__main__":
    main()
