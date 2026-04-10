import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def extract_image_from_page(page_url):
    """Extract image URL from product page HTML"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        print(f"Fetching page: {page_url}")
        response = requests.get(page_url, timeout=30, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Look for img tag with class="show_phone_img_zoom" (main product image)
        img_tag = soup.find('img', class_='show_phone_img_zoom')

        if img_tag:
            img_src = img_tag.get('src')
            print(f"Found img tag with src: {img_src}")

            # Skip default placeholder images
            if img_src and 'default_img_mor' in img_src:
                print(f"SKIP: Default placeholder image")
                return None

            if img_src:
                # Convert relative URL to absolute
                img_url = urljoin(page_url, img_src)
                print(f"Final image URL: {img_url}")
                return img_url
        else:
            print("NO img tag with class='show_phone_img_zoom' found")

            # Let's see what images ARE on the page
            all_imgs = soup.find_all('img')
            print(f"\nFound {len(all_imgs)} total images on page:")
            for i, img in enumerate(all_imgs[:5]):  # Show first 5
                print(f"  {i+1}. class={img.get('class')}, src={img.get('src')[:80] if img.get('src') else 'None'}")

        return None

    except Exception as e:
        print(f"ERROR: {e}")
        return None

# Test with SIENA-2 URL
url = "https://morelli.ru/catalog/ruchki/all/2699"
result = extract_image_from_page(url)
print(f"\nResult: {result}")
