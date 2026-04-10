import os
from PIL import Image
import json
import numpy as np
from dotenv import load_dotenv
import base64
from openai import OpenAI

load_dotenv()

class InvalidImageError(Exception):
    """Raised when the image is not a valid door photo"""
    pass

class DoorAnalyzer:
    """Analyzes door images to extract features for handle recommendation using OpenAI Vision API"""

    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")

        self.client = OpenAI(api_key=self.openai_api_key)
        print("[DoorAnalyzer] Initialized with OpenAI API")

    def validate_image(self, base64_image: str) -> tuple[bool, str]:
        """
        Validate that the image contains a door

        Args:
            base64_image: Base64 encoded image

        Returns:
            Tuple of (is_valid, message)
        """
        print("[DoorAnalyzer] Validating image...")

        validation_prompt = """Посмотри на это изображение и ответь на вопрос: "Это фотография двери?"

Верни ТОЛЬКО JSON объект в следующем формате (без дополнительного текста):
{
  "is_door": true/false,
  "confidence": 0.0-1.0,
  "reason": "краткое пояснение на русском, что изображено на фото"
}

Примеры:
- Если это дверь (входная, межкомнатная, дверное полотно) -> is_door: true
- Если это НЕ дверь (окно, мебель, человек, пейзаж, текст и т.д.) -> is_door: false"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": validation_prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=150
            )

            validation_text = response.choices[0].message.content.strip()
            print(f"[DoorAnalyzer] Validation response: {validation_text}")

            # Parse JSON response
            if validation_text.startswith("```json"):
                validation_text = validation_text.split("```json")[1].split("```")[0].strip()
            elif validation_text.startswith("```"):
                validation_text = validation_text.split("```")[1].split("```")[0].strip()

            validation_result = json.loads(validation_text)

            is_door = validation_result.get('is_door', False)
            confidence = validation_result.get('confidence', 0.0)
            reason = validation_result.get('reason', 'Неизвестная причина')

            print(f"[DoorAnalyzer] Validation result: is_door={is_door}, confidence={confidence}, reason={reason}")

            if not is_door or confidence < 0.6:
                return False, reason

            return True, reason

        except Exception as e:
            print(f"[DoorAnalyzer] Validation error: {str(e)}")
            # If validation fails, assume it's valid to avoid blocking legitimate requests
            return True, "Не удалось проверить изображение"

    def analyze_door(self, image_path: str) -> dict:
        """
        Analyze door image and extract structured features using GPT-4 Vision

        Args:
            image_path: Path to door image file

        Returns:
            Dictionary with door characteristics and embedding

        Raises:
            InvalidImageError: If the image is not a valid door photo
        """
        print(f"[DoorAnalyzer] Analyzing door image: {image_path}")

        try:
            # Read and encode image to base64
            with open(image_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')

            # Validate that the image contains a door
            is_valid, validation_reason = self.validate_image(base64_image)
            if not is_valid:
                print(f"[DoorAnalyzer] Image validation failed: {validation_reason}")
                raise InvalidImageError(f"На фото не дверь. {validation_reason}")

            print(f"[DoorAnalyzer] Image validated successfully: {validation_reason}")

            # Also calculate basic color features locally
            with Image.open(image_path) as img:
                print(f"[DoorAnalyzer] Image size: {img.size}, mode: {img.mode}")
                img_rgb = img.convert("RGB")
                img_array = np.array(img_rgb)
                avg_color = img_array.mean(axis=(0, 1))
                brightness = avg_color.mean() / 255.0
                print(f"[DoorAnalyzer] Average color: RGB{tuple(int(c) for c in avg_color)}, brightness: {brightness:.2f}")

            # Use GPT-4 Vision to analyze the door
            print("[DoorAnalyzer] Calling GPT-4 Vision API for detailed analysis...")

            vision_prompt = """Проанализируй эту дверь и определи следующие характеристики:

1. Цвет двери (белый, светлое дерево, темное дерево, черный, коричневый и т.д.)
2. Цветовая группа (light/dark/warm/cold)
3. Стиль (modern_minimal, classic, contemporary, rustic)
4. Материал (painted_wood, natural_wood, metal, glass и т.д.)
5. Тон (warm - теплый, cold - холодный)

Верни ТОЛЬКО JSON объект в следующем формате (без дополнительного текста):
{
  "door_color": "white",
  "door_color_group": "light",
  "door_tone": "cold",
  "door_style": "modern_minimal",
  "door_material": "painted_wood",
  "description": "Краткое описание двери на русском"
}"""

            response = self.client.chat.completions.create(
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
                max_tokens=300
            )

            analysis_text = response.choices[0].message.content.strip()
            print(f"[DoorAnalyzer] Vision API response: {analysis_text}")

            # Parse JSON response
            if analysis_text.startswith("```json"):
                analysis_text = analysis_text.split("```json")[1].split("```")[0].strip()
            elif analysis_text.startswith("```"):
                analysis_text = analysis_text.split("```")[1].split("```")[0].strip()

            door_analysis = json.loads(analysis_text)

            # Generate embedding for the door description
            print("[DoorAnalyzer] Generating text embedding for door description...")
            embedding_text = f"{door_analysis.get('description', '')} {door_analysis.get('door_style', '')} {door_analysis.get('door_color', '')} door"

            embedding_response = self.client.embeddings.create(
                model="text-embedding-3-small",
                input=embedding_text
            )

            embedding = embedding_response.data[0].embedding
            print(f"[DoorAnalyzer] Embedding generated: dimension={len(embedding)}")

            # Determine preferred handle characteristics
            color_group = door_analysis.get('door_color_group', 'light')
            style = door_analysis.get('door_style', 'modern_minimal')

            if color_group == "light":
                preferred_handle_colors = ["black", "graphite", "dark_bronze"]
                preferred_color_group = "dark"
            elif color_group == "dark":
                preferred_handle_colors = ["white", "chrome", "satin_chrome"]
                preferred_color_group = "light"
            else:  # warm
                preferred_handle_colors = ["bronze", "gold", "copper", "black"]
                preferred_color_group = "dark"

            # Determine preferred rose shape
            preferred_rose_shape = "Квадратная" if "modern" in style else "Круглая"

            # Combine all characteristics
            door_characteristics = {
                "door_color": door_analysis.get('door_color', 'white'),
                "door_color_group": color_group,
                "door_tone": door_analysis.get('door_tone', 'cold'),
                "door_style": style,
                "door_material": door_analysis.get('door_material', 'painted_wood'),
                "hardware_color_current": None,
                "preferred_rose_shape": preferred_rose_shape,
                "preferred_handle_style": style,
                "preferred_finish_colors": preferred_handle_colors,
                "preferred_color_group": preferred_color_group,
                "need_contrast": True,
                "embedding": embedding,
                "brightness": float(brightness),
                "description": door_analysis.get('description', '')
            }

            print(f"[DoorAnalyzer] Analysis complete: {json.dumps({k:v for k,v in door_characteristics.items() if k != 'embedding'}, ensure_ascii=False, indent=2)}")
            return door_characteristics

        except InvalidImageError:
            # Re-raise validation errors
            raise
        except Exception as e:
            print(f"[DoorAnalyzer] ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
            raise
