import streamlit as st
from dotenv import load_dotenv
import logging

# Import components and utils
from components import authentication, book_management, search, recommendation
from utils import rag_engine, database
import config # Ensure config is loaded early

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables from .env file FIRST
load_dotenv()

# --- Page Configuration (Optional but Recommended) ---
st.set_page_config(
    page_title="AI Library Assistant",
    page_icon="📚",
    layout="wide", # Can be "centered" or "wide"
    initial_sidebar_state="expanded" # Can be "auto", "expanded", "collapsed"
)

# --- Initialize RAG Engine ---
# Attempt to initialize the RAG engine once and store the QA chain in session state
# This avoids re-initializing on every interaction, especially the costly index build.
if 'rag_initialized' not in st.session_state:
    st.session_state['vector_store'], st.session_state['qa_chain'] = rag_engine.initialize_rag_engine()
    st.session_state['rag_initialized'] = True
    if st.session_state['qa_chain'] is None:
        logging.warning("RAG QA chain initialization failed or returned None.")
    else:
        logging.info("RAG QA chain initialized successfully.")

# --- Main Application Logic ---
def main():
    # Check login status
    if "logged_in" not in st.session_state or not st.session_state.logged_in:
        authentication.show_login_page()
    else:
        st.sidebar.success(f"Welcome, {st.session_state.get('username', 'User')}!")
        authentication.add_logout_button() # Add logout button to sidebar

        st.sidebar.title("Navigation")
        page_options = ["🏠 Home", "📚 Book Management", "🔍 Search & Query", "💡 Recommendations"]
        selection = st.sidebar.radio("Go to", page_options)

        st.sidebar.divider()
        st.sidebar.info(f"Document Index Status: {'Ready' if st.session_state.get('qa_chain') else 'Not Available'}")


        # Display the selected page
        if selection == "🏠 Home":
            st.title("Welcome to the AI-Powered Library Management System")
            st.markdown("""
            Use the sidebar to navigate through the different sections of the library system.
            - **Book Management:** View the catalog and add new books.
            - **Search & Query:** Find books in the catalog or ask questions about library documents using AI.
            - **Recommendations:** Get simple book recommendations.
            """)
            # Display some stats or featured content maybe?
            books_df = database.load_books()
            st.metric("Total Books in Catalog", len(books_df))


        elif selection == "📚 Book Management":
            book_management.show_book_management()

        elif selection == "🔍 Search & Query":
            # Pass the initialized QA chain to the search page
            qa_chain = st.session_state.get('qa_chain')
            search.show_search_page(qa_chain)

        elif selection == "💡 Recommendations":
            recommendation.show_recommendation_page()

# --- Run the App ---
if __name__ == "__main__":
    # Basic check for OpenAI API Key on startup
    if not config.OPENAI_API_KEY or config.OPENAI_API_KEY == "sk-...":
        st.error("CRITICAL: OpenAI API Key is not configured. Please set it in your `.env` file.")
        logging.critical("OpenAI API Key is missing or invalid. Application might not function correctly.")
        # You might want to prevent the app from fully starting here,
        # but for the POC, we let it load to show the error message.
    main()