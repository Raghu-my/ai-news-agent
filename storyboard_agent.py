# storyboard_agent.py
# Storyboard AI module using Gemini 2.5 Flash for 10-scene documentary storytelling & Imagen 3 / Unsplash fallbacks

import os
import sys
import io
import json
import re
import urllib.parse
import urllib.request
from typing import List, Dict
from PIL import Image, ImageDraw

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
    """Generate a 10-scene long-form documentary storyboard array using Gemini 2.5 Flash.

    Returns a list of 10 dicts: [{'narration_text': '...', 'image_prompt': '...'}, ...]
    """
    print(f"\n[Storyboard AI] Generating 10-scene long-form documentary script for topic: '{topic}'...")

    system_instruction = (
        "You are a professional documentary scriptwriter. Write a comprehensive, highly detailed 600-word deep-dive script about the topic. "
        "Break this script into exactly 10 scenes. "
        "Return your response strictly as a single-line JSON array of objects. "
        "Each object must have exactly two keys: 'narration_text' (2 sentences of in-depth documentary commentary) "
        "and 'image_prompt' (a detailed 16:9 cinematic visual scene description for AI image generation)."
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
                max_output_tokens=2500
            )
        )

        resp_text = response.text.strip() if response.text else "[]"
        scenes = json.loads(resp_text, strict=False)

        if isinstance(scenes, list) and len(scenes) >= 3:
            print(f"[Storyboard AI SUCCESS] Generated {len(scenes)} documentary visual scenes.")
            return scenes

    except Exception as e:
        print(f"[Storyboard AI Note] Gemini JSON parse error ({e}). Using 10-scene fallback storyboard...")

    # 10-scene documentary fallback
    return [
        {
            "narration_text": f"Welcome to an in-depth documentary report on {topic}. Software architecture is undergoing a dramatic shift.",
            "image_prompt": f"A cinematic wide shot of a modern tech laboratory working on {topic}, 8k resolution, highly detailed."
        },
        {
            "narration_text": "Autonomous coding agents are no longer experimental concepts; they are actively writing enterprise production code.",
            "image_prompt": "Digital neural networks glowing with cyan data streams representing artificial intelligence coding agents."
        },
        {
            "narration_text": "Deep learning models process complex pull requests, refactor legacy codebases, and optimize cloud infrastructure in seconds.",
            "image_prompt": "Futuristic glass server rack room illuminated by blue and violet LED lights, photorealistic 16:9 aspect ratio."
        },
        {
            "narration_text": "Engineering teams report a tenfold increase in feature deployment velocity as autonomous agents handle repetitive tasks.",
            "image_prompt": "High-tech software developer workstation with multiple curved monitors displaying code analytics."
        },
        {
            "narration_text": "Security scanning and vulnerability patching are now executed in real time, preventing breaches before code is deployed.",
            "image_prompt": "Digital security shield overlaying cloud infrastructure network nodes, 8k cinematic lighting."
        },
        {
            "narration_text": "Despite rapid technical adoption, questions around code governance, intellectual property, and safety compliance remain prominent.",
            "image_prompt": "Abstract digital balance scale with glowing data blocks and regulatory compliance symbols."
        },
        {
            "narration_text": "Senior technology leaders emphasize that human oversight and architectural intuition are more critical than ever.",
            "image_prompt": "A modern tech executive analyzing holographic AI system diagnostics in a high-rise office at twilight."
        },
        {
            "narration_text": "As foundational models evolve, agentic workflows seamlessly integrate across continuous integration pipelines.",
            "image_prompt": "Interconnected global cloud computing nodes beaming light streams across a stylized digital globe."
        },
        {
            "narration_text": "The future of software development belongs to hybrid human-AI engineering organizations operating at unprecedented scale.",
            "image_prompt": "Collaborative tech workspace where software engineers interact with augmented reality data interfaces."
        },
        {
            "narration_text": f"This concludes our special documentary report on {topic}. Subscribe for more autonomous AI engineering updates.",
            "image_prompt": "Sleek metallic AI news broadcast studio background with glowing modern news lower-thirds graphic."
        }
    ]


def download_unsplash_fallback_image(topic_keyword: str, output_path: str) -> bool:
    """Download a high-resolution 16:9 technology image from Unsplash as visual fallback."""
    encoded_topic = urllib.parse.quote(topic_keyword)
    unsplash_url = f"https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=1920&h=1080&fit=crop"

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    try:
        print(f"[Unsplash Fallback] Fetching 16:9 stock visual for '{topic_keyword}'...")
        req = urllib.request.Request(unsplash_url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            img_data = resp.read()
            with open(output_path, "wb") as f:
                f.write(img_data)
        print(f"[Unsplash Fallback SUCCESS] Downloaded image saved to '{output_path}'")
        return True
    except Exception as e:
        print(f"[Unsplash Fallback Note] Could not fetch online image ({e}). Using Pillow renderer...")
        return False


def generate_scene_image(image_prompt: str, output_path: str) -> str:
    """Generate a 16:9 image using Vertex AI Imagen 3 or Unsplash / Pillow fallbacks."""
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
        print(f"\n[GCP Imagen 3 Exception] Vertex AI Error: {e}")
        print("[Fallback Handler] Attempting Unsplash stock visual fallback...")

    # Attempt Unsplash Fallback
    if download_unsplash_fallback_image(image_prompt[:30], output_path):
        return output_path

    # Local Pillow Fallback (1280x720 16:9)
    img = Image.new("RGB", (1280, 720), color=(26, 26, 46))
    draw = ImageDraw.Draw(img)

    draw.rectangle([40, 40, 1240, 680], outline=(0, 210, 255), width=4)
    draw.line([40, 360, 1240, 360], fill=(70, 70, 100), width=2)

    text_header = "AI DOCUMENTARY STORYBOARD"
    text_sub = image_prompt[:65] + "..." if len(image_prompt) > 65 else image_prompt

    draw.text((80, 80), text_header, fill=(0, 255, 200))
    draw.text((80, 140), text_sub, fill=(255, 255, 255))

    img.save(output_path, "JPEG")
    print(f"[Pillow Fallback] Generated 16:9 visual at '{output_path}'")
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
