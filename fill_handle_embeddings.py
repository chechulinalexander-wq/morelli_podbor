import sqlite3
import os
import requests
from PIL import Image
from io import BytesIO
import time
import json
import base64
from openai import OpenAI
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from urllib.parse import urljoin

load_dotenv()

# Initialize OpenAI for GPT-4 Vision
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
print("OpenAI client initialized\n")

# Create directory for images
os.makedirs('data/handles_images', exist_ok=True)

def extract_image_from_page(page_url):
    """Extract image URL from product page HTML"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(page_url, timeout=30, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Look for img tag with class="show_phone_img_zoom" (main product image)
        img_tag = soup.find('img', class_='show_phone_img_zoom')
        if img_tag and img_tag.get('src'):
            img_src = img_tag['src']

            # Skip default placeholder images
            if 'default_img_mor' in img_src:
                print(f"  [SKIP] Default placeholder image, no real photo")
                return None

            # Convert relative URL to absolute
            img_url = urljoin(page_url, img_src)
            print(f"  Found image: {img_url}")
            return img_url

        print(f"  [WARN] No product image found")
        return None

    except Exception as e:
        print(f"  [ERROR] Failed to parse page: {e}")
        return None

def download_and_convert_image(page_url, product_id):
    """Download image from product page and convert to JPG format"""
    try:
        print(f"  Processing page for {product_id}...")
        print(f"  Page URL: {page_url[:80]}...")

        # Extract image URL from page
        img_url = extract_image_from_page(page_url)
        if not img_url:
            return None

        # Download image
        print(f"  Downloading image...")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(img_url, timeout=30, headers=headers)
        response.raise_for_status()

        # Open image and convert to RGB
        img = Image.open(BytesIO(response.content))

        # Verify it's actually an image
        img.verify()

        # Re-open after verify (verify closes the file)
        img = Image.open(BytesIO(response.content))

        # Convert to RGB (removes alpha channel if present)
        if img.mode != 'RGB':
            img = img.convert('RGB')

        # Save as JPG
        local_path = f'data/handles_images/{product_id}.jpg'
        img.save(local_path, 'JPEG', quality=95)
        print(f"  [OK] Saved: {local_path}")

        return local_path
    except Exception as e:
        print(f"  [ERROR] Download failed: {e}")
        print(f"  [ERROR] Page URL: {page_url}")
        return None

def analyze_handle_with_gpt4(image_path, product_id, name, description):
    """Analyze handle image with GPT-4 Vision to extract characteristics"""
    try:
        print(f"  Analyzing with GPT-4 Vision...")

        # Read and encode image
        with open(image_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')

        vision_prompt = f"""Проанализируй эту дверную ручку и определи следующие характеристики:

Название: {name}
Описание: {description}

1. finish_color - цвет/отделка (например: black, chrome, satin_chrome, gold, bronze, white, graphite, copper, brushed_steel и т.д.)
2. style - стиль (modern_minimal, classic, contemporary, rustic, traditional, art_deco и т.д.)
3. color_group - цветовая группа (light, dark, warm, metallic)
4. series - серия/коллекция (извлеки из названия или описания, например: LUXURY, GRAND CARAT, MH и т.д.)

