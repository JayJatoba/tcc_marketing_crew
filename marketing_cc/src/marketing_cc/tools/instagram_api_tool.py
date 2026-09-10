import os
import time
import requests
from typing import Type, List
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from crewai.tools import BaseTool

load_dotenv()


INITIAL_PRE_PROCESSING_DELAY = 60  
MAX_RETRIES = 5                   
RETRY_DELAY = 15                   
BUFFER_WAITING_TIME = 15                   
POLL_INTERVAL = 5                  
MAX_POLL_TIMEOUT = 60              


class InstagramCarouselToolInput(BaseModel):
    image_urls: List[str] = Field(..., description="List of publicly accessible image URLs (2 to 10 images) to publish.")
    caption: str = Field(..., description="Caption text for the Instagram post.")

class InstagramAPITool(BaseTool):
    name: str = "Instagram Carousel Tool" 
    description: str = (
        "Publishes a multiple-image carousel post with a caption to Instagram via the Graph API. "
        "Requires a list of image URLs."
    )
    args_schema: Type[BaseModel] = InstagramCarouselToolInput

    access_token: str = Field(
        default_factory=lambda: os.getenv("INSTAGRAM_ACCESS_TOKEN", "")
    )
    ig_account_id: str = Field(
        default_factory=lambda: os.getenv("INSTAGRAM_ACCOUNT_ID", "")
    )
    base_url: str = Field(
        default_factory=lambda: os.getenv("INSTAGRAM_BASE_URL", "https://graph.facebook.com/v19.0")
    )

    def _run(self, image_urls: List[str], caption: str) -> str:
        if not self.access_token or not self.ig_account_id:
            return "Error: INSTAGRAM_ACCESS_TOKEN or INSTAGRAM_ACCOUNT_ID is missing from environment variables."

        if not isinstance(image_urls, list) or len(image_urls) < 2 or len(image_urls) > 10:
            return f"Error: Instagram carousels require a list of between 2 and 10 image URLs. Received: {len(image_urls) if isinstance(image_urls, list) else 'Not a list'}"

        print(f"⏳ Waiting {INITIAL_PRE_PROCESSING_DELAY}s for hosted images to propagate before Instagram processing...")
        time.sleep(INITIAL_PRE_PROCESSING_DELAY)

        child_ids = []
        for i, url in enumerate(image_urls):
            print(f"-> Processing child image {i+1} of {len(image_urls)}...")
            child_res = self.stage_child(image_url=url)
            if "error" in child_res or not child_res.get("id"):
                error_details = child_res.get("details", child_res.get("error", "Unknown child staging error"))
                return f"Instagram API Error staging child image '{url}': {error_details}"
            
            child_id = child_res["id"]
            
            if not self.wait_for_container(child_id):
                return f"Instagram API Error: Child image {i+1} failed processing or timed out on Meta's servers."
                
            child_ids.append(child_id)
            time.sleep(BUFFER_WAITING_TIME) 

        parent_res = self.stage_parent(child_ids=child_ids, caption=caption)
        if "error" in parent_res or not parent_res.get("id"):
            error_details = parent_res.get("details", parent_res.get("error", "Unknown parent staging error"))
            return f"Instagram API Error staging parent carousel: {error_details}"
        
        time.sleep(BUFFER_WAITING_TIME)

        published = self.publish_carousel(creation_id=parent_res["id"])
        if "error" in published or not published.get("id"):
            error_details = published.get("details", published.get("error", "Unknown publish error"))
            return f"Instagram API Error during publishing: {error_details}"

        return f"Successfully published Carousel to Instagram! Post ID: {published.get('id')}"

    def stage_child(self, image_url: str) -> dict:
        container_url = f"{self.base_url}/{self.ig_account_id}/media"
        container_payload = {
            "image_url": image_url,
            "is_carousel_item": "true"
        }
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }
        
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                container_response = requests.post(
                    url=container_url, data=container_payload, headers=headers
                )
                res_json = container_response.json()

                if "error" in res_json:
                    subcode = res_json.get("error", {}).get("error_subcode")
                    if (subcode == 2207052 or "error" in res_json) and attempt < MAX_RETRIES:
                        print(f"⚠️ Staging attempt {attempt}/{MAX_RETRIES} failed. Waiting {RETRY_DELAY}s before retry...")
                        time.sleep(RETRY_DELAY)
                        continue

                container_response.raise_for_status()
                return res_json
            except requests.exceptions.RequestException as e:
                if attempt < MAX_RETRIES:
                    print(f"⚠️ Request exception on attempt {attempt}/{MAX_RETRIES}. Waiting {RETRY_DELAY}s before retry...")
                    time.sleep(RETRY_DELAY)
                    continue
                details = e.response.text if e.response is not None else str(e)
                return {"error": str(e), "details": details}

        return {"error": "Failed to stage child container after max retries"}

    def wait_for_container(self, container_id: str) -> bool:
        url = f"{self.base_url}/{container_id}"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        start_time = time.time()
        
        print(f"   -> Polling status for container ID: {container_id}...")
        while time.time() - start_time < MAX_POLL_TIMEOUT:
            try:
                res = requests.get(url, params={"fields": "status_code"}, headers=headers)
                if res.status_code == 200:
                    status = res.json().get("status_code")
                    print(f"      [Status]: {status}")
                    if status == "FINISHED":
                        return True
                    elif status in ["ERROR", "EXPIRED"]:
                        return False
            except Exception:
                pass
            time.sleep(POLL_INTERVAL)
        return False

    def stage_parent(self, child_ids: List[str], caption: str) -> dict:
        container_url = f"{self.base_url}/{self.ig_account_id}/media"
        container_payload = {
            "media_type": "CAROUSEL",
            "caption": caption,
            "children": ",".join(child_ids) 
        }
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }
        
        try:
            container_response = requests.post(
                url=container_url, data=container_payload, headers=headers
            )
            container_response.raise_for_status()
            return container_response.json()
        except requests.exceptions.RequestException as e:
            details = e.response.text if e.response is not None else str(e)
            return {"error": str(e), "details": details}

    def publish_carousel(self, creation_id: str) -> dict:
        container_url = f"{self.base_url}/{self.ig_account_id}/media_publish"
        container_payload = {
            "creation_id": creation_id
        }
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }

        try:
            container_response = requests.post(
                url=container_url, data=container_payload, headers=headers
            )
            container_response.raise_for_status()
            return container_response.json()
        except requests.exceptions.RequestException as e:
            details = e.response.text if e.response is not None else str(e)
            return {"error": str(e), "details": details}