# storyboard_agent.py
# Storyboard AI module using Gemini 2.5 Flash for multi-scene generation and Imagen 3 for 16:9 visuals

import os
import sys
import io
import json
import re
import uuid
from typing import List, Dict, Tuple
from PIL import Image, ImageDraw, ImageFont

# Ensure UTF-8 console output for Windows PowerShell
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from google import genai
from google.genai import types

GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID", "gen-lang-client-0771706827")
LOCAL_TEMP_DIR = os.getenv("LOCAL_TEMP_DIR", "temp_media")

os.makedirs(LOCAL_TEMP_DIR, exist_ok=True)


def get_genai_client():
    return genai.Client(
        vertexai=True,
        project=GCP_PROJECT_ID,
        location="us-central1"
    )


def generate_storyboard(topic: str) -> List[Dict[str, str]]:
    """Generate a multi-scene storyboard array using Gemini 2.5 Flash.

    Returns a list of dicts: [{'narration_text': '...', 'image_prompt': '...'}, ...]
    """
    print(f"\n[Storyboard AI] Generating multi-scene storyboard for topic: '{topic}'...")

    system_instruction = (
        "You are an expert broadcast news director. Create a 3-scene news story storyboard. "
        "Return strictly a single-line JSON array of objects. "
        "Each object must have exactly two keys: 'narration_text' (2 sentences of voiceover) "
        "and 'image_prompt' (a detailed 16:9 visual scene description for text-to-image AI)."
    )

    prompt = f"Topic: {topic}"

    try:
        client = get_genai_client()
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.7,
                response_mime_type="application/json",
                max_output_tokens=700
            )
        )

        resp_text = response.text.strip() if response.text else "[]"
        scenes = json.loads(resp_text, strict=False)

        if isinstance(scenes, list) and len(scenes) > 0:
            print(f"[Storyboard AI SUCCESS] Generated {len(scenes)} visual scenes.")
            return scenes

    except Exception as e:
        print(f"[Storyboard AI Note] Gemini JSON parse fallback ({e}). Using dev fallback storyboard...")

    # Fallback multi-scene storyboard
    return [
        {
            "narration_text": f"Breaking news on {topic}. AI automation is reshaping enterprise computing.",
            "image_prompt": f"A futuristic high-tech command center displaying holographic analytics about {topic}, 8k, cinematic."
        },
        {
            "narration_text": "Autonomous agents are now writing and verifying code faster than human developers.",
            "image_prompt": f"Digital neural network glowing nodes processing code architecture for {topic}, photorealistic."
        },
        {
            "narration_text": "Industry leaders predict unprecedented productivity gains across global technology sectors.",
            "image_prompt": f"A sleek modern glass office building with futuristic AI visualization overlay, sunset lighting."
        }
    ]


def generate_scene_image(image_prompt: str, output_path: str) -> str:
    """Generate a 16:9 image using Vertex AI Imagen 3 (imagen-3.0-generate-001) or fallback."""
    print(f"[Imagen 3] Rendering 16:9 visual for prompt: '{image_prompt[:60]}...'")

    try:
        client = get_genai_client()
        result = client.models.generate_images(
            model="imagen-3.0-generate-001",
            prompt=image_prompt,
            config=types.GenerateImagesConfig(
                number_of_images=1,
                aspect_ratio="16:9",
                output_mime_type="image/jpeg"
            )
        )

        if hasattr(result, "generated_images") and len(result.generated_images) > 0:
            img_bytes = result.generated_images[0].image.image_bytes
            with open(output_path, "wb") as f:
                f.write(img_bytes)
            print(f"[Imagen 3 SUCCESS] Rendered image saved to '{output_path}'")
            return output_path

    except Exception as e:
        print(f"[Imagen 3 Note] Imagen 3 API fallback triggered ({e}). Creating high-res Pillow visual...")

    # Fallback Image Generator using Pillow (1280x720 16:9)
    img = Image.new("RGB", (1280, 720), color=(26, 26, 46))
    draw = ImageDraw.Draw(img)

    # Draw decorative futuristic elements
    draw.rectangle([40, 40, 1240, 680], outline=(0, 210, 255), width=4)
    draw.line([40, 360, 1240, 360], fill=(70, 70, 100), width=2)

    text_header = "AI BREAKING NEWS"
    text_sub = image_prompt[:65] + "..." if len(image_prompt) > 65 else image_prompt

    draw.text((80, 80), text_header, fill=(0, 255, 200))
    draw.text((80, 140), text_sub, fill=(255, 255, 255))

    img.save(output_path, "JPEG")
    print(f"[Pillow Fallback] Generated 16:9 graphic at '{output_path}'")
    return output_path


def render_all_storyboard_scenes(scenes: List[Dict[str, str]], base_name: str) -> List[str]:
    """Loop through storyboard scenes and generate 16:9 images for each scene."""
    image_paths = []
    for idx, scene in enumerate(scenes):
        img_filename = f"scene_{base_name}_{idx + 1}.jpg"
        img_path = os.path.join(LOCAL_TEMP_DIR, img_filename)
        prompt = scene.get("image_prompt", f"High tech AI news scene {idx + 1}")
        rendered_path = generate_scene_image(prompt, img_path)
        image_paths.append(rendered_path)
    return image_paths
