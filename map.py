import folium
from folium.plugins import Geocoder, MarkerCluster
import requests
import pandas as pd

# Define a color palette
color_palette = ["#2C557E", "#fdda25", "#B7DCDF", "#000000"]  # Fixed color format

# Create a base map centered over Maryland
m = folium.Map(location=[39.0458, -76.6413], zoom_start=8)

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
        # Use 'County' as the label for 'COUNTY_NAME'
        geojson_layer.add_child(folium.GeoJsonPopup(fields=['COUNTY_NAME'], aliases=['County:'], labels=True))

    geojson_layer.add_to(feature_group)
    feature_group.add_to(map_obj)

# Add the MDOT SHA County Boundaries GeoJSON layer
github_geojson_sources = [
    ("https://services.arcgis.com/njFNhDsUCentVYJW/arcgis/rest/services/MDOT_SHA_County_Boundaries/FeatureServer/0/query?outFields=*&where=1%3D1&f=geojson", "MDOT SHA County Boundaries")
]

for i, (url, name) in enumerate(github_geojson_sources):
    color = color_palette[i % len(color_palette)]
    add_geojson_from_url(url, name, color, m)

# Load the CSV data for mapping points
csv_url = "https://raw.githubusercontent.com/MEADecarb/MDOCommunityInitiatives/main/Resources_Aug24%20-%20Sheet2.csv"
data = pd.read_csv(csv_url)

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
            renamed_field = field_names.get(field, field)  # Rename the field if a new name is provided
            popup_content += f"<strong>{renamed_field}:</strong> {row[field]}<br>"
    
    popup_content += "</div>"
    
    # Create a custom icon for the LGBTQIA flag
    icon = folium.CustomIcon(
        icon_image="https://upload.wikimedia.org/wikipedia/commons/thumb/4/48/Gay_Pride_Flag.svg/2560px-Gay_Pride_Flag.svg.png",
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

m
