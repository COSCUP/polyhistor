from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough

from src.utils.model import llm_model


def answerChain(retriever):
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
