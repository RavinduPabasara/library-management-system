import streamlit as st
import pandas as pd
from utils import database
from utils.rag_engine import query_rag

def show_search_page(qa_chain):
    """Displays the search page with options for book search and RAG query."""
    st.header("🔍 Search")

    tab1, tab2 = st.tabs(["Search Books (Catalog)", "Query Documents (RAG)"])

    with tab1:
        st.subheader("Search Books in Catalog")
        books_df = database.load_books()

        if books_df.empty:
            st.info("Book catalog is empty. Nothing to search.")
        else:
            search_term = st.text_input("Search by Title, Author, or Genre", key="book_search_term")

            if search_term:
                # Simple search across relevant columns (case-insensitive)
                mask = (
                    books_df['title'].str.contains(search_term, case=False, na=False) |
                    books_df['author'].str.contains(search_term, case=False, na=False) |
                    books_df['genre'].str.contains(search_term, case=False, na=False)
                )
                results_df = books_df[mask]

                if not results_df.empty:
                    st.write(f"Found {len(results_df)} matching book(s):")
                    st.dataframe(results_df, use_container_width=True, hide_index=True)
                else:
                    st.info("No books found matching your search term.")
            else:
                st.info("Enter a term above to search the book catalog.")


    with tab2:
        st.subheader("Ask Questions About Library Documents (RAG)")

        if qa_chain is None:
            st.warning("The RAG engine is not available. This might be due to missing documents, configuration errors, or API key issues. Check application logs.")
        else:
            rag_query = st.text_input("Enter your question about library rules, AI research, history, etc.", key="rag_query")

            if st.button("Ask RAG Engine"):
                if rag_query:
                    answer, source_docs = query_rag(qa_chain, rag_query)
                    st.markdown("#### Answer:")
                    st.markdown(answer)

                    if source_docs:
                        with st.expander("Show Source Document Chunks"):
                             for i, doc in enumerate(source_docs):
                                 st.markdown(f"**Source {i+1}:**")
                                 # Displaying metadata if available, e.g., filename
                                 if 'source' in doc.metadata:
                                     st.caption(f"From: {doc.metadata['source']}")
                                 st.text_area(f"Content Chunk {i+1}", value=doc.page_content, height=150, key=f"src_doc_{i}", disabled=True)
                else:
                    st.warning("Please enter a question.")