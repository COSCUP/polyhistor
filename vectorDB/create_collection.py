import os
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(project_root)

from classes.vector_db import VectorDB

from src.utils.config import get_config


def main():
    config = get_config(config_path=f"{project_root}/config.yaml")
    db = VectorDB(host=config.database.external_host)
    COLLECTION_NAME = config.database.collection

    collection_flag = True
    recreation_Flag = True

    # 是否重建collection
    if recreation_Flag:
        print(f"Create collection-{COLLECTION_NAME}")
        db.recreate_collection(COLLECTION_NAME)
    else:
        # 確認collection是否存在
        collections = db.client.get_collections().collections
        for collection in collections:
            if collection.name == COLLECTION_NAME:
                collection_flag = False
                collection_info = db.client.get_collection(collection.name)
                print(f"collection-{collection.name} 存在")
                print(f"---collection info---\n{collection_info}")
        if collection_flag == True:
            print(f"Create collection-{COLLECTION_NAME}")
            db.create_collection(
                COLLECTION_NAME,
            )


if __name__ == "__main__":
    main()
