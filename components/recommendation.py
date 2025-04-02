import streamlit as st
import pandas as pd
from utils import database

def show_recommendation_page():
    """Displays a basic recommendation page (placeholder)."""
    st.header("💡 Book Recommendations")
    st.info("This is a basic recommendation placeholder.")

    books_df = database.load_books()

    if books_df.empty:
        st.warning("No books available in the catalog to provide recommendations.")
        return

    # --- Simple Recommendation Logic ---
    # Example 1: Recommend books from a popular genre (e.g., Science Fiction)
    st.subheader("Popular Genre: Science Fiction")
    sf_books = books_df[books_df['genre'].str.contains("Science Fiction", case=False, na=False)]
    if not sf_books.empty:
        # Display a few randomly or the first few
        st.dataframe(sf_books.head(3), hide_index=True, use_container_width=True)
    else:
        st.write("No Science Fiction books found.")

    st.divider()

    # Example 2: Recommend recently added books (highest IDs)
    st.subheader("Recently Added Books")
    recent_books = books_df.sort_values(by='id', ascending=False).head(3)
    if not recent_books.empty:
         st.dataframe(recent_books, hide_index=True, use_container_width=True)
    else:
         st.write("No books to show.")