import streamlit as st
import pandas as pd
from utils import database

def show_book_management():
    """Displays the book management page."""
    st.header("📚 Book Management")

    books_df = database.load_books()

    st.subheader("Current Book Catalog")
    if books_df.empty:
        st.info("The book catalog is currently empty.")
    else:
        # Display the dataframe - make it non-editable for viewing
        st.dataframe(books_df, use_container_width=True, hide_index=True)

    st.divider()

    st.subheader("Add New Book")
    with st.form("add_book_form", clear_on_submit=True):
        title = st.text_input("Title", key="add_title")
        author = st.text_input("Author", key="add_author")
        genre = st.text_input("Genre", key="add_genre")
        submitted = st.form_submit_button("Add Book")

        if submitted:
            if title and author and genre:
                if database.add_book(title, author, genre):
                    st.success(f"Book '{title}' added successfully!")
                    # No need to rerun here, load_books() will be called again on next interaction
                    # or could force rerun if immediate table update is critical: st.rerun()
                else:
                    st.error("Failed to add book. Check logs.")
            else:
                st.warning("Please fill in all book details.")

    # Placeholder for Edit/Delete functionality
    st.subheader("Edit/Delete Books (Not Implemented)")
    st.info("Functionality to edit or delete books is not included in this POC version.")