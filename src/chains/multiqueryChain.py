from langchain.load import dumps, loads
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from src.utils.model import llm_model


def reciprocal_rank_fusion(results: list[list], k=60):
    fused_scores = {}
    for docs in results:
        for rank, doc in enumerate(docs):
            doc_str = dumps(doc)
            if doc_str not in fused_scores:
                fused_scores[doc_str] = 0
            fused_scores[doc_str]
            fused_scores[doc_str] += 1 / (rank + k)

    reranked_results = [(loads(doc), score) for doc, score in sorted(fused_scores.items(), key=lambda x: x[1], reverse=True)]
    return reranked_results


def multiqueryChain(retriever, model):

    template = """
        You are a helpful assistant that generates multiple search queries based on a single input query.
        Generate multiple search queries related to: {original_query}
        OUTPUT (4 queries):
    """
    prompt = ChatPromptTemplate.from_template(template)
    model = llm_model(model)

    generate_queries = prompt | model | StrOutputParser() | (lambda x: x.split("\n"))
    chain = generate_queries | retriever.map() | reciprocal_rank_fusion
    return chain


def parse_fusion_results(results):
    content = []
    metadata = set()
    for res in results:
        content.append(res[0].page_content)
        metadata.add(res[0].metadata["source"])
    return {"content": content, "metadata": list(metadata)}
