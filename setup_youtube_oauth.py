# setup_youtube_oauth.py
# One-time script to perform YouTube OAuth 2.0 authorization (with Upload, Readonly & Analytics scopes)
# and store the resulting refresh token in Google Cloud Secret Manager.

import os
import sys
import io
import json
import webbrowser

# Ensure UTF-8 console output for Windows PowerShell
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
else:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
os.environ["OAUTHLIB_RELAX_TOKEN_SCOPE"] = "1"

from google_auth_oauthlib.flow import InstalledAppFlow
from google.cloud import secretmanager

PROJECT_ID = "gen-lang-client-0771706827"
SECRET_NAME = "youtube-refresh-token"
SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/yt-analytics.readonly"
]


def main():
    print("==================================================================")
    print(" ONE-TIME YOUTUBE OAUTH 2.0 REFRESH TOKEN GENERATOR & SECRET SETUP ")
    print("==================================================================\n")

    client_secrets_file = os.getenv("CLIENT_SECRETS_FILE", "client_secret.json")

    if not os.path.exists(client_secrets_file):
        print(f"ERROR: '{client_secrets_file}' not found in current directory.")
        return

    flow = InstalledAppFlow.from_client_secrets_file(
        client_secrets_file,
        SCOPES
    )

    print("Opening browser for YouTube authorization (Upload, Readonly & Analytics scopes)...")
    creds = flow.run_local_server(port=8088, prompt="consent", access_type="offline", open_browser=True)

    token_payload = {
        "refresh_token": creds.refresh_token,
        "client_id": creds.client_id,
        "client_secret": creds.client_secret
    }

    token_json = json.dumps(token_payload)

    print(f"\n[GCP Secret Manager] Storing multi-scope refresh token in secret '{SECRET_NAME}'...")
    client = secretmanager.SecretManagerServiceClient()
    parent = f"projects/{PROJECT_ID}"

    try:
        client.get_secret(request={"name": f"{parent}/secrets/{SECRET_NAME}"})
    except Exception:
        client.create_secret(
            request={
                "parent": parent,
                "secret_id": SECRET_NAME,
                "secret": {"replication": {"automatic": {}}}
            }
        )

    version = client.add_secret_version(
        request={
            "parent": f"{parent}/secrets/{SECRET_NAME}",
            "payload": {"data": token_json.encode("UTF-8")}
        }
    )

    print(f"\n[SUCCESS] Refresh token with YouTube Analytics & Upload scopes stored successfully in Secret Manager!")
    print(f"Version: {version.name}\n")


if __name__ == "__main__":
    main()
