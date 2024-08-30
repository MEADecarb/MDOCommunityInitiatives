import streamlit as st
import pandas as pd
import folium
from folium.plugins import Geocoder, MarkerCluster
import requests
import os
from github import Github

# GitHub setup
github_token = st.secrets["github"]["token"]
github_repo = "MEADecarb/MDOCommunityInitiatives"
g = Github(github_token)
repo = g.get_repo(github_repo)

# Define a color palette
color_palette = ["#2C557E", "#fdda25", "#B7DCDF", "#000000"]

# Function to add GeoJSON from a URL to a feature group with custom color and pop-up
def add_geojson_from_url(geojson_url, name, color, map_obj):
    feature_group = folium.FeatureGroup(name=name)
    style_function = lambda x: {'fillColor': color, 'color': color}
    response = requests.get(geojson_url)
    geojson_data = response.json()

    geojson_layer = folium.GeoJson(
        geojson_data,
        style_function=style_function
    )

    if name == "MDOT SHA County Boundaries":
        geojson_layer.add_child(folium.GeoJsonPopup(fields=['COUNTY_NAME'], aliases=['County:'], labels=True))

    geojson_layer.add_to(feature_group)
    feature_group.add_to(map_obj)

# Function to generate the map
def generate_map(csv_path):
    # Create a base map centered over Maryland
    m = folium.Map(location=[39.0458, -76.6413], zoom_start=8)

    # Add the MDOT SHA County Boundaries GeoJSON layer
    github_geojson_sources = [
        ("https://services.arcgis.com/njFNhDsUCentVYJW/arcgis/rest/services/MDOT_SHA_County_Boundaries/FeatureServer/0/query?outFields=*&where=1%3D1&f=geojson", "MDOT SHA County Boundaries")
    ]

    for i, (url, name) in enumerate(github_geojson_sources):
        color = color_palette[i % len(color_palette)]
        add_geojson_from_url(url, name, color, m)

    # Load the CSV data for mapping points
    data = pd.read_csv(csv_path)

    # Define a dictionary to rename the fields (aliases) in the popup
    field_names = {
        "Organization or Agency Name": "Organization",
        "Organization or Agency Phone Number": "Phone",
        "Organization or Agency Email": "Email",
        "Organization or Agency Location or Address": "Location",
        "Organization or Agency Website": "Website",
        "Facebook": "Facebook",
        "X (formerly Twitter)": "Twitter",
        "Instagram": "Instagram",
        "LinkedIn": "LinkedIn",
        "Truncated Description": "Description"
    }

    # Filter out the columns that should not be included in the popup
    popup_fields = [
        "Organization or Agency Name",
        "Organization or Agency Phone Number",
        "Organization or Agency Email",
        "Organization or Agency Location or Address",
        "Organization or Agency Website",
        "Facebook",
        "X (formerly Twitter)",
        "Instagram",
        "LinkedIn",
        "Truncated Description"
    ]

    # Create a MarkerCluster to manage the display of many points
    marker_cluster = MarkerCluster().add_to(m)

    # Add each point to the map with a popup displaying the relevant fields
    for _, row in data.iterrows():
        popup_content = "<div style='max-height: 150px; overflow-y: auto;'>"

        # Add the Organization Name field in bold, centered, and hyperlink it to the website
        if pd.notna(row['Organization or Agency Name']) and pd.notna(row['Organization or Agency Website']) and row['Organization or Agency Website'].strip():
            popup_content += f"<div style='text-align:center;'><strong><a href='{row['Organization or Agency Website']}' target='_blank'>{row['Organization or Agency Name']}</a></strong></div><br>"
        elif pd.notna(row['Organization or Agency Name']):
            popup_content += f"<div style='text-align:center;'><strong>{row['Organization or Agency Name']}</strong></div><br>"

        # Add other fields if they are not blank or NaN
        for field in popup_fields:
            if field != "Organization or Agency Name" and pd.notna(row[field]) and row[field] != "":
                renamed_field = field_names.get(field, field)
                popup_content += f"<strong>{renamed_field}:</strong> {row[field]}<br>"

        popup_content += "</div>"

        # Create a custom icon for the Intersex-inclusive Pride flag
        icon = folium.CustomIcon(
            icon_image="https://raw.githubusercontent.com/MEADecarb/MDOCommunityInitiatives/main/images/Intersex-inclusive_pride_flag.svg.png",
            icon_size=(30, 20)
        )

        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            popup=folium.Popup(popup_content, max_width=300),
            icon=icon
        ).add_to(marker_cluster)

    # Add Layer Control to toggle feature groups
    folium.LayerControl().add_to(m)

    # Initialize the geocoder plugin
    geocoder = Geocoder(
        collapse=True,
        position='topleft',
        add_marker=True,
        popup_on_found=True,
        zoom=12,
        search_label='address'
    )

    geocoder.add_to(m)

    # Save the map
    m.save("map.html")

# Function to update the GitHub file
def update_github_file(file_path, commit_message):
    try:
        contents = repo.get_contents(file_path)
        with open(file_path, "r") as file:
            new_content = file.read()
        repo.update_file(contents.path, commit_message, new_content, contents.sha)
        st.success(f"Successfully updated {file_path} on GitHub!")
    except Exception as e:
        st.error(f"An error occurred while updating the file on GitHub: {str(e)}")

# Function to show the map preview
def show_map_preview(map_file):
    try:
        with open(map_file, 'r', encoding='utf-8') as file:
            map_html = file.read()
        st.components.v1.html(map_html, height=600)
    except Exception as e:
        st.error(f"An error occurred while loading the map preview: {str(e)}")

# Streamlit app
st.title("Map Generator and GitHub Updater")

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

    # Generate the map
    generate_map(temp_csv_path)

    # Show the map preview
    map_file = "map.html"
    show_map_preview(map_file)

    # Update the map file on GitHub
    update_github_file(map_file, "Update map.html via Streamlit app")

    # Clean up temporary file
    try:
        os.remove(temp_csv_path)
    except Exception as e:
        st.error(f"An error occurred while deleting the temporary file: {str(e)}")
