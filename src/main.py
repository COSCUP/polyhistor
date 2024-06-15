import os

import requests
from dotenv import load_dotenv

load_dotenv()


def main():
    url = os.environ.get("BACKEND_URL")

    input_text = input(">>> ")
    while input_text.lower() != "bye":
        data = {"query": input_text.lower()}
        response = requests.post(url=url, json=data, headers={"Content-Type": "application/json"})
        contents = response.text.split("\\n")
        for content in contents:
            print(content)
        input_text = input(">>> ")


if __name__ == "__main__":
    main()
