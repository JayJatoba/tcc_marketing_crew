import os
from crewai.tools import BaseTool
import requests
from dotenv import load_dotenv

class InstagramAPITool(BaseTool):
    name: str = "Instagram API Tool"
    description: str = (
            "Uses instagram API to "
            "connect and analyze data "
            "of the page"
        )
    
    _ = load_dotenv()
    
    def __init__(self):
        self.access_token = os.getenv("INSTAGRAM_ACCESS_TOKEN")
        self.ig_account_id = os.getenv("INSTAGRAM_ACCOUNT_ID")
        self.base_url = os.getenv("INSTAGRAM_BASE_URL") 

    def _run(self, image_url: str, caption: str):
        staged_image = self.stage_image(image_url=image_url, caption=caption)
        stage_image_id = staged_image['id']
        if str(stage_image_id) == '':
            return "Instagram API Error. Error staging image for posting."
        
        published_image = self.publish_image(stage_image_id)
        if published_image['error']:
            return "Image posting failed: No image posted in feed."
        
    
    def stage_image(self, image_url: str, caption: str):
        container_url = f"{self.base_url}/{self.ig_account_id}/media"
        container_payload = {
            "image_url": image_url,
            "caption": caption
        }
        
        headers={
            "Authorization": f"Bearer {self.access_token}"
        }
        
        try:
            container_response = requests.request(method="POST", url=container_url, json=container_payload, headers=headers)
            container_response.raise_for_status()
            container_data = container_response.json()            
            
            return container_data
            
        except requests.exceptions.RequestException as e:
            return {"error": str(e), "details": e.response.text if e.response else "No response"}
        
    def publish_image(self, image_id: str):
        container_url = f"{self.base_url}/{self.ig_account_id}/media_publish"
        container_payload = {
            "creation_id": image_id
        }
        
        headers={
            "Authorization": f"Bearer {self.access_token}"
        }
        
        try:
            container_response = requests.request(method="POST", url=container_url, json=container_payload, headers=headers)
            container_response.raise_for_status()
            container_data = container_response.json()            
            
            return container_data
            
        except requests.exceptions.RequestException as e:
            print(e)
            return {"error": str(e), "details": e.response.text if e.response else "No response"} 