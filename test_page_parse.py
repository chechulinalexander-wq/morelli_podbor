import requests
from bs4 import BeautifulSoup

url = "https://morelli.ru/catalog/ruchki/all/2462"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

response = requests.get(url, timeout=30, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')

# Find all img tags
print("All img tags:")
for img in soup.find_all('img')[:10]:  # First 10 images
    print(f"\nTag: {img.name}")
    print(f"Class: {img.get('class')}")
    print(f"Src: {img.get('src')}")
    print(f"Data-src: {img.get('data-src')}")
    print("-" * 50)
