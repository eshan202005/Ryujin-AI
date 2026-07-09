from pathlib import Path
import base64

import streamlit as st


# ==========================================================
# PATHS
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

ASSETS_DIR = BASE_DIR / "assets"

BACKGROUND_IMAGE = ASSETS_DIR / "background.jpg"

LOGO_IMAGE = ASSETS_DIR / "logo.png"

STYLE_DIR = BASE_DIR / "styles"


# ==========================================================
# CSS
# ==========================================================

def load_css():
    """
    Load every CSS file inside styles/.
    """

    css_order = [
        "theme.css",
        "layout.css",
        "sidebar.css",
        "chat.css",
        "input.css",
        "animations.css",
    ]

    css = ""

    for file in css_order:

        path = STYLE_DIR / file

        if path.exists():

            css += path.read_text(
                encoding="utf-8"
            )

            css += "\n"

    st.markdown(
        f"<style>{css}</style>",
        unsafe_allow_html=True,
    )


# ==========================================================
# IMAGE
# ==========================================================

def _image_to_base64(path: Path):

    with open(path, "rb") as img:

        return base64.b64encode(
            img.read()
        ).decode()


# ==========================================================
# BACKGROUND
# ==========================================================

def set_background():

    if not BACKGROUND_IMAGE.exists():
        return

    img = _image_to_base64(
        BACKGROUND_IMAGE
    )

    st.markdown(
        f"""
<style>

.stApp{{
background:
linear-gradient(
rgba(4,4,8,.82),
rgba(8,6,16,.90)
),
url("data:image/png;base64,{img}");

background-size:cover;
background-position:center;
background-repeat:no-repeat;
background-attachment:fixed;
}}

</style>
""",
        unsafe_allow_html=True,
    )


# ==========================================================
# LOGO
# ==========================================================

def show_logo(width=70):

    if LOGO_IMAGE.exists():

        st.image(
            LOGO_IMAGE,
            width=width,
        )

    else:

        st.write("🐉")