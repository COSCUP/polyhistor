from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveJsonSplitter


class TextSplitter:
    def __init__(self):
        """
        暫時留空 \n
        用做整理textsplitter的interface
        """

    def create(self, config: dict):
        """
        透過create創建愈使用的textSplitter
        已加入:[MarkdownHeaderTextSplitter]
        ------------------------------------\n
        MarkdownHeaderTextSplitter()\n
        \"\"\"

        Create a new MarkdownHeaderTextSplitter.\n
        Args:\n
            headers_to_split_on: Headers we want to track\n
            return_each_line: Return each line w/ associated headers\n
            strip_headers: Strip split headers from the content of the chunk\n

        \"\"\"
        """
        if config["name"] == "MarkdownHeaderTextSplitter":
            return MarkdownHeaderTextSplitter(config["headers_to_split_on"], strip_headers=False)
        if config["name"] == "RecursiveJsonSplitter":
            return RecursiveJsonSplitter()
