# test_endpoints.py
# End-to-end automated test suite for Phase 3 ai-news-agent FastAPI backend

import sys
import io

# Ensure UTF-8 output encoding for Windows PowerShell console
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
else:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def run_tests():
    print("\n" + "=" * 70)
    print(" 🚀 STARTING PHASE 3 MASTER END-TO-END AUTOMATED TEST SUITE ")
    print("=" * 70 + "\n")

    # ------------------------------------------------------------------
    # TEST 1: Health Check Endpoint
    # ------------------------------------------------------------------
    print("[STEP 1/5] Testing GET /health ...")
    health_response = client.get("/health")
    assert health_response.status_code == 200, f"Expected 200, got {health_response.status_code}: {health_response.text}"
    health_json = health_response.json()
    print("  [SUCCESS] GET /health OK!")
    print(f"  Response: {health_json}\n")

    # ------------------------------------------------------------------
    # TEST 2: Script Generation Endpoint (Vertex AI / Gemini 2.5 Flash)
    # ------------------------------------------------------------------
    print("[STEP 2/5] Testing POST /generate/script (Vertex AI Gemini 2.5 Flash) ...")
    payload = {"topic": "The rise of autonomous AI coding agents"}
    script_response = client.post("/generate/script", json=payload)
    assert script_response.status_code == 200, f"Expected 200, got {script_response.status_code}: {script_response.text}"

    script_data = script_response.json()
    generated_script = script_data.get("script", "")
    assert len(generated_script) > 0, "Generated script should not be empty"

    print("  [SUCCESS] POST /generate/script OK!")
    print("  --------------------------------------------------")
    print(f"  Generated Script:\n  \"{generated_script}\"")
    print("  --------------------------------------------------\n")

    # ------------------------------------------------------------------
    # TEST 3: Audio Synthesis Endpoint & GCS Storage
    # ------------------------------------------------------------------
    print("[STEP 3/5] Testing POST /generate/audio (GCP TTS -> GCS Media Vault) ...")
    audio_response = client.post("/generate/audio", params={"script": generated_script})
    assert audio_response.status_code == 200, f"Expected 200, got {audio_response.status_code}: {audio_response.text}"

    audio_json = audio_response.json()
    audio_gcs_uri = audio_json.get("audio_uri", "")
    assert audio_gcs_uri.startswith("gs://"), f"Audio URI should start with gs://, got {audio_gcs_uri}"

    print("  [SUCCESS] POST /generate/audio OK!")
    print(f"  GCS Audio Vault URI: {audio_gcs_uri}\n")

    # ------------------------------------------------------------------
    # TEST 4: Video Generation Endpoint (Veo 3.1 Model -> GCS)
    # ------------------------------------------------------------------
    print("[STEP 4/5] Testing POST /generate/video (Veo 3.1 Video Generation) ...")
    video_payload = {"prompt": "A cinematic shot of a futuristic cloud data center with AI nodes glowing"}
    video_response = client.post("/generate/video", json=video_payload)
    assert video_response.status_code == 200, f"Expected 200, got {video_response.status_code}: {video_response.text}"

    video_json = video_response.json()
    video_gcs_uri = video_json.get("video_uri", "")
    assert video_gcs_uri.startswith("gs://"), f"Video URI should start with gs://, got {video_gcs_uri}"

    print("  [SUCCESS] POST /generate/video OK!")
    print(f"  GCS Video Vault URI: {video_gcs_uri}\n")

    # ------------------------------------------------------------------
    # TEST 5: Master Autonomous Loop (/agent/run-cycle)
    # ------------------------------------------------------------------
    print("[STEP 5/5] Testing POST /agent/run-cycle (Full Autonomous Loop) ...")
    cycle_payload = {"topic": "Quantum computing breakthrough in 2026"}
    cycle_response = client.post("/agent/run-cycle", json=cycle_payload)
    assert cycle_response.status_code == 200, f"Expected 200, got {cycle_response.status_code}: {cycle_response.text}"

    cycle_data = cycle_response.json()
    print("  [SUCCESS] POST /agent/run-cycle OK!")
    print("  --------------------------------------------------")
    print(f"  Record UUID : {cycle_data.get('video_id')}")
    print(f"  Topic       : {cycle_data.get('topic')}")
    print(f"  Script      : \"{cycle_data.get('script')}\"")
    print(f"  Audio GCS   : {cycle_data.get('audio_gcs_uri')}")
    print(f"  Video GCS   : {cycle_data.get('video_gcs_uri')}")
    print(f"  DB Status   : {cycle_data.get('status')}")
    print(f"  YouTube URL : {cycle_data.get('youtube_url')}")
    print("  --------------------------------------------------\n")

    print("=" * 70)
    print(" 🎉 ALL 5 ENDPOINTS & MASTER AUTONOMOUS CYCLE TESTED SUCCESSFULLY! ")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    run_tests()
