import streamlit as st
from utils import database
import logging

def show_login_page():
    """Displays the login form."""
    st.header("Login")

    users_df = database.load_users()
    if users_df.empty and not config.USERS_CSV_PATH.exists():
         st.warning("User database is empty or not found. Cannot log in.")
         # Optional: Provide instructions to create the file or a first user?
         return # Stop execution if no users can be loaded

    with st.form("login_form"):
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        submitted = st.form_submit_button("Login")

        if submitted:
            if not username or not password:
                st.warning("Please enter both username and password.")
            elif database.verify_user(users_df, username, password):
                st.session_state["logged_in"] = True
                st.session_state["username"] = username
                logging.info(f"User '{username}' logged in successfully.")
                # Use experimental_rerun for cleaner state transition
                st.rerun()
            else:
                st.error("Incorrect username or password.")
                logging.warning(f"Failed login attempt for username: '{username}'")

def add_logout_button():
    """Adds a logout button to the sidebar."""
    if st.sidebar.button("Logout"):
        # Clear relevant session state variables
        for key in ["logged_in", "username"]:
            if key in st.session_state:
                del st.session_state[key]
        logging.info("User logged out.")
        st.rerun() # Rerun to go back to login page