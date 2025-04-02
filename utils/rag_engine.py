# utils/rag_engine.py

import os
import logging
import streamlit as st
# Updated Langchain imports
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader, TextLoader # Use langchain_community
from langchain.chains import RetrievalQA
from utils.openai_utils import get_embeddings, get_llm
import config

logging.basicConfig(level=logging.INFO)

# Global variable for the vector store instance
_vector_store = None

def load_documents(docs_path):
    """Loads documents from the specified directory using appropriate loaders."""
    loaded_documents = []
    try:
        # Load TXT files explicitly
        txt_loader = DirectoryLoader(
            docs_path,
            glob="**/*.txt",
            loader_cls=TextLoader, # Explicitly use TextLoader
            loader_kwargs={'encoding': 'utf-8'}, # Specify encoding (common fix)
            use_multithreading=True,
            show_progress=True,
            recursive=True
        )
        txt_docs = txt_loader.load()
        if txt_docs:
            loaded_documents.extend(txt_docs)
            logging.info(f"Loaded {len(txt_docs)} TXT documents.")
        else:
            logging.warning(f"No TXT documents found in {docs_path}")

        # Load PDF files explicitly
        pdf_loader = DirectoryLoader(
            docs_path,
            glob="**/*.pdf",
            loader_cls=PyPDFLoader, # Explicitly use PyPDFLoader
            use_multithreading=True,
            show_progress=True,
            recursive=True
        )
        pdf_docs = pdf_loader.load()
        if pdf_docs:
            loaded_documents.extend(pdf_docs)
            logging.info(f"Loaded {len(pdf_docs)} PDF documents.")
        else:
            logging.warning(f"No PDF documents found in {docs_path}")

        # Add loaders for other types (e.g., .docx, .csv) here if needed

        if not loaded_documents:
            logging.warning(f"No documents found or loaded from {docs_path}")
            st.warning(f"No compatible documents (.txt, .pdf) were found in the '{config.DOCUMENTS_DIR.name}' directory.")
            return []

        logging.info(f"Total loaded {len(loaded_documents)} documents.")
        return loaded_documents

    except ImportError as ie:
         # Catch specific error if PyPDFLoader is used but pypdf isn't installed
         if 'pypdf' in str(ie).lower():
              logging.error(f"Import error loading PDFs: {ie}. Is 'pypdf' installed?")
              st.error("Failed to load PDF documents. Please install 'pypdf': pip install pypdf")
         else:
              logging.error(f"Import error during document loading: {ie}")
              st.error(f"A required library for document loading might be missing: {ie}")
         return []
    except Exception as e:
        # Catch other potential errors during loading
        logging.error(f"Error loading documents from {docs_path}: {e}", exc_info=True) # Log traceback
        st.error(f"Failed to load documents. Check files in '{config.DOCUMENTS_DIR.name}' and ensure required libraries (like 'pypdf' for PDFs) are installed. Error: {e}")
        return []


def split_documents(documents):
    """Splits documents into chunks."""
    if not documents:
        return []
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP,
        length_function=len,
    )
    chunks = text_splitter.split_documents(documents)
    logging.info(f"Split {len(documents)} documents into {len(chunks)} chunks.")
    return chunks

def create_vector_store(chunks, embeddings):
    """Creates and persists the FAISS vector store."""
    if not chunks:
        logging.warning("No chunks provided to create vector store.")
        return None
    if not embeddings:
        logging.error("Embeddings model not available for vector store creation.")
        st.error("Cannot create document index: Embeddings model is not available.")
        return None

    try:
        vector_store = FAISS.from_documents(chunks, embeddings)
        vector_store_path = str(config.VECTOR_STORE_DIR)
        vector_store.save_local(vector_store_path)
        logging.info(f"Vector store created and saved at {vector_store_path}")
        return vector_store
    except Exception as e:
        logging.error(f"Failed to create or save vector store: {e}", exc_info=True)
        st.error(f"Error creating the document index (vector store): {e}")
        return None

