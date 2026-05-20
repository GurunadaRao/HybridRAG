from __future__ import annotations

import requests
import streamlit as st


DEFAULT_API_BASE_URL = "http://127.0.0.1:8000"
DEFAULT_INGEST_PATH = "/api/ingest/"


st.set_page_config(
    page_title="HybridRAG Ingestion Dashboard",
    page_icon="📥",
    layout="wide",
)


st.markdown(
    """
    <style>
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 1180px;
        }
        .hero {
            padding: 1.5rem 1.75rem;
            border-radius: 22px;
            background: linear-gradient(135deg, rgba(14, 18, 36, 0.98), rgba(25, 33, 58, 0.94));
            color: white;
            border: 1px solid rgba(255, 255, 255, 0.08);
            box-shadow: 0 18px 50px rgba(0, 0, 0, 0.18);
            margin-bottom: 1.25rem;
        }
        .hero h1 {
            margin-bottom: 0.35rem;
            font-size: 2.2rem;
        }
        .hero p {
            margin: 0;
            color: rgba(255, 255, 255, 0.8);
            font-size: 1rem;
        }
        .panel {
            padding: 1rem 1.1rem;
            border-radius: 16px;
            border: 1px solid rgba(128, 128, 128, 0.18);
            background: rgba(255, 255, 255, 0.72);
            backdrop-filter: blur(12px);
        }
        .hint {
            color: #556;
            font-size: 0.95rem;
            line-height: 1.5;
        }
        .small-title {
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: #667;
            margin-bottom: 0.25rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


st.markdown(
    """
    <div class="hero">
        <h1>HybridRAG Ingestion Dashboard</h1>
        <p>Upload files here to send them into the ingestion pipeline. The backend will normalize the text,
        chunk it, and store the output based on the active mode.</p>
    </div>
    """,
    unsafe_allow_html=True,
)


with st.sidebar:
    st.header("Connection")
    api_base_url = st.text_input("API base URL", value=DEFAULT_API_BASE_URL)
    ingest_path = st.text_input("Ingest path", value=DEFAULT_INGEST_PATH)
    st.caption("The UI posts selected files to the ingest endpoint using multipart form-data.")


left, right = st.columns([1.1, 0.9], gap="large")

with left:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="small-title">Upload</div>', unsafe_allow_html=True)
    uploaded_files = st.file_uploader(
        "Choose one or more files",
        type=["pdf", "json", "csv", "txt"],
        accept_multiple_files=True,
        help="PDF and JSON files are normalized into structured text before chunking.",
    )

    if uploaded_files:
        st.write("Selected files:")
        for file_item in uploaded_files:
            st.write(f"- {file_item.name} ({file_item.type or 'unknown content type'})")

    ingest_button = st.button("Ingest files", type="primary", use_container_width=True, disabled=not uploaded_files)
    st.markdown('</div>', unsafe_allow_html=True)


with right:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="small-title">What happens</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="hint">
        1. The backend clears the previous ingestion state first.
        <br />
        2. Each upload is normalized into structured text.
        <br />
        3. The document, chunks, and embeddings are then written to the active storage mode.
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown('</div>', unsafe_allow_html=True)


if ingest_button and uploaded_files:
    url = f"{api_base_url.rstrip('/')}/{ingest_path.lstrip('/')}"
    files = []
    for file_item in uploaded_files:
        file_bytes = file_item.getvalue()
        files.append(("files", (file_item.name, file_bytes, file_item.type or "application/octet-stream")))

    with st.spinner("Sending uploads to the ingestion pipeline..."):
        try:
            response = requests.post(url, files=files, timeout=300)
            response.raise_for_status()
            payload = response.json()
            st.success("Ingestion request completed")
            st.subheader("API response")
            st.json(payload)

            document_ids = payload.get("document_ids", [])
            local_artifacts = payload.get("local_artifacts", [])

            if document_ids:
                st.subheader("Stored document IDs / paths")
                for item in document_ids:
                    st.code(str(item), language="text")

            # allow fetching chunks from the API (useful when running with Mongo mode)
            if document_ids:
                if st.button("Fetch chunks from API for saved documents"):
                    for doc_id in document_ids:
                        try:
                            resp = requests.post(f"{api_base_url.rstrip('/')}/{'api/chunk'.lstrip('/')}/", json={"document_id": doc_id}, timeout=60)
                            if resp.status_code == 200:
                                data = resp.json()
                                st.markdown(f"### Chunks for document {doc_id}")
                                chunks = data.get("chunks", [])
                                st.write(f"Returned {len(chunks)} chunks (source: {data.get('source')})")
                                with st.expander(f"Show chunks for {doc_id}"):
                                    for i, c in enumerate(chunks[:10]):
                                        st.markdown(f"**#{i}**")
                                        st.code(c if isinstance(c, str) else (c.get('text') if isinstance(c, dict) else str(c)), language="text")
                            else:
                                st.error(f"Failed to fetch chunks for {doc_id}: {resp.status_code} {resp.text}")
                        except Exception as e:
                            st.error(f"Error fetching chunks for {doc_id}: {e}")

            if local_artifacts:
                st.subheader("Local normalized output")
                preview_count = st.number_input("Chunks preview count", min_value=1, max_value=50, value=5)
                for artifact in local_artifacts:
                    st.markdown("---")
                    st.markdown(f"**Artifact:** `{artifact}`")
                    # artifact is expected to contain 'chunks' and 'embeddings' paths for local mode
                    chunks_path = artifact.get("chunks") if isinstance(artifact, dict) else None
                    contextual_chunks_path = artifact.get("contextual_chunks") if isinstance(artifact, dict) else None
                    embeddings_path = artifact.get("embeddings") if isinstance(artifact, dict) else None

                    if chunks_path:
                        st.markdown(f"**Chunks file:** {chunks_path}")
                        try:
                            import json

                            with open(chunks_path, "r", encoding="utf-8") as fh:
                                chunk_list = json.load(fh)

                            st.write(f"Total chunks: {len(chunk_list)}")
                            # show a small preview
                            with st.expander("Preview chunks"):
                                for idx, chunk in enumerate(chunk_list[:preview_count]):
                                    st.markdown(f"**#{idx}**")
                                    if isinstance(chunk, dict):
                                        text = chunk.get("text") or chunk.get("chunk_text") or str(chunk)
                                    else:
                                        text = str(chunk)
                                    st.code(text[:1000], language="text")

                                if len(chunk_list) > preview_count:
                                    st.write(f"...and {len(chunk_list)-preview_count} more chunks")

                            # allow user to view the full chunks JSON
                            if st.checkbox(f"Show raw chunks JSON for {chunks_path}"):
                                st.json(chunk_list)

                        except FileNotFoundError:
                            st.warning(f"Chunks file not found on disk: {chunks_path}")
                        except Exception as e:
                            st.error(f"Failed to read chunks file: {e}")

                    if contextual_chunks_path:
                        st.markdown(f"**Contextual chunks file:** {contextual_chunks_path}")
                        if st.checkbox(f"Show contextual chunks JSON for {contextual_chunks_path}"):
                            try:
                                import json

                                with open(contextual_chunks_path, "r", encoding="utf-8") as fh:
                                    contextual_chunks = json.load(fh)
                                st.json(contextual_chunks)
                            except Exception as e:
                                st.error(f"Failed to read contextual chunks file: {e}")

                    if embeddings_path:
                        st.markdown(f"**Embeddings file:** {embeddings_path}")
                        if st.checkbox(f"Show embeddings JSON for {embeddings_path}"):
                            try:
                                import json

                                with open(embeddings_path, "r", encoding="utf-8") as fh:
                                    emb = json.load(fh)
                                st.json(emb)
                            except Exception as e:
                                st.error(f"Failed to read embeddings file: {e}")

        except requests.RequestException as exc:
            st.error(f"Failed to reach the ingest endpoint: {exc}")
        except ValueError:
            st.error("The API did not return valid JSON.")


st.divider()
st.caption("Run this app from the dashboard folder with: streamlit run streamlit_app.py")
