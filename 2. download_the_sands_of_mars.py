import requests

url = "https://tululu.org/txt.php"
payload = {"id": 32168}

response = requests.get(url, params=payload)
response.raise_for_status()

with open('The_Sands_of_Mars.txt', 'w') as file:
    file.write(response.text)
