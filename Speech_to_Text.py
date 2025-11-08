import requests
import sys
import os
from config import (
    IOTYPE_API_KEY, IOTYPE_API_URL, 
)
# --- Module 1: Speech-to-Text (iotype.com) ---

def speech_to_text(file_path = "Voice.mp3"):

    if not IOTYPE_API_KEY:
        print("Error: The 'IOTYPE_API_KEY' environment variable is not set.", file=sys.stderr)
        return None

    headers = {
        "Authorization": IOTYPE_API_KEY,
        "Accept": "application/json",
        "X-Requested-With": "XMLHttpRequest"
    }
    payload = {
        "type": "file"
    }

    try:
        with open(file_path, 'rb') as f:
            mime_type = 'audio/wav' if file_path.endswith('.wav') else 'audio/mpeg'
            
            files_to_upload = {
                'file': (os.path.basename(file_path), f, mime_type)
            }
            
            print(f"Sending {mime_type} transcription request to iotype.com...")
            
            response = requests.post(IOTYPE_API_URL, headers=headers, data=payload, files=files_to_upload)
            
            if response.status_code == 200:
                print("Request successful. Processing response...")
                json_data = response.json()
                transcribed_text = json_data.get("result", "")
                print(f"✅ Transcribed text: {transcribed_text}")
                return transcribed_text
            else:
                print(f"Error in request. Status code: {response.status_code}", file=sys.stderr)
                print("Error message:", response.text, file=sys.stderr)
                return None

    except FileNotFoundError:
        print(f"Error: File not found at specified path: {file_path}", file=sys.stderr)
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to API: {e}", file=sys.stderr)
        return None
    except KeyError:
        print(f"Error: 'result' key not found in API response. Response: {json_data}", file=sys.stderr)
        return None