def load_vector_store(embeddings):
    """Loads the FAISS vector store from local storage."""
    if not embeddings:
        logging.error("Embeddings model not available for loading vector store.")
        st.error("Cannot load document index: Embeddings model is not available.")
        return None

    index_path = str(config.VECTOR_STORE_DIR)
    faiss_index_file = os.path.join(index_path, "index.faiss")
    faiss_pkl_file = os.path.join(index_path, "index.pkl")

    if not os.path.exists(faiss_index_file) or not os.path.exists(faiss_pkl_file):
         logging.warning(f"Vector store index files not found at {index_path}. Need to create it first.")
         return None
    try:
        # Allow dangerous deserialization for FAISS loading locally, accept the risk for this POC
        vector_store = FAISS.load_local(index_path, embeddings, allow_dangerous_deserialization=True)
        logging.info(f"Vector store loaded successfully from {index_path}")
        return vector_store
    except Exception as e:
        logging.error(f"Failed to load vector store from {index_path}: {e}", exc_info=True)
        st.error(f"Error loading existing document index. It might be corrupted or incompatible. Consider deleting the '{config.VECTOR_STORE_DIR.name}' folder and restarting. Error: {e}")
        # Clean up potentially corrupted files? Be cautious here.
        # try:
        #     if os.path.exists(faiss_index_file): os.remove(faiss_index_file)
        #     if os.path.exists(faiss_pkl_file): os.remove(faiss_pkl_file)
        # except OSError as ose:
        #     logging.error(f"Could not delete potentially corrupt index files: {ose}")
        return None

def get_retrieval_qa_chain(vector_store, llm):
    """Creates the RetrievalQA chain."""
    if not vector_store:
        logging.error("Vector store not available for QA chain.")
        # No need for st.error here, handled during initialization
        return None
    if not llm:
        logging.error("LLM not available for QA chain.")
        st.error("Cannot create RAG query engine: LLM is not available.")
        return None

    try:
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=vector_store.as_retriever(),
            return_source_documents=True
        )
        logging.info("RetrievalQA chain created.")
        return qa_chain
    except Exception as e:
        logging.error(f"Failed to create RetrievalQA chain: {e}", exc_info=True)
        st.error(f"Error setting up the RAG query engine: {e}")
        return None

def initialize_rag_engine():
    """Initializes the entire RAG engine: loads/creates vector store and QA chain."""
    global _vector_store
    # Reset vector store at start of initialization if needed
    # _vector_store = None

    embeddings = get_embeddings()
    llm = get_llm()

    if not embeddings or not llm:
        st.error("RAG Engine initialization failed: Cannot get OpenAI models/embeddings.")
        return None, None # Return None for both vector_store and qa_chain

    # Try loading existing vector store first
    _vector_store = load_vector_store(embeddings)

    if _vector_store is None:
        st.info("Building document index... (This may take a moment on first run)")
        logging.info("Attempting to build a new vector store.")
        # If loading failed or store doesn't exist, create it
        documents = load_documents(str(config.DOCUMENTS_DIR))
        if not documents:
            st.warning("No documents were loaded. RAG querying will be unavailable.")
            return None, None # No docs, no store, no chain
        else:
            chunks = split_documents(documents)
            if chunks:
                _vector_store = create_vector_store(chunks, embeddings)
                if _vector_store:
                    st.success("Document index built successfully!")
                else:
                    st.error("Failed to build the document index.")
                    # _vector_store remains None
            else:
                 st.warning("Documents were loaded but could not be split into chunks.")
                 # _vector_store remains None

    # Create QA chain if vector store is available *now*
    qa_chain = None
    if _vector_store:
        qa_chain = get_retrieval_qa_chain(_vector_store, llm)
        if not qa_chain:
             st.error("Failed to create RAG query engine even though index exists.")
             # Fallback: _vector_store might exist but chain creation failed.
    elif not os.path.exists(str(config.VECTOR_STORE_DIR)):
         # Only show this if we didn't just attempt/fail a build
         st.warning("RAG query engine not available: Document index needs to be built (check logs for errors).")

    return _vector_store, qa_chain # Return current state


def query_rag(qa_chain, query: str):
    """Queries the RAG engine."""
    if not qa_chain:
        logging.error("QA chain is not initialized for querying.")
        st.error("Error: RAG Query Engine is not ready. Cannot answer question.")
        return "Error: RAG Query Engine is not ready.", []

    try:
        with st.spinner("🧠 Thinking..."):
            # Ensure query is passed correctly if using invoke
            # result = qa_chain.invoke({"query": query}) # For newer LCEL chains
            result = qa_chain({"query": query}) # For older RetrievalQA chain type

        answer = result.get('result', "Sorry, I couldn't find an answer in the documents.")
        source_docs = result.get('source_documents', [])
        logging.info(f"RAG Query: '{query}', Answer: '{answer[:50]}...'")
        return answer, source_docs
    except Exception as e:
        logging.error(f"Error during RAG query execution: {e}", exc_info=True)
        st.error(f"An error occurred while processing your query: {e}")
        return "Error processing query.", []