Верни ТОЛЬКО JSON объект в следующем формате:
{{
  "finish_color": "black",
  "style": "modern_minimal",
  "color_group": "dark",
  "series": "LUXURY"
}}"""

        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": vision_prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=200
        )

        analysis_text = response.choices[0].message.content.strip()

        # Parse JSON response
        if analysis_text.startswith("```json"):
            analysis_text = analysis_text.split("```json")[1].split("```")[0].strip()
        elif analysis_text.startswith("```"):
            analysis_text = analysis_text.split("```")[1].split("```")[0].strip()

        analysis = json.loads(analysis_text)
        print(f"  [OK] Analysis: {json.dumps(analysis, ensure_ascii=False)}")

        # Generate text embedding for the handle description
        print(f"  Generating text embedding...")
        embedding_text = f"{name} {description or ''} {analysis.get('finish_color', '')} {analysis.get('style', '')} {analysis.get('color_group', '')}"

        embedding_response = openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=embedding_text
        )

        embedding = embedding_response.data[0].embedding
        analysis['embedding'] = embedding
        print(f"  [OK] Embedding generated: {len(embedding)} dimensions")

        return analysis

    except Exception as e:
        print(f"  [ERROR] GPT-4 analysis failed: {e}")
        return None

def process_handles():
    """Process all handles: download images and analyze with GPT-4"""
    conn = sqlite3.connect('handles_server.db')
    cursor = conn.cursor()

    # Get only handles that need processing (missing any field)
    cursor.execute('''
        SELECT product_id, url, name, description, image_path, finish_color, style, color_group, series, image_embedding
        FROM handles
        WHERE url IS NOT NULL AND url != ''
        AND (
            image_path IS NULL OR image_path = ''
            OR finish_color IS NULL OR finish_color = ''
            OR style IS NULL OR style = ''
            OR color_group IS NULL OR color_group = ''
            OR series IS NULL OR series = ''
            OR image_embedding IS NULL OR image_embedding = ''
        )
    ''')
    handles = cursor.fetchall()

    print(f"\nFound {len(handles)} handles to process\n")

    processed = 0
    failed = 0
    skipped = 0

    for product_id, image_url, name, description, existing_image_path, existing_finish_color, existing_style, existing_color_group, existing_series, existing_embedding in handles:
        print(f"\n{'='*60}")
        print(f"[{processed + failed + skipped + 1}/{len(handles)}] Processing: {name}")
        print(f"Product ID: {product_id}")
        print(f"{'='*60}")

        # Check what needs to be done
        needs_image = not existing_image_path
        needs_analysis = not existing_finish_color or not existing_style or not existing_color_group or not existing_series or not existing_embedding

        # Download image only if needed
        if needs_image:
            local_path = download_and_convert_image(image_url, product_id)
            if not local_path:
                failed += 1
                continue
        else:
            local_path = existing_image_path
            print(f"  [SKIP] Image already exists: {local_path}")

        # Analyze with GPT-4 Vision only if needed
        if needs_analysis:
            analysis = analyze_handle_with_gpt4(local_path, product_id, name, description or "")
            if not analysis:
                analysis = {}
        else:
            print(f"  [SKIP] All fields already filled")
            skipped += 1
            continue

        # Update database with only missing fields
        try:
            update_fields = []
            update_values = []

            if needs_image:
                update_fields.append("image_path = ?")
                update_values.append(local_path)

            if not existing_finish_color and analysis.get('finish_color'):
                update_fields.append("finish_color = ?")
                update_values.append(analysis.get('finish_color'))

            if not existing_style and analysis.get('style'):
                update_fields.append("style = ?")
                update_values.append(analysis.get('style'))

            if not existing_color_group and analysis.get('color_group'):
                update_fields.append("color_group = ?")
                update_values.append(analysis.get('color_group'))

            if not existing_series and analysis.get('series'):
                update_fields.append("series = ?")
                update_values.append(analysis.get('series'))

            if not existing_embedding and analysis.get('embedding'):
                update_fields.append("image_embedding = ?")
                update_values.append(json.dumps(analysis.get('embedding')))

            if update_fields:
                update_values.append(product_id)
                query = f"UPDATE handles SET {', '.join(update_fields)} WHERE product_id = ?"
                cursor.execute(query, update_values)
                conn.commit()
                print(f"  [OK] Database updated: {', '.join([f.split(' = ')[0] for f in update_fields])}")
                processed += 1
            else:
                print(f"  [SKIP] No new data to update")
                skipped += 1

        except Exception as e:
            print(f"  [ERROR] Database update failed: {e}")
            failed += 1

        # Delay between requests (only if we made API call)
        if needs_analysis:
            time.sleep(1)

    conn.close()

    print(f"\n\n{'='*60}")
    print(f"SUMMARY")
    print(f"{'='*60}")
    print(f"Total: {len(handles)}")
    print(f"Processed: {processed}")
    print(f"Skipped: {skipped}")
    print(f"Failed: {failed}")

if __name__ == "__main__":
    print("Starting handle analysis with GPT-4 Vision...")
    process_handles()
