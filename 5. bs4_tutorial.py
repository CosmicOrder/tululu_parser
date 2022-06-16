import requests
from bs4 import BeautifulSoup

url = "https://www.franksonnenbergonline.com/blog/are-you-grateful/"

resp = requests.get(url)
article = resp.text

soup = BeautifulSoup(article, 'lxml')

title = soup.find('h1', class_='entry-title').text
post_image = soup.find('img', class_='attachment-post-image')['src']
post_text = soup.find('div', class_='entry-content').text

print(title)
print(post_image, post_text, sep='\n\n')
