"""
AI Image Generator — Streamlit frontend.
UI only. All generation logic lives in api_handler.py, all prompt logic in prompts.py.
"""
import io
import streamlit as st
from PIL import Image

from api_handler import generate_image, GenerationError, ENGINES
from prompts import apply_style, random_prompt, STYLES

st.set_page_config(page_title="Prism — AI Image Generator", page_icon="🔮", layout="wide")

# ---------------------------------------------------------------------------
# Session state (theme must be read before CSS is injected)
# ---------------------------------------------------------------------------
if "history" not in st.session_state:
    st.session_state.history = []
if "prompt_text" not in st.session_state:
    st.session_state.prompt_text = "A futuristic Indian city at night"
if "light_mode" not in st.session_state:
    st.session_state.light_mode = False

# ---------------------------------------------------------------------------
# Theme — a deliberate "ink + neon prism" palette, with a real light variant
# ---------------------------------------------------------------------------
if st.session_state.light_mode:
    palette = """
    :root {
        --bg-deep: #faf8ff;
        --bg-panel: #f1ecff;
        --bg-card: #ffffff;
        --violet: #7c3aed;
        --magenta: #db2777;
        --cyan: #0891b2;
        --amber: #d97706;
        --lime: #65a30d;
        --text-soft: #251f3d;
    }
    .stApp {
        background:
            radial-gradient(circle at 10% 0%, rgba(124, 58, 237, 0.12) 0%, transparent 45%),
            radial-gradient(circle at 90% 15%, rgba(219, 39, 119, 0.10) 0%, transparent 45%),
            radial-gradient(circle at 50% 100%, rgba(8, 145, 178, 0.08) 0%, transparent 50%),
            var(--bg-deep);
        color: var(--text-soft);
    }
    """
else:
    palette = """
    :root {
        --bg-deep: #120e24;
        --bg-panel: #1d1838;
        --bg-card: #241d47;
        --violet: #a78bfa;
        --magenta: #f472b6;
        --cyan: #22d3ee;
        --amber: #fbbf24;
        --lime: #a3e635;
        --text-soft: #f1eefc;
    }
    .stApp {
        background:
            radial-gradient(circle at 10% 0%, rgba(167, 139, 250, 0.25) 0%, transparent 45%),
            radial-gradient(circle at 90% 15%, rgba(244, 114, 182, 0.20) 0%, transparent 45%),
            radial-gradient(circle at 50% 100%, rgba(34, 211, 238, 0.15) 0%, transparent 50%),
            var(--bg-deep);
        color: var(--text-soft);
    }
    """

