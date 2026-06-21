"""
Prompt engineering logic: style conditioning and the random prompt
generator (bonus feature).
"""
import random

# --- Style-conditioned prompt suffixes -------------------------------------
STYLES = {
    "None": "",
    "Anime": "anime style, detailed, vibrant colors, studio ghibli, masterpiece",
    "Cyberpunk": "cyberpunk, neon lights, futuristic, highly detailed, dark sci-fi",
    "Photorealistic": "photorealistic, 8k resolution, highly detailed, realistic lighting, octane render",
    "Watercolor": "watercolor painting, soft pastel tones, paper texture, delicate brush strokes",
    "Pixel Art": "pixel art, 16-bit, retro game sprite, crisp pixels, limited color palette",
}

RANDOM_PROMPTS = [
    "A futuristic Indian city at night with flying autorickshaws",
    "A tiger reading a newspaper in a cafe",
    "An ancient library floating in the clouds",
    "A robot tending a rooftop garden at sunset",
    "A bioluminescent forest with glowing mushrooms",
    "A steampunk train crossing a canyon bridge",
    "A cozy bookstore inside a giant tree trunk",
    "An astronaut painting a mural on the moon",
    "A market street in Old Delhi reimagined in space",
    "A dragon curled up asleep on a pile of vintage books",
    "A lighthouse on a cliff during a meteor shower",
    "A samurai cat guarding a sushi restaurant",
]


def apply_style(prompt: str, style: str) -> str:
    """Append style keywords to the user's raw prompt."""
    suffix = STYLES.get(style, "")
    if not suffix:
        return prompt
    return f"{prompt}, {suffix}"


def random_prompt() -> str:
    return random.choice(RANDOM_PROMPTS)
