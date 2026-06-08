import base64
import os

from datetime import datetime

from crewai.tools import BaseTool
from dotenv import load_dotenv
from openai import OpenAI


class ImageGenerationTool(BaseTool):
    name: str = "AI Image Generator"

    description: str = (
        "Generates marketing images using AI "
        "based on prompts."
    )

    _ = load_dotenv()

    def _run(self, prompt: str) -> str:
        try:
            model = os.getenv("IMAGE_MODEL")

            client = OpenAI(
                api_key=os.getenv("OPENAI_API_KEY")
            )

            response = client.images.generate(
                model=model,
                prompt=prompt,
                size="1024x1024"
            )

            image_base64 = response.data[0].b64_json

            if not image_base64:
                return "Image generation failed: No image returned."

            image_bytes = base64.b64decode(image_base64)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            output_dir = f"output/{timestamp}/images"

            os.makedirs(output_dir, exist_ok=True)

            image_path = (
                f"{output_dir}/generated_image.png"
            )

            with open(image_path, "wb") as image_file:
                image_file.write(image_bytes)

            return (
                f"Image successfully generated "
                f"and saved at: {image_path}"
            )

        except Exception as e:
            return (
                f"Image generation failed: {str(e)}"
            )