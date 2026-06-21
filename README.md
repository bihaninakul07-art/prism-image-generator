# 🔮 Prism — AI Image Generator

A colorful, deployable Streamlit web app that turns text prompts into AI-generated images, with style presets, a choice of generation engines, and a full prompt-history gallery.

## What the project does

Users type a prompt, pick a visual style (Anime, Cyberpunk, Photorealistic, Watercolor, Pixel Art), choose a generation engine, and hit Generate. The app rewrites the prompt with style-specific keywords, calls the selected image API, displays the result, and keeps a running gallery of everything generated this session. It also supports multiple images per click, different aspect ratios, a one-click random prompt idea generator, and a light/dark theme toggle.

**Generation engines:**
1. **Hugging Face — Flux Schnell** (`black-forest-labs/FLUX.1-schnell`) — free, no billing setup, just a Hugging Face token. This is the recommended default.
2. **Stability AI — Stable Image Core** — paid, requires your own Stability AI API key and account credits.

## Project structure

```
image-gen-bot/
├── app.py              # Streamlit UI only
├── api_handler.py       # All API calls (Hugging Face / Stability AI)
├── prompts.py            # Style conditioning, random prompt ideas
├── requirements.txt
├── .env.example          # Template — copy to .env, no real keys committed
├── .gitignore             # Ignores .env, venv, caches
└── README.md
```

## How to run it locally

1. Clone this repository and `cd` into it.
2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Add your API key(s) (see below).
5. Run the app:
   ```bash
   streamlit run app.py
   ```

## How to add your API key(s)

1. Copy the template: `cp .env.example .env`
2. Open `.env` and paste in your key(s):
   - **Hugging Face (required for the free engine):** get a token at https://huggingface.co/settings/tokens → "New token" → Read access is enough.
     ```
     HF_TOKEN="hf_xxxxxxxxxxxxxxxxxxxx"
     ```
   - **Stability AI (optional, only needed if you use that engine):** get a key at https://platform.stability.ai/account/keys.
     ```
     STABILITY_KEY="sk-xxxxxxxxxxxxxxxxxxxx"
     ```
3. `.env` is listed in `.gitignore`, so it is never committed or pushed to GitHub.

## How to deploy it

1. Push the code to a public GitHub repository (`.env` will not be included).
2. Log into [Streamlit Community Cloud](https://share.streamlit.io).
3. Click **New app**, point it at your repo, branch, and `app.py`.
4. Before deploying, open **Advanced settings → Secrets** and paste:
   ```toml
   HF_TOKEN = "hf_xxxxxxxxxxxxxxxxxxxx"
   STABILITY_KEY = "sk-xxxxxxxxxxxxxxxxxxxx"
   ```
   (Omit the Stability line if you're not using that engine.)
5. Click **Deploy**.

## Known limitation

The Hugging Face Inference API can take 10–20 seconds to "warm up" on the first request after idling (a cold start), occasionally returning a 503 that the app automatically retries. The Stability AI engine requires its own separate paid API key and account credits — it is not free.
