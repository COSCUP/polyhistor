from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from src.utils.model import llm_model


<<<<<<< HEAD
def answerChain(retriever, model):
=======
def answerChain():
>>>>>>> main
    template = """你是一位COSCUP的工作人員，請利用下面的資訊，使用繁體中文回答問題，並且回答的內容要完整且有邏輯。
    #####
    問題: {question}
    #####
    {context}

    #####
    """
    prompt = ChatPromptTemplate.from_template(template)
<<<<<<< HEAD

    model = llm_model(model)
=======
    model = llm_model("ycchen/breeze-7b-instruct-v1_0")
    chain = prompt | model | StrOutputParser()
>>>>>>> main

    return chain
