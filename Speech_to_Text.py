import requests
import os

api_token = os.getenv("IOTYPE_API_KEY") 

if not api_token:
    print("Error: The 'IOTYPE_API_KEY' environment variable is not set.")
    print("Please set it before running the script.")
    exit()

api_url = "https://www.iotype.com/developer/transcription"
headers = {
    "Authorization": api_token,
    "Accept": "application/json",
    "X-Requested-With": "XMLHttpRequest"
}
payload = {
    "type": "file"
}
file_path = "Voice.mp3"

try:
    with open(file_path, 'rb') as f:

        files_to_upload = {
            'file': (file_path, f, 'audio/mpeg')
        }
        
        print("Sending transcription request to iotype.com...")
        
        response = requests.post(api_url, headers=headers, data=payload, files=files_to_upload)
        
        if response.status_code == 200:
            print("Request successful. Processing response...")
            
            json_data = response.json()
            
            transcribed_text = json_data["result"]
            
            output_filename = "transcription_result.txt"
            
            with open(output_filename, "w", encoding="utf-8") as f:
                f.write(transcribed_text)
            
            print(f"✅ Successfully transcribed text saved to '{output_filename}'")

        else:
            print(f"Error in request. Status code: {response.status_code}")
            print("Error message:")
            print(response.text)

except FileNotFoundError:
    print(f"Error: File not found at specified path: {file_path}")
except requests.exceptions.RequestException as e:
    print(f"Error connecting to API: {e}")
