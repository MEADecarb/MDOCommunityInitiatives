import streamlit as st
import pandas as pd
import subprocess
import os
from github import Github

# Access the GitHub token securely from Streamlit secrets
github_token = st.secrets["github"]["token"]

# GitHub setup
github_repo = "MEADecarb/MDOCommunityInitiatives"

# Authenticate with GitHub
g = Github(github_token)
repo = g.get_repo(github_repo)

def run_map_generator():
    try:
        # Run the map generation script
        result = subprocess.run(["python", "scripts/map.py"], check=True, capture_output=True, text=True)
        st.success("Map generated successfully!")
        st.text(result.stdout)  # Display the output of the map.py script
        st.text(result.stderr)  # Display any error messages
    except subprocess.CalledProcessError as e:
        st.error("Error occurred while generating the map.")
        st.text(e.stdout)
        st.text(e.stderr)
    except FileNotFoundError as e:
        st.error("Map generation script not found. Please check the file path.")
        st.text(str(e))
    except Exception as e:
        st.error("An unexpected error occurred while generating the map.")
        st.text(str(e))

def update_github_file(file_path, commit_message):
    try:
        contents = repo.get_contents(file_path)
        with open(file_path, "r") as file:
            new_content = file.read()
        repo.update_file(contents.path, commit_message, new_content, contents.sha)
        st.success(f"Successfully updated {file_path} on GitHub!")
    except FileNotFoundError as e:
        st.error(f"File {file_path} not found. Please check the file path.")
        st.text(str(e))
    except Exception as e:
        st.error(f"An error occurred while updating the file on GitHub: {str(e)}")

def show_map_preview(map_file):
    try:
        with open(map_file, 'r', encoding='utf-8') as file:
            map_html = file.read()
        st.components.v1.html(map_html, height=600)
    except FileNotFoundError as e:
        st.error(f"Map file {map_file} not found. Please ensure the map was generated successfully.")
        st.text(str(e))
    except Exception as e:
        st.error(f"An error occurred while loading the map preview: {str(e)}")

st.title("Map Generator and GitHub Updater")

# File uploader for CSV files
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    # Save the uploaded file to a temporary location
    temp_csv_path = "temp_upload.csv"
    with open(temp_csv_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.success("File uploaded successfully!")

    # Display the content of the uploaded CSV file for verification
    try:
        uploaded_data = pd.read_csv(temp_csv_path)
        st.write("Uploaded CSV content:")
        st.write(uploaded_data)
    except pd.errors.EmptyDataError:
        st.error("Uploaded CSV file is empty or corrupt.")
    except Exception as e:
        st.error(f"An error occurred while reading the CSV file: {str(e)}")

    # Run the map generation script and handle the result
    run_map_generator()

    # Define the map file name (assuming the map is saved as map.html)
    map_file = "map.html"
    
    # Show a preview of the generated map
    show_map_preview(map_file)
    
    # Update the map file on GitHub
    update_github_file(map_file, "Update map.html via Streamlit app")
    
    # Clean up temporary file
    try:
        os.remove(temp_csv_path)
    except Exception as e:
        st.error(f"An error occurred while deleting the temporary file: {str(e)}")
