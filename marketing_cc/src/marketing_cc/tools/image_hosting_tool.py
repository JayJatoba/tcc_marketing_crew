import base64
import os
from pathlib import Path
import re
from typing import Type, List
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
from dotenv import load_dotenv
import requests

load_dotenv()
class ImgBBBatchUploadToolInput(BaseModel):
    file_paths: List[str] = Field(
        ..., 
        description="List of local file paths pointing to the generated images."
    )

class ImageHostingTool(BaseTool):
    name: str = "Image Hosting Tool"
    description: str = (
        "Uploads a batch of local image files to ImgBB to generate public URLs. "
        "Accepts a list of file path strings and returns a list of public URLs."
    )
    args_schema: Type[BaseModel] = ImgBBBatchUploadToolInput

    def _run(self, file_paths: List[str]) -> List[str]:
        api_key = os.getenv("IMG_BB_TOKEN")
        base_url = os.getenv("IMG_BB_BASE_URL") 
        
        uploaded_urls = []
        
        for path in file_paths:
            try:
                clean_input = path.strip().strip("'").strip('"')
                
                path_match = re.search(
                    r'([a-zA-Z]:[\\/][^:\n\r]+|\boutput[\\/][^:\n\r]+|\b[^\s]+\.(?:png|jpg|jpeg))', 
                    clean_input, 
                    re.IGNORECASE
                )
                if path_match:
                    clean_input = path_match.group(1)

                image_path = Path(clean_input).resolve()

                if not image_path.exists():
                    uploaded_urls.append(f"Error: File does not exist at normalized path: {image_path}") 
                        
                with open(image_path, "rb") as file:
                    print(f'Uploading {image_path}...')
                    query_params = {
                        "key": api_key,
                    }
                    payload={
                        "image": base64.b64encode(file.read()),
                    }
                    response = requests.request('POST', url=base_url, params=query_params, data=payload)
                    response.raise_for_status()
                    
                    public_url = response.json()["data"]["url"]
                    uploaded_urls.append(public_url)
                    
            except FileNotFoundError as e:
                uploaded_urls.append(f"Error: Could not find the image file at {image_path}")
            except Exception as e:
                uploaded_urls.append(f"Error uploading {path}: {str(e)}")
                
        return uploaded_urls