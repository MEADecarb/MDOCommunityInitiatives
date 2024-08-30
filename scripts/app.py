import streamlit as st
import pandas as pd
import subprocess
import os
from github import Github

# Access the GitHub token
github_token = st.secrets["github"]["token"]

# GitHub setup
github_repo = "MEADecarb/MDOCommunityInitiatives"

g = Github(github_token)
repo = g.get_repo(github_repo)

def run_map_generator():
    try:
        subprocess.run(["python", "map.py"], check=True)
        st.success("Map generated successfully!")
    except subprocess.CalledProcessError:
        st.error("Error occurred while generating the map.")

def update_github_file(file_path, commit_message):
    try:
        contents = repo.get_contents(file_path)
        with open(file_path, "r") as file:
            new_content = file.read()
        repo.update_file(contents.path, commit_message, new_content, contents.sha)
        st.success(f"Successfully updated {file_path} on GitHub!")
    except Exception as e:
        st.error(f"An error occurred while updating the file on GitHub: {str(e)}")

st.title("Map Generator and GitHub Updater")

uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    with open("temp_upload.csv", "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.success("File uploaded successfully!")
    
    run_map_generator()
    update_github_file("map.html", "Update map.html via Streamlit app")
    
    # Clean up temporary file
    os.remove("temp_upload.csv")
