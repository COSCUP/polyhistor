from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders.github import GithubFileLoader
from langchain_community.document_loaders import DirectoryLoader

from getpass import getpass

ACCESS_TOKEN = getpass()

# 1
text_loader = TextLoader("path/to/test.txt")
documents = text_loader.load()

# 2
github_loader = GithubFileLoader(
    repo="COSCUP/COSCUP-Volunteer",
    access_token=ACCESS_TOKEN,
    github_api_url="https://api.github.com",
    branch="main",
    file_filter=lambda file_path: file_path.endswith(".md"),
)
documents = github_loader.load()

# 3
dir_loader = DirectoryLoader(
    path="path/to//test_dir/", 
    glob="**/*.txt"
)
documents = dir_loader.load()