st.markdown(f"""
<style>
{palette}

h1, h2, h3 {{ font-family: 'Georgia', serif; letter-spacing: 0.3px; }}

/* Force every native Streamlit text element onto the theme color.
   Streamlit's own stylesheet loads after ours and otherwise keeps
   light/white text even when our background turns white. */
.stApp, .stApp p, .stApp span, .stApp label, .stApp li,
.stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6,
[data-testid="stMarkdownContainer"],
[data-testid="stMarkdownContainer"] *,
[data-testid="stWidgetLabel"],
[data-testid="stWidgetLabel"] *,
[data-testid="stCaptionContainer"],
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {{
    color: var(--text-soft) !important;
}}

.prism-hero {{
    background: linear-gradient(120deg, rgba(167,139,250,0.22), rgba(244,114,182,0.18), rgba(34,211,238,0.16));
    border: 1px solid rgba(167, 139, 250, 0.4);
    border-radius: 18px;
    padding: 1.6rem 1.8rem;
    margin-bottom: 1.4rem;
}}
.prism-title {{
    font-size: 2.6rem;
    font-weight: 800;
    background: linear-gradient(90deg, var(--cyan), var(--violet), var(--magenta), var(--amber));
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
    margin-bottom: 0;
}}
.prism-sub {{ color: var(--text-soft); opacity: 0.75; font-size: 1.05rem; margin-top: 0.3rem; }}

/* Buttons */
div.stButton > button {{
    background: linear-gradient(90deg, var(--violet), var(--magenta));
    color: #ffffff !important; border: none; border-radius: 10px;
    padding: 0.6rem 1.4rem; font-weight: 600;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}}
div.stButton > button:hover {{
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(139, 92, 246, 0.45);
}}
div.stDownloadButton > button {{
    background: linear-gradient(90deg, var(--cyan), var(--lime));
    color: #0d1117 !important; border: none; border-radius: 10px; font-weight: 700;
}}

/* Sidebar */
[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, var(--bg-panel) 0%, var(--bg-deep) 100%);
    border-right: 1px solid rgba(167, 139, 250, 0.3);
}}
[data-testid="stSidebar"] h3 {{
    color: var(--cyan) !important;
}}

/* Inputs */
.stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] > div {{
    background: var(--bg-card) !important;
    color: var(--text-soft) !important;
    border: 1px solid rgba(167, 139, 250, 0.45) !important;
    border-radius: 8px !important;
}}
.stTextInput input:focus, .stTextArea textarea:focus {{
    border: 1px solid var(--cyan) !important;
    box-shadow: 0 0 0 1px var(--cyan) !important;
}}

/* Radio buttons styled as colorful pills */
div[role="radiogroup"] label {{
    background: var(--bg-card);
    border: 1px solid rgba(167, 139, 250, 0.4);
    border-radius: 999px;
    padding: 0.35rem 0.9rem;
    margin: 0.15rem 0.3rem 0.15rem 0;
    transition: border-color 0.15s ease, background 0.15s ease;
}}
div[role="radiogroup"] label:hover {{
    border-color: var(--magenta);
}}
div[data-baseweb="radio"] label {{ color: var(--text-soft) !important; }}

/* Slider */
div[data-testid="stSlider"] [role="slider"] {{
    background-color: var(--magenta) !important;
}}
div[data-testid="stSlider"] > div > div > div > div {{
    background: linear-gradient(90deg, var(--cyan), var(--magenta)) !important;
}}

/* Toggle / checkbox accents */
[data-testid="stCheckbox"] label, [data-testid="stToggle"] label {{ color: var(--text-soft); }}

/* Expander */
.streamlit-expanderHeader, [data-testid="stExpander"] summary {{
    background: var(--bg-card) !important;
    border-radius: 10px !important;
    color: var(--amber) !important;
}}

/* Alert boxes */
div[data-testid="stAlert"] {{
    border-radius: 10px;
    border: 1px solid rgba(167, 139, 250, 0.4);
}}

/* Image frames */
[data-testid="stImage"] img {{
    border-radius: 14px;
    border: 1px solid rgba(167, 139, 250, 0.35);
    box-shadow: 0 4px 24px rgba(167, 139, 250, 0.15);
}}

.mode-badge {{
    display: inline-block; padding: 0.2rem 0.7rem; border-radius: 999px;
    background: linear-gradient(90deg, rgba(167,139,250,0.3), rgba(244,114,182,0.3));
    border: 1px solid var(--violet);
    font-size: 0.78rem; color: var(--cyan) !important; margin-bottom: 0.5rem; font-weight: 600;
}}

hr {{ border-color: rgba(167, 139, 250, 0.25); }}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.markdown(
    '<div class="prism-hero">'
    '<div class="prism-title">🔮 Prism — AI Image Generator</div>'
    '<div class="prism-sub">Type an idea, pick a style, and watch it render.</div>'
    '</div>',
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Sidebar — mode + settings
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### ⚙️ Engine")
    engine = st.radio(
        "Choose an engine:",
        ENGINES,
        help="Hugging Face is free with just a HF_TOKEN. Stability AI needs its own paid STABILITY_KEY in .env.",
    )

    st.markdown("### 🖼️ Image size")
    size_label = st.selectbox(
        "Aspect / size",
        ["Square (1024×1024)", "Portrait (1024×1792)", "Landscape (1792×1024)"],
    )
    size_map = {
        "Square (1024×1024)": (1024, 1024),
        "Portrait (1024×1792)": (1024, 1792),
        "Landscape (1792×1024)": (1792, 1024),
    }
    width, height = size_map[size_label]

    st.markdown("### 🎚️ Batch")
    num_images = st.slider("Number of images", 1, 4, 1)

    st.toggle("🌗 Light mode", key="light_mode",
              help="Switches the whole app between dark and light palettes.")

# ---------------------------------------------------------------------------
# Main controls
# ---------------------------------------------------------------------------
def _fill_random_prompt():
    # Safe to set session_state here: callbacks run BEFORE the widgets
    # below are re-instantiated on the next script run, so this doesn't
    # collide with the text_input's own ownership of the key.
    st.session_state.prompt_text = random_prompt()

col_a, col_b = st.columns([3, 1])
with col_a:
    prompt = st.text_input("Describe the image you want:", key="prompt_text")
with col_b:
    st.write("")
    st.write("")
    st.button("🎲 Random idea", on_click=_fill_random_prompt)

style = st.radio("Choose a style:", list(STYLES.keys()), horizontal=True)

generate_clicked = st.button("✨ Generate Image", type="primary")

# ---------------------------------------------------------------------------
# Generation
# ---------------------------------------------------------------------------
if generate_clicked:
    if not prompt.strip():
        st.warning("Please enter a prompt first.")
    else:
        final_prompt = apply_style(prompt, style)

        progress_box = st.empty()
        results = []
        for i in range(num_images):
            progress_box.info(f"Generating image {i + 1} of {num_images} with **{engine}**…")
            try:
                img = generate_image(final_prompt, engine, width=width, height=height)
                results.append(img)
            except GenerationError as e:
                st.error(str(e))
                break
            except Exception as e:
                st.error(f"Unexpected error: {e}")
                break
        progress_box.empty()

        for img in results:
            st.image(img, caption=final_prompt, use_container_width=True)
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            st.download_button(
                "⬇️ Download image",
                data=buf.getvalue(),
                file_name="prism_generated.png",
                mime="image/png",
                key=f"dl_{len(st.session_state.history)}_{id(img)}",
            )
            st.session_state.history.append({
                "prompt": final_prompt,
                "style": style,
                "engine": engine,
                "image": img,
            })

# ---------------------------------------------------------------------------
# Gallery / history (bonus feature)
# ---------------------------------------------------------------------------
if st.session_state.history:
    st.divider()
    st.subheader("🖼️ Recent generations")
    cols = st.columns(3)
    for idx, item in enumerate(reversed(st.session_state.history)):
        with cols[idx % 3]:
            st.markdown(f'<span class="mode-badge">{item["style"]} · {item["engine"].split("(")[0].strip()}</span>',
                        unsafe_allow_html=True)
            st.image(item["image"], caption=item["prompt"], use_container_width=True)

    if st.button("🗑️ Clear history"):
        st.session_state.history = []
        st.rerun()
