from langchain_community.document_loaders.github import GithubFileLoader

from classes.custom_loader import CustomDirectoryLoader
from getpass import getpass

ACCESS_TOKEN = getpass()


class DocumentLoader:
    def __init__(self):
        pass

    def create(self, config: dict):
        if config["name"] == "CustomDirectoryLoader":
            return CustomDirectoryLoader(
                directory_path=config["dir_path"], client=config["client"]
            )
        if config["name"] == "GithubFileLoader":
            return GithubFileLoader(
                repo=config["repo_url"],
                access_token=ACCESS_TOKEN,
                github_api_url="https://api.github.com",
                branch=config["branch"],
                file_filter=lambda file_path: file_path.endswith(
                    config["file_extension"]
                ),
            )

    def get_metadata(self, doc, fields: list):
        metadata = {}
        for field in fields:
            if field in doc.metadata:
                metadata[field] = doc.metadata[field]
        return metadata
