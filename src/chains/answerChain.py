from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from src.utils.model import llm_model


def answerChain(model):
    template = """你是一位COSCUP的工作人員，請利用下面的資訊，資訊來源為文件與頻道對話。使用繁體中文回答問題，並且回答的內容要完整且有邏輯。
    #####
    問題: {question}
    #####
    {context}

    #####
    """
    prompt = ChatPromptTemplate.from_template(template)
    model = llm_model(model)
    chain = prompt | model | StrOutputParser()

    return chain
