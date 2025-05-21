import os
import time
import uuid
from pathlib import Path
from typing import List, Tuple

import streamlit as st
from langchain.chains.question_answering import load_qa_chain          # still works – backwards-compatible :contentReference[oaicite:0]{index=0}
from langchain_openai import ChatOpenAI, OpenAIEmbeddings              # new import path :contentReference[oaicite:1]{index=1}
from langchain_community.document_loaders import PyPDFLoader          # new import path :contentReference[oaicite:2]{index=2}
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_pinecone import PineconeVectorStore                     # new vector store impl :contentReference[oaicite:3]{index=3}
from pinecone import Pinecone, ServerlessSpec

# ---------------------------------------------------------------------------#
# Helpers                                                                    #
# ---------------------------------------------------------------------------#
def _save_uploaded_file(temp_file) -> Path:
    """Persist uploaded PDF to disk so PyPDFLoader can read it."""
    dest = Path(temp_file.name)
    dest.write_bytes(temp_file.getbuffer())
    return dest


@st.cache_resource(show_spinner=False)
def split_files(files) -> List[dict]:
    """Split uploaded PDFs into LangChain Document chunks."""
    docs = []
    splitter = RecursiveCharacterTextSplitter(chunk_size=2_000, chunk_overlap=0)

    for f in files:
        with st.spinner(f"✂️ Splitting {f.name}…"):
            pdf_path = _save_uploaded_file(f)
            loader = PyPDFLoader(str(pdf_path))
            for chunk in splitter.split_documents(loader.load()):
                docs.append({"text": chunk, "filename": f.name})

    return docs


@st.cache_resource(show_spinner=False)
def vectorize_documents(_documents: List[dict], number_of_documents: int):
    """
    • Embeds chunks with OpenAI   → 1 536-D vectors
    • Ensures serverless index    → aws / us-east-1
    • Upserts into namespace 'docs'
    • Returns (vectorstore, qa_chain)
    """
    import uuid

    # ── Prepare data ────────────────────────────────────────────────────
    texts     = [d["text"].page_content for d in _documents]
    metadatas = [{"source file": d["filename"]} for d in _documents]

    with st.spinner("✨ Vectorizing documents…"):
        # ── Embeddings ---------------------------------------------------
        embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            api_key=os.environ["OPENAI_API_KEY"],
        )
        dims = len(embeddings.embed_query("dimension_check"))  # 1 536

        # ── Pinecone index ----------------------------------------------
        pc         = Pinecone(api_key=os.environ["PINECONE_API_KEY"])
        index_name = "dewey"
        spec       = ServerlessSpec(cloud="aws", region="us-east-1")

        if index_name in [idx.name for idx in pc.list_indexes().index_list["indexes"]]:
            info = pc.describe_index(index_name)
            if info.dimension != dims:
                pc.delete_index(index_name)

        if index_name not in [idx.name for idx in pc.list_indexes().index_list["indexes"]]:
            pc.create_index(
                name=index_name,
                dimension=dims,
                metric="cosine",
                spec=spec,
            )
        while not pc.describe_index(index_name).status["ready"]:
            time.sleep(1)

        # ── LangChain vector store --------------------------------------
        namespace   = "docs"
        vectorstore = PineconeVectorStore.from_existing_index(
            index_name=index_name,
            namespace=namespace,
            embedding=embeddings,
        )

        # safe-delete: ignore 404 if namespace not yet created
        try:
            vectorstore.delete(delete_all=True)
        except Exception:
            pass  # namespace didn't exist yet – that's fine

        vectorstore.add_texts(
            texts=texts,
            metadatas=metadatas,
            ids=[str(uuid.uuid4()) for _ in texts],
        )

        # ── QA chain -----------------------------------------------------
        llm   = ChatOpenAI(temperature=0.5, api_key=os.environ["OPENAI_API_KEY"])
        chain = load_qa_chain(llm, chain_type="stuff")

    return vectorstore, chain





def answer(query: str, _docsearch: PineconeVectorStore, _chain) -> Tuple[list, str]:
    """Retrieve similar chunks + synthesize answer."""
    with st.spinner("📚 Researching…"):
        docs = _docsearch.similarity_search(query, k=4)
    with st.spinner("🧠 Synthesizing…"):
        response = _chain.run(input_documents=docs, question=query).strip()
    return docs, response
