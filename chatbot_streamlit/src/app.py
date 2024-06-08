import streamlit as st
from utils.helpers import initialize_session, check_auth

def main():
    initialize_session()
    check_auth("App")

if __name__ == "__main__":
    main()