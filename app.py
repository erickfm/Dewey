import streamlit as st
from Dewey.constants import dewey_image_path, github_image_path, patreon_image_path
from langchain.document_loaders import UnstructuredPDFLoader, OnlinePDFLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma, Pinecone
from langchain.embeddings.openai import OpenAIEmbeddings
import pinecone

import os

os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
os.environ["PINECONE_API_KEY"] = st.secrets["PINECONE_API_KEY"]
os.environ["PINECONE_API_ENV"] = st.secrets["PINECONE_API_ENV"]

st.set_page_config(page_title='Dewey', page_icon="📖", layout="centered", initial_sidebar_state='collapsed')
st.markdown(f'''
    <style>
        section[data-testid="stSidebar"] .css-ng1t4o {{width: 14rem;}}
        section[data-testid="stSidebar"] .css-1d391kg {{width: 14rem;}}
    </style>
''', unsafe_allow_html=True)

with st.sidebar:
    main_page = st.button('Dewey', use_container_width=1)
    about_page = st.button('About', use_container_width=1)
    if not about_page:
        main_page = True


def save_texts(texts):
    with open(texts.name, "wb") as f:
        f.write(texts.getbuffer())
    return texts.name


if main_page:
    cola, colb = st.columns([2,9])
    cola.markdown(
        f"""<a target="_self" href="{'https://dewey.streamlit.app/'}"><img src="{dewey_image_path}" style="display:block;" width="100%" height="100%"></a>""",
        unsafe_allow_html=1)
    colb.markdown('# Dewey \nAn AI Text Reference')
    temp = st.empty()
    texts = temp.file_uploader('Texts', 'pdf', accept_multiple_files=True, label_visibility='hidden')
    if texts:
        save_location = save_texts(texts[0])
        loader = PyPDFLoader(save_location)


        # file_like_obj = BytesIO(texts)
        # PyPDFParser()
        # lazy_parse(
        # loader = BSHTMLLoader(file_like_obj)
        data = loader.load()
        st.write(f'You have {len(data)} document(s) in your data')


        temp.empty()






        query = st.text_input('Query', 'Give me an overview', label_visibility='hidden')
        st.write(query)

if about_page:
    st.markdown('# About \n')
    st.write('Built by [Erick Martinez](https://github.com/erickfm) using OpenAI, LangChain, and Streamlit. Dewey icons by me'
             '\n\nModel is tuned for more variety in answers. ChatGPT is trained on data limited to September 2021.')
    st.markdown(f"""<div><a href="https://github.com/erickfm/Dewey"><img src="{github_image_path}" style="padding-right: 10px;" width="6%" height="6%"></a>
    <a href="https://www.patreon.com/ErickFMartinez"><img src="{patreon_image_path}" style="padding-right: 10px;" width="6%" height="6%"></a></div>""", unsafe_allow_html=1)
