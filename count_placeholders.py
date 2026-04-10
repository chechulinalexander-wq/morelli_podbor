import sqlite3
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

conn = sqlite3.connect('handles_server.db')
cursor = conn.cursor()

# Get handles with empty embeddings
cursor.execute("""
    SELECT product_id, name, url
    FROM handles
    WHERE url IS NOT NULL AND url != ''
    AND (image_embedding IS NULL OR image_embedding = '')
    LIMIT 10
""")

handles = cursor.fetchall()
print(f"Checking {len(handles)} handles with empty embeddings...\n")

placeholders = 0
real_images = 0
errors = 0

for product_id, name, url in handles:
    try:
        print(f"[{product_id}] {name[:50]}...")
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, timeout=10, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        img_tag = soup.find('img', class_='show_phone_img_zoom')

        if img_tag and img_tag.get('src'):
            img_src = img_tag['src']
            if 'default_img_mor' in img_src:
                print(f"  [X] PLACEHOLDER: {img_src}\n")
                placeholders += 1
            else:
                print(f"  [OK] REAL IMAGE: {img_src}\n")
                real_images += 1
        else:
            print(f"  [!] NO IMAGE TAG\n")
            errors += 1
    except Exception as e:
        print(f"  [!] ERROR: {e}\n")
        errors += 1

conn.close()

print(f"\n{'='*60}")
print(f"RESULTS (sample of 10):")
print(f"{'='*60}")
print(f"Placeholders: {placeholders}")
print(f"Real images: {real_images}")
print(f"Errors/No tag: {errors}")
