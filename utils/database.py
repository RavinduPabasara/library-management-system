import pandas as pd
import config
import streamlit as st
import logging

logging.basicConfig(level=logging.INFO)

def load_users() -> pd.DataFrame:
    """Loads user data from the CSV file."""
    try:
        users_df = pd.read_csv(config.USERS_CSV_PATH)
        # Ensure required columns exist, handle potential missing columns gracefully
        if not all(col in users_df.columns for col in ['username', 'password', 'id']):
             logging.error(f"Users CSV ({config.USERS_CSV_PATH}) is missing required columns (id, username, password).")
             st.error("User database file is corrupted or missing required columns.")
             return pd.DataFrame(columns=['id', 'username', 'password']) # Return empty DataFrame
        return users_df
    except FileNotFoundError:
        logging.error(f"Users CSV file not found at {config.USERS_CSV_PATH}")
        st.error(f"User database file not found. Please ensure '{config.USERS_CSV_PATH}' exists.")
        # Create a dummy empty file or return an empty DataFrame?
        # For now, return empty DF to avoid crashing the app immediately
        return pd.DataFrame(columns=['id', 'username', 'password'])
    except pd.errors.EmptyDataError:
        logging.warning(f"Users CSV file is empty at {config.USERS_CSV_PATH}")
        return pd.DataFrame(columns=['id', 'username', 'password']) # Return empty DataFrame
    except Exception as e:
        logging.error(f"Error loading users CSV: {e}")
        st.error("An unexpected error occurred while loading user data.")
        return pd.DataFrame(columns=['id', 'username', 'password'])

def verify_user(users_df: pd.DataFrame, username, password) -> bool:
    """Verifies user credentials against the loaded DataFrame."""
    if users_df.empty:
        return False
    # WARNING: Plain text password comparison - HIGHLY INSECURE FOR PRODUCTION
    user_record = users_df[users_df['username'] == username]
    if not user_record.empty:
        # Compare plain text password
        return user_record.iloc[0]['password'] == password
    return False

def load_books() -> pd.DataFrame:
    """Loads book data from the CSV file."""
    try:
        books_df = pd.read_csv(config.BOOKS_CSV_PATH)
        if not all(col in books_df.columns for col in ['id', 'title', 'author', 'genre', 'available']):
             logging.error(f"Books CSV ({config.BOOKS_CSV_PATH}) is missing required columns.")
             st.error("Book database file is corrupted or missing required columns.")
             return pd.DataFrame(columns=['id', 'title', 'author', 'genre', 'available'])
        # Ensure 'available' is boolean if read as string
        if books_df['available'].dtype == 'object':
             books_df['available'] = books_df['available'].str.lower().map({'true': True, 'false': False}).fillna(False).astype(bool)
        return books_df
    except FileNotFoundError:
        logging.error(f"Books CSV file not found at {config.BOOKS_CSV_PATH}")
        st.error(f"Book database file not found. Please ensure '{config.BOOKS_CSV_PATH}' exists.")
        return pd.DataFrame(columns=['id', 'title', 'author', 'genre', 'available'])
    except pd.errors.EmptyDataError:
        logging.warning(f"Books CSV file is empty at {config.BOOKS_CSV_PATH}")
        return pd.DataFrame(columns=['id', 'title', 'author', 'genre', 'available'])
    except Exception as e:
        logging.error(f"Error loading books CSV: {e}")
        st.error("An unexpected error occurred while loading book data.")
        return pd.DataFrame(columns=['id', 'title', 'author', 'genre', 'available'])


def save_books(books_df: pd.DataFrame):
    """Saves the book DataFrame back to the CSV file."""
    try:
        books_df.to_csv(config.BOOKS_CSV_PATH, index=False)
        logging.info("Books data saved successfully.")
    except Exception as e:
        logging.error(f"Error saving books CSV: {e}")
        st.error("Failed to save book data.")

def add_book(title, author, genre):
    """Adds a new book to the CSV file."""
    books_df = load_books()
    # Find the next available ID
    if books_df.empty:
        new_id = 1
    else:
        new_id = books_df['id'].max() + 1

    new_book = pd.DataFrame([{
        'id': new_id,
        'title': title,
        'author': author,
        'genre': genre,
        'available': True  # New books are available by default
    }])

    # Use concat instead of append
    updated_books_df = pd.concat([books_df, new_book], ignore_index=True)
    save_books(updated_books_df)
    logging.info(f"Book added: {title}")
    return True # Indicate success