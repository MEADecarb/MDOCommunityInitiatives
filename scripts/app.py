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
      # Update the path to the correct location of map.py
      result = subprocess.run(["python", "scripts/map.py"], check=True, capture_output=True, text=True)
      st.success("Map generated successfully!")
      st.text(result.stdout)  # Display the output of the map.py script
      st.text(result.stderr)  # Display any error messages
  except subprocess.CalledProcessError as e:
      st.error("Error occurred while generating the map.")
      st.text(e.stdout)
      st.text(e.stderr)

def update_github_file(file_path, commit_message):
  try:
      contents = repo.get_contents(file_path)
      with open(file_path, "r") as file:
          new_content = file.read()
      repo.update_file(contents.path, commit_message, new_content, contents.sha)
      st.success(f"Successfully updated {file_path} on GitHub!")
  except Exception as e:
      st.error(f"An error occurred while updating the file on GitHub: {str(e)}")

def show_map_preview(map_file):
  try:
      with open(map_file, 'r', encoding='utf-8') as file:
          map_html = file.read()
      st.components.v1.html(map_html, height=600)
  except Exception as e:
      st.error(f"An error occurred while loading the map preview: {str(e)}")

st.title("Map Generator and GitHub Updater")

uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
  with open("temp_upload.csv", "wb") as f:
      f.write(uploaded_file.getbuffer())
  st.success("File uploaded successfully!")

  # Debug: Show the content of the uploaded CSV file
  uploaded_data = pd.read_csv("temp_upload.csv")
  st.write("Uploaded CSV content:")
  st.write(uploaded_data)

  run_map_generator()
  map_file = "map.html"
  show_map_preview(map_file)
  update_github_file(map_file, "Update map.html via Streamlit app")
  
  # Clean up temporary file
  os.remove("temp_upload.csv")
