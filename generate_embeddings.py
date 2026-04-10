import sqlite3
import os
import requests
from PIL import Image
from io import BytesIO
import torch
from transformers import CLIPProcessor, CLIPModel
import time
import numpy as np

# Initialize CLIP model for image embeddings
print("Loading CLIP model...")
model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
device = "cuda" if torch.cuda.is_available() else "cpu"
model = model.to(device)
print(f"Model loaded on {device}\n")

# Create directory for images
os.makedirs('data/handles_images', exist_ok=True)

def download_and_convert_image(url, product_id):
    """Download image and convert to JPG format"""
    try:
        print(f"Downloading image for product {product_id}...")
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        # Open image and convert to RGB
        img = Image.open(BytesIO(response.content))

        # Convert to RGB (removes alpha channel if present)
        if img.mode != 'RGB':
            img = img.convert('RGB')

        # Save as JPG
        local_path = f'data/handles_images/{product_id}.jpg'
        img.save(local_path, 'JPEG', quality=95)
        print(f"[OK] Saved: {local_path}")

        return local_path, img
    except Exception as e:
        print(f"[ERROR] Error downloading {url}: {e}")
        return None, None

def get_image_embedding(image):
    """Get embedding from CLIP model"""
    try:
        print(f"Generating embedding...")

        # Process image
        inputs = processor(images=image, return_tensors="pt").to(device)

        # Get image features
        with torch.no_grad():
            image_features = model.get_image_features(**inputs)

        # Normalize embedding
        embedding = image_features / image_features.norm(dim=-1, keepdim=True)
        embedding = embedding.cpu().numpy().flatten().tolist()

        print(f"[OK] Embedding generated: {len(embedding)} dimensions")

        return embedding
    except Exception as e:
        print(f"[ERROR] Error generating embedding: {e}")
        return None

def process_handles():
    """Process all handles images and generate embeddings"""
    conn = sqlite3.connect('handles.db')
    cursor = conn.cursor()

    # Get all handles with image paths
    cursor.execute('SELECT product_id, image_path FROM handles WHERE image_path IS NOT NULL')
    handles = cursor.fetchall()

    print(f"\nFound {len(handles)} handles with images\n")

    processed = 0
    failed = 0

    for product_id, image_url in handles:
        print(f"\n--- Processing product {product_id} ({processed + 1}/{len(handles)}) ---")

        # Download and convert image
        local_path, img = download_and_convert_image(image_url, product_id)

        if local_path and img is not None:
            # Generate embedding
            embedding = get_image_embedding(img)

            if embedding:
                # Convert embedding to JSON string for storage
                import json
                embedding_json = json.dumps(embedding)

                # Update database
                cursor.execute(
                    'UPDATE handles SET image_embedding = ? WHERE product_id = ?',
                    (embedding_json, product_id)
                )
                conn.commit()

                print(f"[OK] Saved embedding to database for product {product_id}")
                processed += 1
            else:
                failed += 1
        else:
            failed += 1

        # Small delay between requests
        time.sleep(0.2)

    conn.close()

    print(f"\n\n=== SUMMARY ===")
    print(f"Total: {len(handles)}")
    print(f"Processed: {processed}")
    print(f"Failed: {failed}")

if __name__ == "__main__":
    print("Starting image embedding generation...")
    process_handles()
