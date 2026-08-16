import base64
import os
from pathlib import Path
import re
from crewai.tools import BaseTool
from dotenv import load_dotenv
import requests

class ImageHostingTool(BaseTool):
    name: str = "Image Hosting Tool"
    description: str = (
        "Uploads a local image file to ImgBB to generate a public URL. "
        "Accepts a file path string or text containing an image path."
    )
    _ = load_dotenv()
    

    def _run(self, local_file_path: str) -> str:
        api_key = os.getenv("IMG_BB_TOKEN")
        base_url = os.getenv("IMG_BB_BASE_URL") 
        
        try:
            clean_input = local_file_path.strip().strip("'").strip('"')
            
            path_match = re.search(
                r'([a-zA-Z]:[\\/][^:\n\r]+|\boutput[\\/][^:\n\r]+|\b[^\s]+\.(?:png|jpg|jpeg))', 
                clean_input, 
                re.IGNORECASE
            )
            if path_match:
                clean_input = path_match.group(1)

            image_path = Path(clean_input).resolve()

            if not image_path.exists():
                return f"Error: File does not exist at normalized path: {image_path}"   
                    
            with open(image_path, "rb") as file:
                print('testing')
                query_params = {
                    "key": api_key,
                }
                payload={
                    "image": base64.b64encode(file.read()),
                }
                response = requests.request('POST', url=base_url, params = query_params, data=payload)
                response.raise_for_status()
                print(response.json())
                
                public_url = response.json()["data"]["url"]
                return public_url
                
        except FileNotFoundError as e:
            return f"Error: Could not find the image file at {image_path}"
        except Exception as e:
            return f"Image upload failed: {str(e)}"