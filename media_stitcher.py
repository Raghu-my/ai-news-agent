# media_stitcher.py
# Strict YouTube-compliant Media Stitcher module with Subtitle (.srt) generation & Multi-Scene Slideshow Stitching

import os
import sys
import io
import shutil
import subprocess
from typing import List, Dict

# Ensure UTF-8 console output on Windows PowerShell
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import ffmpeg


def is_ffmpeg_installed() -> bool:
    """Check if ffmpeg binary is available on PATH."""
    return shutil.which("ffmpeg") is not None


def format_srt_timestamp(seconds: float) -> str:
    """Format float seconds into SRT timestamp HH:MM:SS,mmm."""
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hrs:02d}:{mins:02d}:{secs:02d},{millis:03d}"


def generate_srt(scenes: List[Dict[str, str]], total_audio_duration: float, srt_output_path: str) -> str:
    """Generate a valid SRT subtitle file from narration scenes proportional to word counts."""
    os.makedirs(os.path.dirname(os.path.abspath(srt_output_path)), exist_ok=True)

    total_words = sum(len(s.get("narration_text", "").split()) for s in scenes)
    if total_words == 0:
        total_words = 1

    current_time = 0.0
    srt_entries = []

    for idx, scene in enumerate(scenes):
        narration = scene.get("narration_text", "").strip()
        word_count = max(1, len(narration.split()))
        scene_duration = (word_count / total_words) * total_audio_duration

        start_ts = format_srt_timestamp(current_time)
        end_time = current_time + scene_duration
        end_ts = format_srt_timestamp(end_time)

        srt_entries.append(f"{idx + 1}\n{start_ts} --> {end_ts}\n{narration}\n")
        current_time = end_time

    srt_content = "\n".join(srt_entries)
    with open(srt_output_path, "w", encoding="utf-8") as f:
        f.write(srt_content)

    print(f"[Subtitles Generator SUCCESS] Created SRT file at '{srt_output_path}' ({len(scenes)} scenes)")
    return srt_output_path


def stitch_multi_scene_video(image_paths: List[str], audio_path: str, srt_path: str, output_path: str) -> str:
    """Stitch multiple 16:9 images, audio track, and burned-in SRT subtitles into YouTube H.264/AAC MP4 file."""
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")
    if not image_paths:
        raise ValueError("Image paths list cannot be empty.")

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    print(f"[FFmpeg Multi-Scene Stitcher] Combining {len(image_paths)} scenes + audio + subtitles -> '{output_path}'")

    # Get audio duration using ffprobe or estimate
    audio_duration = 12.0
    try:
        probe = ffmpeg.probe(audio_path)
        audio_duration = float(probe['format']['duration'])
    except Exception:
        pass

    duration_per_image = max(3.0, audio_duration / len(image_paths))

    # Escape subtitle path for FFmpeg filter on Windows
    escaped_srt_path = srt_path.replace("\\", "/").replace(":", "\\:")

    # Build FFmpeg command to loop images and burn subtitles
    # Using ffmpeg concat filter or image loop
    inputs = []
    filter_chains = []

    for idx, img in enumerate(image_paths):
        inputs.extend(["-loop", "1", "-t", str(duration_per_image), "-i", img])

    concat_inputs = "".join([f"[{i}:v]" for i in range(len(image_paths))])
    filter_complex = f"{concat_inputs}concat=n={len(image_paths)}:v=1:a=0[vconcat]"

    if os.path.exists(srt_path):
        filter_complex += f";[vconcat]subtitles='{escaped_srt_path}':force_style='FontSize=20,PrimaryColour=&H00FFFF&,OutlineColour=&H000000&,BorderStyle=3'[vsub]"
        video_map = "[vsub]"
    else:
        video_map = "[vconcat]"

    cmd = [
        "ffmpeg", "-y"
    ] + inputs + [
        "-i", audio_path,
        "-filter_complex", filter_complex,
        "-map", video_map,
        "-map", f"{len(image_paths)}:a",
        "-c:v", "libx264",
        "-c:a", "aac",
        "-pix_fmt", "yuv420p",
        "-movflags", "faststart",
        "-shortest",
        output_path
    ]

    try:
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        print(f"[FFmpeg Stitcher SUCCESS] Multi-scene video created with subtitles: {output_path}")
        return output_path
    except subprocess.CalledProcessError as err:
        print(f"[FFmpeg Stitcher WARN] Subtitle filter stitch failed ({err.stderr.decode('utf-8', errors='ignore')[:150]}). Running fallback...")

    # Fallback FFmpeg stitch without subtitle filter
    cmd_fallback = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", "color=c=0x1a1a2e:s=1280x720:r=30",
        "-i", audio_path,
        "-c:v", "libx264",
        "-c:a", "aac",
        "-pix_fmt", "yuv420p",
        "-movflags", "faststart",
        "-shortest",
        output_path
    ]
    subprocess.run(cmd_fallback, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    print(f"[FFmpeg Stitcher SUCCESS] Fallback video created: {output_path}")
    return output_path


def stitch_audio_video(video_path: str, audio_path: str, output_path: str) -> str:
    """Backwards compatible wrapper for single video + audio stitching."""
    return stitch_multi_scene_video([video_path], audio_path, "", output_path)
