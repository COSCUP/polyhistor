import glob
from tqdm import tqdm

from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    UnstructuredFileLoader,
    UnstructuredMarkdownLoader,
    UnstructuredWordDocumentLoader,
)
from langchain_core.documents.base import Document

from qdrant_client import QdrantClient

from utils import compute_file_hash, retrieve_file_record, delete_file_record


class CustomDirectoryLoader:
    def __init__(
        self, directory_path: str, client: QdrantClient, glob_pattern: str = "**"
    ):
        """Initialize the loader with a directory path and a glob pattern.

        Args:
            directory_path (str): Path to the directory containing files to load.
            client (QdrantClient): Qdrant client instance.
            glob_pattern (str, optional): Glob pattern to match files within the directory.
        """
        self.directory_path = directory_path
        self.client = client
        self.glob_pattern = glob_pattern
        self.filetype_mapping = {
            # "md": (UnstructuredMarkdownLoader, {}),
            "md": (TextLoader, {"encoding": "utf8"}),
            "txt": (TextLoader, {"encoding": "utf8"}),
            "docx": (UnstructuredWordDocumentLoader, {}),
            "pdf": (PyPDFLoader, {}),
        }

    def _load_file(self, file_path: str) -> list[Document]:
        """Load a single file using the appropriate loader.

        Args:
            file_path (str): Path to the file to load.

        Returns:
            list[Document]: List of Document objects loaded from the file.
        """
        file_extension = file_path.split(".")[-1]
        loader_cls, loader_kwargs = self.filetype_mapping.get(
            file_extension, (UnstructuredFileLoader, {})
        )
        loader = loader_cls(file_path=file_path, **loader_kwargs)
        try:
            return loader.load()
        except Exception as e:
            print(f"Error loading file {file_path} with {loader_cls}: {e}")

    def _search_and_load(self, file_path: str):
        """Search for file metadata in Qdrant and load the file if necessary.

        Args:
            file_path (str): Path to the file to search and load.

        Returns:
            list[Document]: List of Document objects loaded from the file.
        """
        try:
            records = retrieve_file_record(self.client, file_path)
            current_hash = compute_file_hash(file_path)

            if records:
                # File has already saved in vector db
                old_hash = records[0].payload["metadata"]["hash"]
                if current_hash != old_hash:
                    # File has changed, delete and update the new file
                    delete_file_record(self.client, file_path)
                    docs = self._load_file(file_path)
                else:
                    # File has not been changed
                    return []
            else:
                # The first time processing this file
                docs = self._load_file(file_path)

            # Update the metadata with the current hash
            docs[0].metadata["hash"] = current_hash
            return docs

        except Exception as e:
            print(f"Error search and load file {file_path}: {e}")

    def load(self) -> list[Document]:
        """Load all files matching the glob pattern in the directory. Support md, txt, and docx files.

        Returns:
            list[Document]: List of Document objects loaded from the files.
        """
        documents = []
        full_glob_pattern = f"{self.directory_path}/{self.glob_pattern}"
        for file_path in tqdm(glob.glob(full_glob_pattern)):
            print("Processing file: ", file_path)
            try:
                docs = self._search_and_load(file_path)
                documents.extend(docs)
            except Exception as e:
                print(f"Error loading documents from file {file_path}: {e}")
        return documents
