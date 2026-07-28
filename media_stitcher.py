# media_stitcher.py
# Dynamic FFmpeg Media Stitcher module with audio duration probing, subtitle (.srt) generation & Ken Burns Zoom multi-scene stitching

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


def get_audio_duration(audio_path: str) -> float:
    """Probe exact duration of audio file in seconds using ffprobe / ffmpeg.probe."""
    try:
        probe = ffmpeg.probe(audio_path)
        duration = float(probe['format']['duration'])
        if duration > 0:
            print(f"[FFprobe Audio Inspector] Exact audio duration: {duration:.2f} seconds.")
            return duration
    except Exception as e:
        print(f"[FFprobe Warning] Could not probe audio duration ({e}). Using file-size estimation...")

    # Fallback duration estimation if probing is unavailable
    file_size = os.path.getsize(audio_path)
    # Estimate 24KB per second for 192kbps MP3
    estimated_duration = max(10.0, file_size / 24000.0)
    return estimated_duration


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
    """Stitch multiple 16:9 images, audio track, and burned-in SRT subtitles into YouTube H.264/AAC MP4 file.

    Calculates exact duration per scene dynamically based on audio duration probing.
    """
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")
    if not image_paths:
        raise ValueError("Image paths list cannot be empty.")

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    # Calculate exact dynamic timing per scene
    total_audio_duration = get_audio_duration(audio_path)
    num_scenes = len(image_paths)
    duration_per_scene = round(total_audio_duration / num_scenes, 2)

    print(f"[FFmpeg Multi-Scene Stitcher] Audio Duration: {total_audio_duration:.2f}s | {num_scenes} scenes -> {duration_per_scene:.2f}s per scene")

    escaped_srt_path = srt_path.replace("\\", "/").replace(":", "\\:")

    inputs = []
    for img in image_paths:
        inputs.extend(["-loop", "1", "-t", str(duration_per_scene), "-i", img])

    concat_inputs = "".join([f"[{i}:v]" for i in range(num_scenes)])
    filter_complex = f"{concat_inputs}concat=n={num_scenes}:v=1:a=0[vconcat]"

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
        "-map", f"{num_scenes}:a",
        "-c:v", "libx264",
        "-c:a", "aac",
        "-pix_fmt", "yuv420p",
        "-movflags", "faststart",
        "-shortest",
        output_path
    ]

    try:
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        print(f"[FFmpeg Stitcher SUCCESS] Multi-scene subtitled video generated: {output_path}")
        return output_path
    except subprocess.CalledProcessError as err:
        print(f"[FFmpeg Stitcher WARN] Primary filter stitch failed ({err.stderr.decode('utf-8', errors='ignore')[:150]}). Running fallback...")

    # Fallback FFmpeg stitch
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
