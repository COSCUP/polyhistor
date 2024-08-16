from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from src.utils.model import llm_model


def answerChain(model):
    template = """你是一位COSCUP的工作人員，請利用下面的資訊回答問題，回答時需遵守以下幾點：
    1. 回答需確保資訊正確、完整
    2. 使用繁體中文回答
    3. 回答需清晰、易懂
    4. 回答需盡量簡潔
    5. 回答需盡量符合問題
    6. 回答需使用台灣用語

    $$$$$$
    問題: {original_query}
    $$$$$$
    {context}

    $$$$$$
    回答:
    """
    prompt = ChatPromptTemplate.from_template(template)
    model = llm_model(model)
    chain = prompt | model | StrOutputParser()

    return chain
