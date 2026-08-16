import os
import time
import requests
from typing import Type
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from crewai.tools import BaseTool

load_dotenv()

# Define explicit input schema for CrewAI tool invocation
class InstagramAPIToolInput(BaseModel):
    image_url: str = Field(..., description="Publicly accessible image URL to publish.")
    caption: str = Field(..., description="Caption text for the Instagram post.")

class InstagramAPITool(BaseTool):
    name: str = "Instagram API Tool"
    description: str = (
        "Publishes an image post with a caption to Instagram via the Graph API."
    )
    args_schema: Type[BaseModel] = InstagramAPIToolInput

    access_token: str = Field(
        default_factory=lambda: os.getenv("INSTAGRAM_ACCESS_TOKEN", "")
    )
    ig_account_id: str = Field(
        default_factory=lambda: os.getenv("INSTAGRAM_ACCOUNT_ID", "")
    )
    base_url: str = Field(
        default_factory=lambda: os.getenv("INSTAGRAM_BASE_URL", "https://graph.facebook.com/v19.0")
    )

    def _run(self, image_url: str, caption: str) -> str:
        if not self.access_token or not self.ig_account_id:
            return "Error: INSTAGRAM_ACCESS_TOKEN or INSTAGRAM_ACCOUNT_ID is missing from environment variables."

        staged_image = self.stage_image(image_url=image_url, caption=caption)
        if "error" in staged_image or not staged_image.get("id"):
            error_details = staged_image.get("details", staged_image.get("error", "Unknown staging error"))
            return f"Instagram API Error during staging: {error_details}"

        stage_image_id = staged_image["id"]

        published_image = self.publish_image(stage_image_id)
        if "error" in published_image or not published_image.get("id"):
            error_details = published_image.get("details", published_image.get("error", "Unknown publish error"))
            return f"Instagram API Error during publishing: {error_details}"

        return f"Successfully published to Instagram! Post ID: {published_image.get('id')}"

    def stage_image(self, image_url: str, caption: str, retries: int = 3, delay: int = 3) -> dict:
        container_url = f"{self.base_url}/{self.ig_account_id}/media"
        container_payload = {
            "image_url": image_url,
            "caption": caption
        }
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }
        
        for attempt in range(retries):
            try:
                container_response = requests.post(
                    url=container_url, data=container_payload, headers=headers
                )
                
                res_json = container_response.json()

                if "error" in res_json:
                    subcode = res_json.get("error", {}).get("error_subcode")
                    if subcode == 2207052 and attempt < retries - 1:
                        time.sleep(delay)
                        continue

                container_response.raise_for_status()
                return res_json
            except requests.exceptions.RequestException as e:
                details = e.response.text if e.response is not None else str(e)
                return {"error": str(e), "details": details}

    def publish_image(self, image_id: str) -> dict:
        container_url = f"{self.base_url}/{self.ig_account_id}/media_publish"
        container_payload = {
            "creation_id": image_id
        }
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }

        try:
            container_response = requests.post(
                url=container_url, json=container_payload, headers=headers
            )
            container_response.raise_for_status()
            return container_response.json()
        except requests.exceptions.RequestException as e:
            details = e.response.text if e.response is not None else str(e)
            return {"error": str(e), "details": details}