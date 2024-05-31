from classes.vector_db import VectorDB


def main():
    db = VectorDB(host="http://localhost:6333")
    COLLECTION_NAME = "test"

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
            db.create_collection(COLLECTION_NAME)


if __name__ == "__main__":
    main()
