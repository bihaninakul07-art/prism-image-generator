"""
API handler: talks to whichever image-generation backend the user picks.
No API key ever appears in source — everything comes from environment
variables loaded via python-dotenv (.env locally) or Streamlit Secrets
(when deployed).
"""
import os
import time
import requests
from io import BytesIO
from PIL import Image
from dotenv import load_dotenv

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")
STABILITY_KEY = os.getenv("STABILITY_KEY")

# Only the model confirmed live on Hugging Face's free "hf-inference"
# provider for text-to-image. Other Flux/SDXL variants now live behind
# paid third-party providers and are intentionally left out.
HF_MODELS = {
    "Flux Schnell (Hugging Face — free)": "black-forest-labs/FLUX.1-schnell",
}

HF_API_URL = "https://router.huggingface.co/hf-inference/models/{model}"
STABILITY_API_URL = "https://api.stability.ai/v2beta/stable-image/generate/core"

# Engine choices shown in the UI.
ENGINES = list(HF_MODELS.keys()) + ["Stability AI (paid — needs your own key)"]


class GenerationError(Exception):
    pass


def _check_key(key, name, env_var, help_url):
    if not key or "your_" in key:
        raise GenerationError(
            f"Missing {name} API key. Add {env_var} to your .env file "
            f"(local) or to Streamlit Secrets (deployed). Get one at {help_url}"
        )


def _generate_hf(prompt: str, model_label: str, width: int, height: int) -> Image.Image:
    """Generate via Hugging Face's free Inference Providers (hf-inference)."""
    _check_key(HF_TOKEN, "Hugging Face", "HF_TOKEN", "https://huggingface.co/settings/tokens")
    model_id = HF_MODELS[model_label]
    url = HF_API_URL.format(model=model_id)
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    payload = {
        "inputs": prompt,
        "parameters": {"width": width, "height": height},
    }

    # The model can be "cold" — retry a couple of times while it spins up.
    for attempt in range(3):
        response = requests.post(url, headers=headers, json=payload, timeout=120)
        if response.status_code == 200:
            content_type = response.headers.get("content-type", "")
            if "image" not in content_type:
                # Got JSON back instead of image bytes — surface the real error.
                raise GenerationError(f"Hugging Face did not return an image: {response.text[:300]}")
            return Image.open(BytesIO(response.content))
        if response.status_code == 503:
            time.sleep(8)
            continue
        raise GenerationError(f"Hugging Face API error {response.status_code}: {response.text[:300]}")

    raise GenerationError("Model is still loading after multiple retries. Try again in a moment.")


def _generate_stability(prompt: str, width: int, height: int) -> Image.Image:
    """Generate via Stability AI's Stable Image Core endpoint (paid, your own key)."""
    _check_key(STABILITY_KEY, "Stability AI", "STABILITY_KEY", "https://platform.stability.ai/account/keys")
    headers = {
        "authorization": f"Bearer {STABILITY_KEY}",
        "accept": "image/*",
    }
    data = {
        "prompt": prompt,
        "output_format": "png",
        "aspect_ratio": _closest_aspect_ratio(width, height),
    }
    response = requests.post(STABILITY_API_URL, headers=headers, files={"none": ""}, data=data, timeout=60)
    if response.status_code == 200:
        return Image.open(BytesIO(response.content))
    raise GenerationError(f"Stability AI error {response.status_code}: {response.text[:300]}")


def _closest_aspect_ratio(width: int, height: int) -> str:
    ratio = width / height
    options = {
        "1:1": 1.0, "16:9": 16 / 9, "9:16": 9 / 16,
        "4:3": 4 / 3, "3:4": 3 / 4,
    }
    return min(options, key=lambda k: abs(options[k] - ratio))


def generate_image(prompt: str, engine: str, width: int = 1024, height: int = 1024) -> Image.Image:
    """Dispatch to the selected engine."""
    if engine in HF_MODELS:
        return _generate_hf(prompt, engine, width, height)
    elif engine.startswith("Stability AI"):
        return _generate_stability(prompt, width, height)
    else:
        raise GenerationError(f"Unknown engine: {engine}")
