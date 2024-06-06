import hashlib
import re

from qdrant_client import QdrantClient
from qdrant_client.http import models


def compute_file_hash(file_path: str):
    """Compute the SHA-256 hash of the given file.

    Args:
        file_path (str): Path to the file to hash.

    Returns:
        str: The computed hash value of the file.
    """
    hash_algo = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            while chunk := f.read(8192):
                hash_algo.update(chunk)
    except IOError as e:
        print(f"Error reading file {file_path}: {e}")
    return hash_algo.hexdigest()


def retrieve_file_record(client: QdrantClient, file_path: str):
    """Retrieve the record for a file from Qdrant.

    Args:
        client (QdrantClient): Qdrant client instance.
        file_path (str): Path to the file to retrieve metadata for.

    Returns:
        list: Record of the file including its metadata.
    """
    try:
        result, _ = client.scroll(
            collection_name="test",
            scroll_filter=models.Filter(
                should=[
                    models.FieldCondition(key="metadata.source", match=models.MatchValue(value=file_path)),
                ],
            ),
        )
    except Exception as e:
        print(f"Error retrieving file record for {file_path} in Qdrant: {e}")
    return result


def delete_file_record(client: QdrantClient, file_path: str):
    """Delete the record for a file from Qdrant.

    Args:
        client (QdrantClient): Qdrant client instance.
        file_path (str): Path to the file to delete metadata for.

    Returns:
        None
    """
    try:
        client.delete(
            collection_name="test",
            points_selector=models.FilterSelector(
                filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="metadata.source",
                            match=models.MatchValue(value=file_path),
                        ),
                    ],
                )
            ),
        )
    except Exception as e:
        print(f"Error deleting file record for {file_path} in Qdrant: {e}")


def filter_data(text: str, file_type: str) -> str:
    """filter data based on file type

    Args:
        text (str): file content
        file_type (str): file type

    Returns:
        str: filtered text
    """

    if file_type == "md":
        pattern = r"!\[.*?\]\(.*?\)|\[[^\]]*?\]\(.*?\)"
        text = re.sub(pattern, "", text)
        text = f"The following content is markdown:\n\n{text} \n\n"
    elif file_type == "pdf":
        text = text.replace("\n", "")

    return text
