from langchain_community.document_loaders import TextLoader, UnstructuredMarkdownLoader


class DocumentLoader:
    def __init__(self):
        """
        暫時留空 \n
        用做整理documentloader的interface
        """

    def create(self, config: dict):
        """
        透過create創建愈使用的DocumentLoader
        已加入:[UnstructuredMarkdownLoader]
        ------------------------------------\n
        class UnstructuredMarkdownLoader(
            file_path: str | List[str] | Path | List[Path] | None,
            mode: str = "single",
            **unstructured_kwargs: Any
        )\n

        Initialize with file path.
        """
        if config["name"] == "UnstructuredMarkdownLoader":
            return UnstructuredMarkdownLoader(config["file_path"], config["mode"])
        if config["name"] == "TextLoader":
            return TextLoader(config["file_path"])
