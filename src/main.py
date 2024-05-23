from dotenv import load_dotenv
from langchain.retrievers import EnsembleRetriever
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.chat_models import ChatOllama
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.retrievers import BM25Retriever
from langchain_community.vectorstores import Qdrant
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough

from utils import load_docs

load_dotenv()


def get_chain(retriever):
    template = """根據下列內容回答問題，請使用繁體中文回答:
    {context}

    問題: {question}
    """
    prompt = ChatPromptTemplate.from_template(template)

    model = ChatOllama(model="qwen:4b", temperature=0)

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

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50, add_start_index=True)

    docs = load_docs(folder_path="../testdata")
    print("Docs loaded")
    all_splits = text_splitter.split_documents(docs)

    vectorstore = Qdrant.from_documents(all_splits, embeddings, path="./local_qdrant", collection_name="RAG")
    print("Vectorstore loaded")

    bm25_retriever = BM25Retriever.from_documents(all_splits)
    bm25_retriever.k = 2
    retriever = vectorstore.as_retriever(search_kwargs={"k": 5}, search_type="mmr")

    ensemble_retriever = EnsembleRetriever(retrievers=[bm25_retriever, retriever], weights=[0.5, 0.5])

    chain = get_chain(ensemble_retriever)

    input_text = input(">>> ")
    while input_text.lower() != "bye":
        parse_answer(chain.invoke(input_text))
        input_text = input(">>> ")


if __name__ == "__main__":
    main()
