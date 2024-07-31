from classes.custom_loader import CustomDirectoryLoader, CustomGithubFileLoader


class DocumentLoader:
    loaders = {
        "CustomDirectoryLoader": CustomDirectoryLoader,
        "CustomGithubFileLoader": CustomGithubFileLoader,
    }
    metadata = {
        "CustomDirectoryLoader": ["source", "hash"],
        "CustomGithubFileLoader": ["source", "sha"],
    }

    @staticmethod
    def create(config: dict):
        loader_class = DocumentLoader.loaders.get(config["name"])
        if not loader_class:
            raise ValueError(f"Unsupported document loader: {config['name']}")

        if config["name"] == "CustomGithubFileLoader":
            file_extension = config.get("file_extension", "")
            file_filter = lambda file_path: file_path.endswith(file_extension)
            config.pop("file_extension", None)
            config["file_filter"] = file_filter

        return loader_class(**{k: v for k, v in config.items() if k != "name"})

    @staticmethod
    def get_metadata(doc, doc_loader: list):
        fields = DocumentLoader.metadata.get(doc_loader, [])
        metadata = {field: doc.metadata.get(field) for field in fields}
        if "api.github.com" in metadata["source"]:
            metadata["source"] = metadata["source"].replace("api.github.com", "github.com")
        return metadata
