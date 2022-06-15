import os.path
from pathlib import Path

import requests

url = "https://tululu.org/txt.php"
Path("books").mkdir(exist_ok=True)

for i in range(1, 10):
    payload = {"id": i}

    response = requests.get(url, params=payload)
    response.raise_for_status()

    with open(os.path.join("books", f"id{i}.txt"), "w") as file:
        file.write(response.text)
