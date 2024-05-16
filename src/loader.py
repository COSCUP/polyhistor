import glob

from langchain_community.document_loaders import PyPDFLoader, TextLoader, UnstructuredFileLoader, UnstructuredMarkdownLoader, UnstructuredWordDocumentLoader
from langchain_core.documents.base import Document
from tqdm import tqdm


class CustomDirectoryLoader:
    def __init__(self, directory_path: str, glob_pattern: str = "**", mode: str = "single"):
        """Initialize the loader with a directory path and a glob pattern

        Args:
            directory_path (str): Path to the directory containing files to load.
            glob_pattern (str, optional): Glob pattern to match files within the directory.
            mode (str, optional): Mode to use with Loader. Defaults to "single".
        """
        self.directory_path = directory_path
        self.glob_pattern = glob_pattern
        self.mode = mode
        self.filetype_mapping = {
            "md": (UnstructuredMarkdownLoader, {}),
            "txt": (TextLoader, {"encoding": "utf8"}),
            "docx": (UnstructuredWordDocumentLoader, {}),
            "pdf": (PyPDFLoader, {}),
        }

    def load(self) -> list[Document]:
        """Load all files matching the glob pattern in the directory. Support md, txt, and docx files.

        Returns:
            list[Document]: List of Document objects loaded from the files.
        """
        documents = []
        # Construct the full glob pattern
        full_glob_pattern = f"{self.directory_path}/{self.glob_pattern}"
        for file_path in tqdm(glob.glob(full_glob_pattern)):
            file_extension = file_path.split(".")[-1]
            loader_cls, loader_kwargs = self.filetype_mapping.get(file_extension, (UnstructuredFileLoader, {}))
            if file_extension != "pdf":
                loader_kwargs["mode"] = self.mode
                loader_kwargs["use_multithreading"] = True

            loader = loader_cls(file_path=file_path, **loader_kwargs)
            docs = loader.load()
            documents.extend(docs)

        return documents
