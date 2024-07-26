def parse_answer(answer: str, metadata: list[str]) -> str:
    content = f"{answer}\n Source: \n"

    for source in metadata[:3]:
        content += f"- {source}\n"
    return content
