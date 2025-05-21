import os
from textwrap import TextWrapper

import streamlit as st

from dewey.constants import (
    dewey_image_path,
    github_image_path,
    patreon_image_path,
)
from dewey.functions import split_files, vectorize_documents, answer

# ── API keys ────────────────────────────────────────────────────────────────
os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
os.environ["PINECONE_API_KEY"] = st.secrets["PINECONE_API_KEY"]

# optional: still respected by Pinecone client v6+
os.environ["PINECONE_API_ENV"] = st.secrets.get("PINECONE_API_ENV", "us-west-2")

# ── Streamlit layout tweaks ────────────────────────────────────────────────
st.set_page_config(
    page_title="dewey",
    page_icon="📖",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
        section[data-testid="stSidebar"] .css-ng1t4o {width: 14rem;}
        section[data-testid="stSidebar"] .css-1d391kg {width: 14rem;}
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Sidebar nav ─────────────────────────────────────────────────────────────
with st.sidebar:
    main_page = st.button("dewey", use_container_width=True)
    about_page = st.button("About", use_container_width=True)
    if not about_page:
        main_page = True

# ── Main page ───────────────────────────────────────────────────────────────
if main_page:
    cola, colb = st.columns([2, 9])
    cola.markdown(
        f'<a href="https://dewey-ai.streamlit.app/" target="_self">'
        f'<img src="{dewey_image_path}" width="100%" height="100%"></a>',
        unsafe_allow_html=True,
    )
    colb.markdown("# dewey \nAn AI Text Reference")

    uploader = st.empty()
    files = uploader.file_uploader(
        "files",
        type="pdf",
        accept_multiple_files=True,
        label_visibility="hidden",
    )

    if files:
        uploader.empty()

        documents = split_files(files)
        docsearch, chain = vectorize_documents(documents, len(documents))

        query = st.text_input(
            "Query", placeholder="Ask your question here!", label_visibility="hidden"
        )
        if query:
            st.write("---")
            docs, response = answer(query, docsearch, chain)

            st.code(TextWrapper(width=75).fill(response), language="markdown")
            with st.expander("See References"):
                for d in docs:
                    st.write("---")
                    st.write(f'**{d.metadata["source file"]}**')
                    st.write(d.page_content)

    else:
        # clear cached vector store when user removes uploads
        st.cache_resource.clear()

# ── About page ──────────────────────────────────────────────────────────────
if about_page:
    st.markdown("# About \n")
    st.write(
        "Built by [Erick Martinez](https://github.com/erickfm) using "
        "OpenAI, LangChain, and Streamlit. Art by me.\n\n"
        "Named after Melvil dewey, inventor of the "
        "[dewey Decimal System](https://en.wikipedia.org/wiki/Dewey_Decimal_Classification).\n\n"
        "Model is tuned for slight variety in answers.\n\n"
        "Please don't spam dewey—it costs me money 🤕"
    )
    st.markdown(
        f'<div>'
        f'<a href="https://github.com/erickfm/Dewey"><img src="{github_image_path}" width="6%" style="padding-right:10px;"></a>'
        f'<a href="https://www.patreon.com/ErickFMartinez"><img src="{patreon_image_path}" width="6%" style="padding-right:10px;"></a>'
        f"</div>",
        unsafe_allow_html=True,
    )
