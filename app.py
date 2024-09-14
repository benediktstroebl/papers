import streamlit as st
import os
from paperqa import Docs, Settings, ask
import shutil

# Define the directory to save uploaded papers
UPLOAD_DIR = "./"

# Ensure the upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Initialize Docs with existing papers in the upload directory
@st.cache_resource
def initialize_docs():
    docs = Docs()
    for filename in os.listdir(UPLOAD_DIR):
        if filename.endswith(".pdf"):
            file_path = os.path.join(UPLOAD_DIR, filename)
            try:
                docs.add(file_path, docname=filename, title="test")
            except Exception as e:
                st.error(f"Error loading {filename}: {str(e)}")
    return docs

# Initialize session state
if 'docs' not in st.session_state:
    st.session_state.docs = initialize_docs()

st.title("PaperQA")

# File uploader
uploaded_files = st.file_uploader("Upload PDF papers", type="pdf", accept_multiple_files=True)

if uploaded_files:
    for uploaded_file in uploaded_files:
        # Save the uploaded file to the server
        file_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getvalue())

        # Add the document to the Docs object
        try:
            st.session_state.docs.add(file_path, docname=uploaded_file.name)
            st.success(f"Successfully added {uploaded_file.name}")
        except Exception as e:
            st.error(f"Error adding {uploaded_file.name}: {str(e)}")
            # Remove the file if it couldn't be added to Docs
            os.remove(file_path)

# Question input
question = st.text_input("Ask a question about the uploaded papers:")

settings = Settings()
settings.llm = "gpt-4o-mini"
settings.summary_llm = "gpt-4o-mini"

if question:
    if st.session_state.docs.docs:
        with st.spinner("Generating answer..."):
            answer = st.session_state.docs.query(question, settings=settings)
        st.write("Answer:", answer.formatted_answer)
    else:
        st.warning("Please upload some papers before asking questions.")

# Display current papers
if st.session_state.docs.docs:
    st.subheader("Papers in corpus:")
    for doc in st.session_state.docs.docs:
        st.write(f"- {st.session_state.docs.docs[doc].citation}")
else:
    st.info("No papers uploaded yet.")

