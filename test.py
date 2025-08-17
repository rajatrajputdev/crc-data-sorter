import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
import numpy as np
# Hardcoded data for Indian states with coordinates
indian_states = {
    'Andhra Pradesh': {'lat': 15.9129, 'lon': 79.7400},
    'Arunachal Pradesh': {'lat': 28.2711, 'lon': 94.7278},
    'Assam': {'lat': 26.1433, 'lon': 91.7898},
    'Bihar': {'lat': 25.0961, 'lon': 85.3131},
    'Chhattisgarh': {'lat': 21.2787, 'lon': 81.8661},
    'Goa': {'lat': 15.2993, 'lon': 74.1240},
    'Gujarat': {'lat': 22.2587, 'lon': 71.1924},
    'Haryana': {'lat': 29.0588, 'lon': 76.0856},
    'Himachal Pradesh': {'lat': 31.1048, 'lon': 77.1734},
    'Jharkhand': {'lat': 23.6102, 'lon': 85.2799},
    'Karnataka': {'lat': 15.3173, 'lon': 75.7139},
    'Kerala': {'lat': 10.8505, 'lon': 76.2711},
    'Madhya Pradesh': {'lat': 22.9734, 'lon': 78.6569},
    'Maharashtra': {'lat': 19.7515, 'lon': 75.7139},
    'Manipur': {'lat': 24.6637, 'lon': 93.9063},
    'Meghalaya': {'lat': 25.4670, 'lon': 91.9563},
    'Mizoram': {'lat': 23.1645, 'lon': 92.9376},
    'Nagaland': {'lat': 26.1584, 'lon': 94.5624},
    'Odisha': {'lat': 20.9517, 'lon': 85.0985},
    'Punjab': {'lat': 31.1471, 'lon': 75.3412},
    'Rajasthan': {'lat': 27.0238, 'lon': 74.2179},
    'Sikkim': {'lat': 27.5330, 'lon': 88.5122},
    'Tamil Nadu': {'lat': 11.1271, 'lon': 78.6569},
    'Telangana': {'lat': 18.1124, 'lon': 79.0193},
    'Tripura': {'lat': 23.9408, 'lon': 91.8700},
    'Uttar Pradesh': {'lat': 26.8467, 'lon': 80.9462},
    'Uttarakhand': {'lat': 30.0668, 'lon': 79.0193},
    'West Bengal': {'lat': 22.9868, 'lon': 87.8550},
    'Andaman and Nicobar Islands': {'lat': 11.7401, 'lon': 92.6586},
    'Chandigarh': {'lat': 30.7333, 'lon': 76.7794},
    'Dadra and Nagar Haveli and Daman and Diu': {'lat': 20.1809, 'lon': 73.0169},
    'Delhi': {'lat': 28.7041, 'lon': 77.1025},
    'Jammu and Kashmir': {'lat': 33.7782, 'lon': 76.5762},
    'Ladakh': {'lat': 34.1526, 'lon': 77.5771},
    'Lakshadweep': {'lat': 10.5667, 'lon': 72.6417},
    'Puducherry': {'lat': 11.9416, 'lon': 79.8083}
}

# Dummy data for demonstration
# In your actual app, you would load this from your Excel/CSV file
signup_data = [
    {'State': 'Maharashtra', 'participants': 500},
    {'State': 'Uttar Pradesh', 'participants': 650},
    {'State': 'Delhi', 'participants': 300},
    {'State': 'Karnataka', 'participants': 450},
    {'State': 'Tamil Nadu', 'participants': 400},
    {'State': 'Gujarat', 'participants': 250},
    {'State': 'West Bengal', 'participants': 350},
    {'State': 'Telangana', 'participants': 200},
    {'State': 'Kerala', 'participants': 150},
    {'State': 'Punjab', 'participants': 180},
    {'State': 'Rajasthan', 'participants': 220},
    {'State': 'Madhya Pradesh', 'participants': 280},
    {'State': 'Bihar', 'participants': 100},
]
df_signup = pd.DataFrame(signup_data)

st.title("📊 Indian State Signup Analysis")
st.markdown("This app visualizes signup data from Indian states on an interactive map.")
st.markdown("---")

st.header("📈 Signup Statistics")
col1, col2 = st.columns(2)
with col1:
    st.metric("Total Signups", df_signup['participants'].sum())
with col2:
    top_state = df_signup.loc[df_signup['participants'].idxmax()]
    st.metric("Top State", f"{top_state['State']} ({top_state['participants']} participants)")

st.markdown("---")

st.header("📍 Geographical Distribution")
st.write("Explore the map to see the number of participants from each state. The size of the circle represents the number of signups.")

# Create a DataFrame for the map with latitudes and longitudes
map_data = pd.DataFrame(indian_states).T
map_data.index.name = 'State'
map_data = map_data.reset_index()

# Merge the signup data with the geographical data
map_data = pd.merge(map_data, df_signup, on='State', how='left').fillna(0)

# Create the Folium map centered on India
m = folium.Map(location=[22.3511148, 78.6677428], zoom_start=4.5)

# Add markers for each state with a non-zero participant count
for idx, row in map_data.iterrows():
    if row['participants'] > 0:
        folium.CircleMarker(
            location=[row['lat'], row['lon']],
            radius=np.log(row['participants'] + 1) * 2, # Use a log scale for better visualization
            popup=f"State: {row['State']}<br>Participants: {int(row['participants'])}",
            color='#FF6B6B',
            fill=True,
            fill_color='#FF6B6B'
        ).add_to(m)

# Display the map in Streamlit
folium_static(m, width=900, height=500)

st.markdown("---")

st.header("📋 Data Table")
st.write("Full data used for the visualization:")
st.dataframe(map_data.sort_values('participants', ascending=False))
