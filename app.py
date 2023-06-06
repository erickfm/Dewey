import streamlit as st
from textwrap import TextWrapper
from Dewey.constants import dewey_image_path, github_image_path, patreon_image_path
from Dewey.functions import split_files, vectorize_documents, answer
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

if main_page:
    cola, colb = st.columns([2, 9])
    cola.markdown(
        f"""<a target="_self" href="{'https://dewey-ai.streamlit.app/'}"><img src="{dewey_image_path}" style="display:block;" width="100%" height="100%"></a>""",
        unsafe_allow_html=1)
    colb.markdown('# Dewey \nAn AI Text Reference')
    temp = st.empty()
    files = temp.file_uploader('files', 'pdf', accept_multiple_files=True, label_visibility='hidden')
    if files:
        temp.empty()
        documents = split_files(files)
        docsearch, chain = vectorize_documents(documents, len(documents))
        query = st.text_input('Query', placeholder='Ask your question here!', label_visibility='hidden')
        if query:
            st.write('---')
            docs, response = answer(query, docsearch, chain)
            wrapper = TextWrapper(width=75)
            st.code(wrapper.fill(response), language='markdown')
            st.write('')
            with st.expander("See References"):
                for doc in docs:
                    st.write('---')
                    st.write(f'**[{doc.metadata["source file"]}]({doc.metadata["source file"]})**')
                    st.write(doc.page_content)

if about_page:
    st.markdown('# About \n')
    st.write(
        "Built by [Erick Martinez](https://github.com/erickfm) using OpenAI, LangChain, and Streamlit. Art by me"
        "\n\nModel is tuned for slight variety in answers"
        "\n\nPlease don't spam Dewey, it costs me money 🤕")
    st.markdown(f"""<div><a href="https://github.com/erickfm/Dewey"><img src="{github_image_path}" style="padding-right: 10px;" width="6%" height="6%"></a>
    <a href="https://www.patreon.com/ErickFMartinez"><img src="{patreon_image_path}" style="padding-right: 10px;" width="6%" height="6%"></a></div>""",
                unsafe_allow_html=1)
