import glob
from typing import Iterator

from langchain_community.document_loaders import PyPDFLoader, TextLoader, UnstructuredFileLoader, UnstructuredWordDocumentLoader
from langchain_community.document_loaders.github import GithubFileLoader
from langchain_core.documents.base import Document
from qdrant_client import QdrantClient
from tqdm import tqdm

from utils import compute_file_hash, delete_file_record, retrieve_file_record


class CustomDirectoryLoader:
    def __init__(self, directory_path: str, client: QdrantClient, glob_pattern: str = "**"):
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
        loader_cls, loader_kwargs = self.filetype_mapping.get(file_extension, (UnstructuredFileLoader, {}))
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


class CustomGithubFileLoader(GithubFileLoader):
    client: QdrantClient

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, repo, access_token, github_api_url, branch, client: QdrantClient, file_filter=None):
        """Initialize the loader with a GitHub repository and an access token.

        Args:
            repo (str): GitHub repository name.
            access_token (str): GitHub access token.
            github_api_url (str): GitHub API URL.
            branch (str): GitHub branch to load files from.
            file_filter (callable, optional): Function to filter files to load. Defaults to None.
        """

        super().__init__(repo=repo, access_token=access_token, github_api_url=github_api_url, branch=branch, file_filter=file_filter, client=client)
        self.client = client

    def _load_file(self, file_path: str) -> list[Document]:
        """Load a single file using the GitHub file loader.

        Args:
            file_path (str): Path to the file to load.

        Returns:
            list[Document]: List of Document objects loaded from the file.
        """
        try:
            documents = super()._load_file(file_path)
            return documents
        except Exception as e:
            print(f"Error loading file {file_path} from GitHub: {e}")
            return []

    def _search_and_load(self, file):
        """Search for file metadata in Qdrant and load the file if necessary.

        Args:
            file_path (str): Path to the file to search and load.
            client (QdrantClient): Qdrant client instance.

        Returns:
            list[Document]: List of Document objects loaded from the file.
        """
        sha = file["sha"]

        if "api.github.com" in self.github_api_url:
            github_url = self.github_api_url.replace("api.github.com", "github.com")
        else:
            github_url = self.github_api_url
        source = f"{github_url}/{self.repo}/{file['type']}/{self.branch}/{file['path']}"
        records = retrieve_file_record(self.client, source)
        if records:
            # File has already saved in vector db
            old_sha = records[0].payload["metadata"]["sha"]
        else:
            old_sha = None
        if sha != old_sha:
            # File has changed, delete and update the new file
            delete_file_record(self.client, source)
            content = self.get_file_content_by_path(file["path"])
            if content == "":
                return []
            metadata = {
                "path": file["path"],
                "sha": sha,
                "source": f"{self.github_api_url}/{self.repo}/{file['type']}/" f"{self.branch}/{file['path']}",
            }
            return [Document(page_content=content, metadata=metadata)]
        else:
            # File has not been changed
            print(f"File {source} has not been changed")
        return []

    def lazy_load(self) -> Iterator[Document]:
        files = self.get_file_paths()
        for file in files:
            print("Processing file: ", file["path"])
            file_path = file["path"]
            try:
                docs = self._search_and_load(file)
                if docs:
                    yield from docs
            except Exception as e:
                print(f"Error loading file {file_path}: {e}")
