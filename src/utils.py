from langchain_core.documents.base import Document

from loader import CustomDirectoryLoader


def load_docs(folder_path: str = "../testdata") -> list[Document]:
    """This function load md files under folder_path.

    Args:
        folder_path (str, optional): _description_. Defaults to "../testdata".

    Returns:
        list[Document]
    """
    directory_loader = CustomDirectoryLoader(directory_path=folder_path)
    docs = directory_loader.load()
    print(f"Loaded {len(docs)} documents")
    return docs
