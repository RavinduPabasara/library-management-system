import os
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from dotenv import load_dotenv
import config
import streamlit as st
import logging

# Load environment variables from .env file
load_dotenv()

def get_openai_key():
    """Gets the OpenAI API key from environment variables."""
    api_key = config.OPENAI_API_KEY
    if not api_key or api_key == "sk-...":
        logging.error("OpenAI API Key not configured properly.")
        st.error("OpenAI API Key is missing or invalid. Please check your .env file.")
        return None
    return api_key

# Global instances (initialized once)
_openai_llm = None
_openai_embeddings = None

def get_llm():
    """Initializes and returns the OpenAI LLM instance."""
    global _openai_llm
    if _openai_llm is None:
        api_key = get_openai_key()
        if api_key:
            try:
                # You can customize the model name if needed, e.g., "gpt-4"
                _openai_llm = ChatOpenAI(openai_api_key=api_key, model_name="gpt-3.5-turbo")
                logging.info("OpenAI LLM initialized.")
            except Exception as e:
                logging.error(f"Failed to initialize OpenAI LLM: {e}")
                st.error(f"Failed to initialize OpenAI LLM. Check API key and network. Error: {e}")
                return None
        else:
            return None # API key error handled in get_openai_key
    return _openai_llm

def get_embeddings():
    """Initializes and returns the OpenAI Embeddings instance."""
    global _openai_embeddings
    if _openai_embeddings is None:
        api_key = get_openai_key()
        if api_key:
            try:
                 # You can choose different embedding models if desired
                _openai_embeddings = OpenAIEmbeddings(openai_api_key=api_key)
                logging.info("OpenAI Embeddings initialized.")
            except Exception as e:
                logging.error(f"Failed to initialize OpenAI Embeddings: {e}")
                st.error(f"Failed to initialize OpenAI Embeddings. Check API key and network. Error: {e}")
                return None
        else:
            return None # API key error handled in get_openai_key
    return _openai_embeddings

# Example of a direct call (though RAG engine will likely use the initialized instances)
def generate_summary(text: str) -> str:
    """Generates a summary of the given text using OpenAI."""
    llm = get_llm()
    if not llm:
        return "Error: LLM not available."

    try:
        prompt = f"Please provide a concise summary of the following text:\n\n{text}\n\nSummary:"
        response = llm.invoke(prompt) # Use invoke for newer LangChain versions
        return response.content # Access content attribute for the response string
    except Exception as e:
        logging.error(f"Error during OpenAI summary generation: {e}")
        st.error(f"An error occurred while generating the summary: {e}")
        return "Error generating summary."