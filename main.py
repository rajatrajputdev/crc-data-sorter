import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
import re
import matplotlib.pyplot as plt
import folium
from streamlit_folium import st_folium

def clean_phone_number(phone):
    """Clean and standardize phone numbers"""
    if pd.isna(phone):
        return ""
    phone_str = str(phone).strip()
    # Remove any non-digit characters
    phone_clean = re.sub(r'\D', '', phone_str)
    # Take last 10 digits if longer
    if len(phone_clean) > 10:
        phone_clean = phone_clean[-10:]
    return phone_clean

def clean_email(email):
    """Clean and standardize email addresses"""
    if pd.isna(email):
        return ""
    return str(email).strip().lower()

def clean_aadhaar(aadhaar):
    """Clean and standardize Aadhaar last 4 digits"""
    if pd.isna(aadhaar):
        return ""
    return str(aadhaar).strip()

def get_indian_states():
    """Return list of all Indian states and union territories"""
    return [
        'Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chhattisgarh', 'Goa', 
        'Gujarat', 'Haryana', 'Himachal Pradesh', 'Jharkhand', 'Karnataka', 'Kerala', 
        'Madhya Pradesh', 'Maharashtra', 'Manipur', 'Meghalaya', 'Mizoram', 'Nagaland', 
        'Odisha', 'Punjab', 'Rajasthan', 'Sikkim', 'Tamil Nadu', 'Telangana', 'Tripura', 
        'Uttar Pradesh', 'Uttarakhand', 'West Bengal', 'Andaman and Nicobar Islands', 
        'Chandigarh', 'Dadra and Nagar Haveli and Daman and Diu', 'Delhi', 'Jammu and Kashmir', 
        'Ladakh', 'Lakshadweep', 'Puducherry'
    ]

def get_state_coordinates():
    """Return approximate coordinates for Indian states and union territories"""
    return {
        'Andhra Pradesh': [15.9129, 79.7400],
        'Arunachal Pradesh': [28.2180, 94.7278],
        'Assam': [26.2006, 92.9376],
        'Bihar': [25.0961, 85.3131],
        'Chhattisgarh': [21.2787, 81.8661],
        'Goa': [15.2993, 74.1240],
        'Gujarat': [23.0225, 72.5714],
        'Haryana': [29.0588, 76.0856],
        'Himachal Pradesh': [31.1048, 77.1734],
        'Jharkhand': [23.6102, 85.2799],
        'Karnataka': [15.3173, 75.7139],
        'Kerala': [10.8505, 76.2711],
        'Madhya Pradesh': [22.9734, 78.6569],
        'Maharashtra': [19.7515, 75.7139],
        'Manipur': [24.6637, 93.9063],
        'Meghalaya': [25.4670, 91.3662],
        'Mizoram': [23.1645, 92.9376],
        'Nagaland': [26.1584, 94.5624],
        'Odisha': [20.9517, 85.0985],
        'Punjab': [31.1471, 75.3412],
        'Rajasthan': [27.0238, 74.2179],
        'Sikkim': [27.5330, 88.5122],
        'Tamil Nadu': [11.1271, 78.6569],
        'Telangana': [18.1124, 79.0193],
        'Tripura': [23.9408, 91.9882],
        'Uttar Pradesh': [26.8467, 80.9462],
        'Uttarakhand': [30.0668, 79.0193],
        'West Bengal': [22.9868, 87.8550],
        'Andaman and Nicobar Islands': [11.7401, 92.6586],
        'Chandigarh': [30.7333, 76.7794],
        'Dadra and Nagar Haveli and Daman and Diu': [20.1809, 73.0169],
        'Delhi': [28.7041, 77.1025],
        'Jammu and Kashmir': [34.0837, 74.7973],
        'Ladakh': [34.2996, 78.2932],
        'Lakshadweep': [10.5667, 72.6417],
        'Puducherry': [11.9416, 79.8083]
    }

def create_indian_map_with_data(df, show_registration_status=False):
    """Create an interactive map of India with state-wise participant data"""
    
    # Get state coordinates
    state_coords = get_state_coordinates()
    
    # Calculate state-wise statistics
    state_counts = df['State'].value_counts().to_dict()
    
    # Create base map centered on India
    india_map = folium.Map(
        location=[20.5937, 78.9629],  # Center of India
        zoom_start=5,
        tiles='OpenStreetMap'
    )
    
    # Add markers for states with participants
    for state, count in state_counts.items():
        if state in state_coords and count > 0:
            coords = state_coords[state]
            
            # Calculate additional statistics if registration status is available
            if show_registration_status and 'Registered_Team' in df.columns:
                registered_count = len(df[(df['State'] == state) & (df['Registered_Team'] == 'Yes')])
                not_registered_count = count - registered_count
                popup_text = f"""
                <b>{state}</b><br>
                Total Participants: {count}<br>
                Registered in Teams: {registered_count}<br>
                Individual Signups: {not_registered_count}
                """
            else:
                popup_text = f"""
                <b>{state}</b><br>
                Total Participants: {count}
                """
            
            # Determine marker size based on participant count
            if count >= 100:
                marker_size = 15
                marker_color = 'red'
            elif count >= 50:
                marker_size = 12
                marker_color = 'orange'
            elif count >= 20:
                marker_size = 10
                marker_color = 'yellow'
            elif count >= 10:
                marker_size = 8
                marker_color = 'lightgreen'
            else:
                marker_size = 6
                marker_color = 'lightblue'
            
            # Add marker to map
            folium.CircleMarker(
                location=coords,
                radius=marker_size,
                popup=folium.Popup(popup_text, max_width=200),
                tooltip=f"{state}: {count} participants",
                color='black',
                weight=1,
                fillColor=marker_color,
                fillOpacity=0.7
            ).add_to(india_map)
    
    # Add a legend
    legend_html = """
    <div style="position: fixed; 
                bottom: 50px; left: 50px; width: 200px; height: 120px; 
                background-color: white; border:2px solid grey; z-index:9999; 
                font-size:14px; padding: 10px">
    <p><b>Participants Legend</b></p>
    <p><i class="fa fa-circle" style="color:red"></i> 100+ participants</p>
    <p><i class="fa fa-circle" style="color:orange"></i> 50-99 participants</p>
    <p><i class="fa fa-circle" style="color:yellow"></i> 20-49 participants</p>
    <p><i class="fa fa-circle" style="color:lightgreen"></i> 10-19 participants</p>
    <p><i class="fa fa-circle" style="color:lightblue"></i> 1-9 participants</p>
    </div>
    """
    india_map.get_root().html.add_child(folium.Element(legend_html))
    
    return india_map

def extract_state_from_data(df):
    """Extract state information from dataframe, checking multiple possible columns"""
    state_column = None
    possible_state_columns = ['State', 'state', 'State Name', 'state_name', 'State/UT', 'Location', 'Address']
    
    for col in possible_state_columns:
        if col in df.columns:
            state_column = col
            break
    
    if state_column:
        return df[state_column].fillna('Unknown')
    else:
        # If no state column found, return 'Unknown' for all rows
        return pd.Series(['Unknown'] * len(df), index=df.index)

def create_state_wise_excel(df, state_name):
    """Create downloadable Excel file for a specific state"""
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name=f'{state_name}_Participants', index=False)
    output.seek(0)
    return output.getvalue()

def process_registration_data(df_reg):
    """Process registration data to extract all team members"""
    members_list = []
    
    for _, row in df_reg.iterrows():
        team_name = row.get('Team Name', '')
        team_leader = row.get('Team Leader Name', '')
        
        # Add team leader
        if pd.notna(row.get('Team Leader Name')):
            members_list.append({
                'Name': row.get('Team Leader Name', ''),
                'Email': clean_email(row.get('Team Leader Email')),
                'Phone': clean_phone_number(row.get('Team Leader Phone Number')),
                'Aadhaar_Last4': clean_aadhaar(row.get('Team Leader Aadhaar Last 4 Digits')),
                'Team_Name': team_name,
                'Role': 'Team Leader'
            })
        
        # Add other members
        for i in range(1, 4):  # Member 1, 2, 3
            member_name = row.get(f'Member {i} Name')
            if pd.notna(member_name) and member_name.strip():
                members_list.append({
                    'Name': member_name,
                    'Email': clean_email(row.get(f'Member {i} Email')),
                    'Phone': clean_phone_number(row.get(f'Member {i} Phone Number')),
                    'Aadhaar_Last4': clean_aadhaar(row.get(f'Member {i} Aadhaar Last 4 Digits')),
                    'Team_Name': team_name,
                    'Role': row.get(f'Member {i} Role', 'Member')
                })
    
    return pd.DataFrame(members_list)

def match_users(df_signup, df_team_members):
    """Match signup users with team members"""
    # Clean signup data
    df_signup_clean = df_signup.copy()
    df_signup_clean['Email_Clean'] = df_signup_clean['Email ID'].apply(clean_email)
    df_signup_clean['Phone_Clean'] = df_signup_clean['Phone Number'].apply(clean_phone_number)
    df_signup_clean['Aadhaar_Clean'] = df_signup_clean['Aadhaar Last 4 Digits'].apply(clean_aadhaar)
    
    # Clean team members data
    df_team_clean = df_team_members.copy()
    df_team_clean['Email_Clean'] = df_team_clean['Email'].apply(clean_email)
    df_team_clean['Phone_Clean'] = df_team_clean['Phone'].apply(clean_phone_number)
    df_team_clean['Aadhaar_Clean'] = df_team_clean['Aadhaar_Last4'].apply(clean_aadhaar)
    
    # Create result dataframe
    result_df = df_signup_clean.copy()
    result_df['Registered_Team'] = 'No'
    result_df['Team_Name'] = ''
    result_df['Team_Role'] = ''
    
    # Match based on multiple criteria
    for idx, signup_row in df_signup_clean.iterrows():
        matched = False
        
        # Try to match by email first (most reliable)
        if signup_row['Email_Clean']:
            email_match = df_team_clean[df_team_clean['Email_Clean'] == signup_row['Email_Clean']]
            if not email_match.empty:
                result_df.at[idx, 'Registered_Team'] = 'Yes'
                result_df.at[idx, 'Team_Name'] = email_match.iloc[0]['Team_Name']
                result_df.at[idx, 'Team_Role'] = email_match.iloc[0]['Role']
                matched = True
        
        # If no email match, try phone number
        if not matched and signup_row['Phone_Clean']:
            phone_match = df_team_clean[df_team_clean['Phone_Clean'] == signup_row['Phone_Clean']]
            if not phone_match.empty:
                result_df.at[idx, 'Registered_Team'] = 'Yes'
                result_df.at[idx, 'Team_Name'] = phone_match.iloc[0]['Team_Name']
                result_df.at[idx, 'Team_Role'] = phone_match.iloc[0]['Role']
                matched = True
        
        # If no phone match, try Aadhaar
        if not matched and signup_row['Aadhaar_Clean']:
            aadhaar_match = df_team_clean[df_team_clean['Aadhaar_Clean'] == signup_row['Aadhaar_Clean']]
            if not aadhaar_match.empty:
                result_df.at[idx, 'Registered_Team'] = 'Yes'
                result_df.at[idx, 'Team_Name'] = aadhaar_match.iloc[0]['Team_Name']
                result_df.at[idx, 'Team_Role'] = aadhaar_match.iloc[0]['Role']
                matched = True
    
    return result_df

def create_downloadable_excel(df_result):
    """Create downloadable Excel file"""
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Main sheet with all data
        df_result.to_excel(writer, sheet_name='Registration Status', index=False)
        
        # Summary sheet
        registered_count = len(df_result[df_result['Registered_Team'] == 'Yes'])
        not_registered_count = len(df_result[df_result['Registered_Team'] == 'No'])
        
        summary_df = pd.DataFrame({
            'Status': ['Registered in Team', 'Not Registered in Team', 'Total'],
            'Count': [registered_count, not_registered_count, len(df_result)]
        })
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        # Team-wise breakdown
        if registered_count > 0:
            team_summary = df_result[df_result['Registered_Team'] == 'Yes'].groupby('Team_Name').size().reset_index(name='Members_Count')
            team_summary.to_excel(writer, sheet_name='Team Summary', index=False)
    
    output.seek(0)
    return output.getvalue()

def read_file_safely(file, file_name):
    """Safely read uploaded files with validation"""
    # Reset file pointer
    file.seek(0)
    first_bytes = file.read(2048)
    file.seek(0)

    # Check if file is actually HTML (common with fake .xls files)
    if first_bytes.startswith(b'<') or b'<html' in first_bytes.lower():
        dfs = pd.read_html(file)
        df = dfs[0]  # Take first table
        return df

    # Read CSV
    if file_name.endswith('.csv'):
        return pd.read_csv(file)

    # Try reading as real Excel
    try:
        if file_name.endswith('.xls'):
            return pd.read_excel(file, engine='xlrd')
        else:
            return pd.read_excel(file, engine='openpyxl')
    except Exception as e:
        # Attempt fallback to HTML parsing for mislabelled .xls
        file.seek(0)
        try:
            dfs = pd.read_html(file)
            df = dfs[0]
            return df
        except:
            raise ValueError(f"❌ Unable to read '{file_name}'. Make sure it's a valid Excel or CSV file.")

def display_state_statistics(df, show_registration_status=False):
    """Display state-wise statistics with download buttons"""
    st.subheader("🗺️ State-wise Statistics")
    
    # Add the interactive map
    st.subheader("🌍 Interactive India Map")
    st.write("Click on the markers to see detailed information for each state:")
    
    try:
        india_map = create_indian_map_with_data(df, show_registration_status)
        st_folium(india_map, width=700, height=500)
    except Exception as e:
        st.warning(f"Map could not be loaded: {str(e)}")
        st.info("📊 Showing tabular data instead:")
    
    # Get all Indian states
    all_states = get_indian_states()
    
    # Get actual state counts from data
    actual_state_counts = df['State'].value_counts().to_dict()
    
    # Create comprehensive state statistics
    state_stats = []
    for state in all_states:
        count = actual_state_counts.get(state, 0)
        if show_registration_status and count > 0:
            registered_count = len(df[(df['State'] == state) & (df['Registered_Team'] == 'Yes')])
        else:
            registered_count = 0
        
        state_stats.append({
            'State': state,
            'Total_Participants': count,
            'Registered_in_Teams': registered_count,
            'Not_in_Teams': count - registered_count
        })
    
    # Add states that are in data but not in the predefined list
    for state in actual_state_counts.keys():
        if state not in all_states:
            count = actual_state_counts[state]
            if show_registration_status:
                registered_count = len(df[(df['State'] == state) & (df['Registered_Team'] == 'Yes')])
            else:
                registered_count = 0
            state_stats.append({
                'State': state,
                'Total_Participants': count,
                'Registered_in_Teams': registered_count,
                'Not_in_Teams': count - registered_count
            })
    
    # Convert to DataFrame and sort by participant count
    state_stats_df = pd.DataFrame(state_stats)
    state_stats_df = state_stats_df.sort_values('Total_Participants', ascending=False)
    
    # Display state statistics
    states_with_participants = state_stats_df[state_stats_df['Total_Participants'] > 0]
    states_without_participants = state_stats_df[state_stats_df['Total_Participants'] == 0]
    
    if len(states_with_participants) > 0:
        st.write("**States with Participants:**")
        
        # Create columns for better display
        num_cols = 3
        cols = st.columns(num_cols)
        
        for idx, (_, row) in enumerate(states_with_participants.iterrows()):
            col_idx = idx % num_cols
            with cols[col_idx]:
                st.write(f"**{row['State']}**")
                if show_registration_status:
                    st.write(f"Total: {row['Total_Participants']} | Teams: {row['Registered_in_Teams']} | Individual: {row['Not_in_Teams']}")
                else:
                    st.write(f"Total: {row['Total_Participants']} participants")
                
                # Download button for this state
                state_data = df[df['State'] == row['State']]
                if len(state_data) > 0:
                    excel_data = create_state_wise_excel(state_data, row['State'])
                    st.download_button(
                        label=f"📥 Download {row['State']} Data",
                        data=excel_data,
                        file_name=f"{row['State'].replace(' ', '_')}_participants_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        key=f"download_{row['State']}_{idx}"
                    )
                st.write("---")
    
    # Show summary of states without participants
    if len(states_without_participants) > 0:
        with st.expander(f"📍 States with 0 participants ({len(states_without_participants)} states)"):
            zero_states = states_without_participants['State'].tolist()
            # Display in 4 columns
            num_cols = 4
            cols = st.columns(num_cols)
            for idx, state in enumerate(zero_states):
                col_idx = idx % num_cols
                with cols[col_idx]:
                    st.write(f"• {state}")

# Streamlit App
st.set_page_config(page_title="Team Registration Tracker", page_icon="📊", layout="wide")

st.title("📊 Team Registration Tracker")
st.markdown("Choose your analysis type and upload the required files")

# Install instruction notice
st.info("📝 **Note**: To run this enhanced version, install the required packages: `pip install folium streamlit-folium`")

# Main selection
st.subheader("🎯 What would you like to analyze?")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div style="border: 2px solid #FF6B6B; border-radius: 10px; padding: 20px; text-align: center; margin: 10px 0;">
        <h3 style="color: #FF6B6B;">Signup Analysis Only</h3>
        <p>Analyze individual signups and get state-wise statistics with interactive map</p>
    </div>
    """, unsafe_allow_html=True)
    
    signup_only = st.button("Choose Signup Analysis", key="signup_only", use_container_width=True)

with col3:
    st.markdown("""
    <div style="border: 2px solid #FF6B6B; border-radius: 10px; padding: 20px; text-align: center; margin: 10px 0;">
        <h3 style="color: #FF6B6B;">Registration Analysis Only</h3>
        <p>Analyze individual registrations and get state-wise statistics</p>
    </div>
    """, unsafe_allow_html=True)

    registration_only = st.button("Choose Registration Analysis", key="registration_only", use_container_width=True)

with col2:
    st.markdown("""
    <div style="border: 2px solid #4ECDC4; border-radius: 10px; padding: 20px; text-align: center; margin: 10px 0;">
        <h3 style="color: #4ECDC4;">Complete Team Analysis</h3>
        <p>Full analysis comparing signups with team registrations with interactive map</p>
    </div>
    """, unsafe_allow_html=True)
    
    team_analysis = st.button("Choose Team Analysis", key="team_analysis", use_container_width=True)

# Initialize session state
if 'analysis_type' not in st.session_state:
    st.session_state.analysis_type = None

# Set analysis type based on button clicks
if signup_only:
    st.session_state.analysis_type = 'signup_only'
elif team_analysis:
    st.session_state.analysis_type = 'team_analysis'
elif registration_only:
    st.session_state.analysis_type = 'registration_only'

# Show file upload and analysis based on selection
if st.session_state.analysis_type == 'signup_only':
    st.markdown("---")
    st.subheader("📝 Signup Analysis")
    
    signup_file = st.file_uploader(
        "Upload Signup Excel/CSV", 
        type=['xlsx', 'xls', 'csv'], 
        key="signup_file",
        help="Upload your signup data file containing participant information"
    )
    
    if signup_file:
        try:
            # Load signup data
            df_signup = read_file_safely(signup_file, signup_file.name)
            
            # Extract state information
            df_signup['State'] = extract_state_from_data(df_signup)
            
            st.success(f"✅ {len(df_signup)} signup records loaded successfully!")
            
            # Basic statistics
            st.subheader("📈 Statistics")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Signups", len(df_signup))
            with col2:
                unique_states = len(df_signup['State'].value_counts())
                st.metric("States Represented", unique_states)
            with col3:
                top_state = df_signup['State'].mode().iloc[0] if len(df_signup) > 0 else "N/A"
                st.metric("Top State", top_state)
            
            # State-wise statistics with interactive map
            display_state_statistics(df_signup, show_registration_status=False)
            
            # Download complete report
            st.subheader("💾 Download Results")
            excel_data = create_state_wise_excel(df_signup, "All_Participants")
            st.download_button(
                label="📥 Download Complete Signup Report",
                data=excel_data,
                file_name=f"signup_report_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
        except Exception as e:
            st.error(f"❌ Error processing files: {str(e)}")
            st.write("Please ensure your files have the correct format and column names.")
    
    elif signup_file:
        st.info("📁 Please upload both signup and registration files for complete analysis")

elif st.session_state.analysis_type == 'registration_only':
    st.markdown("---")
    st.subheader("📋 Registration Analysis")

    reg_file = st.file_uploader(
        "📝 Upload Registration Data", 
        type=['xlsx', 'xls', 'csv'], 
        key="reg_file",
        help="Upload your team registration data file"
    )

    if reg_file:
        try:
            # Load registration data safely
            df = read_file_safely(reg_file, reg_file.name)

            # Convert Registration_Date if column exists
            if "Registration_Date" in df.columns:
                df["Registration_Date"] = pd.to_datetime(df["Registration_Date"], errors="coerce")

            # Remove duplicate teams
            if "Team Name" in df.columns and "Team Leader Name" in df.columns:
                df_clean = df.drop_duplicates(subset=["Team Name", "Team Leader Name"])
            else:
                df_clean = df.copy()

            # Find missing PPT if column exists
            if "PPT Link / File Name" in df_clean.columns:
                missing_ppt = df_clean[df_clean["PPT Link / File Name"].isna()]
            else:
                missing_ppt = pd.DataFrame()

            # Calculate team size if member columns exist
            member_cols = [col for col in df_clean.columns if "Member" in col and "Name" in col]
            if member_cols:
                df_clean["Team Size"] = df_clean[member_cols].notna().sum(axis=1) + 1
                avg_team_size = df_clean["Team Size"].mean()
            else:
                avg_team_size = 0

            # Sidebar filters
            st.sidebar.header("🔍 Filters")
            if "Theme" in df_clean.columns:
                theme_filter = st.sidebar.multiselect(
                    "Select Theme(s)", 
                    options=df_clean["Theme"].dropna().unique()
                )
            else:
                theme_filter = []

            if "Team Leader University Name with address" in df_clean.columns:
                uni_filter = st.sidebar.multiselect(
                    "Select University(s)", 
                    options=df_clean["Team Leader University Name with address"].dropna().unique()
                )
            else:
                uni_filter = []

            # Date range filter if available
            if "Registration_Date" in df_clean.columns:
                min_date = df_clean["Registration_Date"].min()
                max_date = df_clean["Registration_Date"].max()
                date_range = st.sidebar.date_input("Select Date Range", [min_date, max_date])
            else:
                date_range = None

            # Apply filters
            filtered_df = df_clean.copy()
            if theme_filter and "Theme" in filtered_df.columns:
                filtered_df = filtered_df[filtered_df["Theme"].isin(theme_filter)]
            if uni_filter and "Team Leader University Name with address" in filtered_df.columns:
                filtered_df = filtered_df[filtered_df["Team Leader University Name with address"].isin(uni_filter)]
            if date_range and len(date_range) == 2 and "Registration_Date" in filtered_df.columns:
                start_date, end_date = date_range
                filtered_df = filtered_df[
                    (filtered_df["Registration_Date"] >= pd.to_datetime(start_date)) &
                    (filtered_df["Registration_Date"] <= pd.to_datetime(end_date))
                ]

            # Tabs
            tab1, tab2, tab3, tab4 = st.tabs(["📄 Data Preview", "📊 Charts", "⚠ Missing PPT", "📥 Downloads"])

            # Tab 1 - Data Preview
            with tab1:
                st.subheader("📌 Key Stats")
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Total Teams", len(filtered_df))
                if "Team Leader University Name with address" in filtered_df.columns:
                    col2.metric("Unique Universities", filtered_df["Team Leader University Name with address"].nunique())
                else:
                    col2.metric("Unique Universities", "N/A")
                col3.metric("Avg Team Size", f"{avg_team_size:.2f}")
                col4.metric("Missing PPT", len(missing_ppt))

                st.subheader("📄 Filtered Data")
                st.dataframe(filtered_df)

            # Tab 2 - Charts
            with tab2:
                if "Theme" in filtered_df.columns and not filtered_df.empty:
                    col1, col2 = st.columns(2)

                    with col1:
                        st.subheader("🎯 Teams per Theme")
                        theme_counts = filtered_df["Theme"].value_counts()
                        fig1, ax1 = plt.subplots()
                        ax1.pie(theme_counts, labels=theme_counts.index, autopct='%1.1f%%', startangle=90)
                        ax1.axis('equal')
                        st.pyplot(fig1)

                    with col2:
                        if "Team Leader University Name with address" in filtered_df.columns:
                            st.subheader("🏫 Top 5 Universities by Participation")
                            top_unis = filtered_df["Team Leader University Name with address"].value_counts().head(5)
                            fig2, ax2 = plt.subplots()
                            ax2.bar(top_unis.index, top_unis.values)
                            plt.xticks(rotation=45, ha='right')
                            st.pyplot(fig2)

                # Line Chart - Registrations Over Time
                if "Registration_Date" in filtered_df.columns:
                    st.subheader("📅 Registrations Over Time")
                    registrations_by_date = filtered_df.groupby(filtered_df["Registration_Date"].dt.date).size()
                    st.line_chart(registrations_by_date)

                # 📌 NEW: Theme-wise Data with Download
                if "Theme" in filtered_df.columns:
                    st.markdown("---")
                    st.subheader("📂 Theme-wise Data & Downloads")
                    
                    theme_groups = filtered_df.groupby("Theme")
                    for theme_name, theme_df in theme_groups:
                        st.write(f"### 🎯 {theme_name} — {len(theme_df)} Teams")
                        theme_excel = BytesIO()
                        with pd.ExcelWriter(theme_excel, engine='openpyxl') as writer:
                            theme_df.to_excel(writer, index=False, sheet_name="Theme Data")
                        theme_excel.seek(0)

                        st.download_button(
                            label=f"📥 Download '{theme_name}' Data",
                            data=theme_excel,
                            file_name=f"{theme_name.replace(' ', '_')}_teams.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )

            # Tab 3 - Missing PPT
            with tab3:
                st.subheader("⚠ Teams Missing PPT")
                if not missing_ppt.empty:
                    def highlight_missing(s):
                        return ['background-color: #ffcccc' if pd.isna(v) else '' for v in s]
                    st.dataframe(missing_ppt.style.apply(highlight_missing, subset=["PPT Link / File Name"]))
                else:
                    st.info("✅ No missing PPTs found.")

            # Tab 4 - Downloads
            with tab4:
                st.subheader("📥 Download Data")
                st.download_button("Download Cleaned CSV", df_clean.to_csv(index=False), "registrations_cleaned.csv", "text/csv")
                if not missing_ppt.empty:
                    st.download_button("Download Missing PPT List", missing_ppt.to_csv(index=False), "teams_missing_ppt.csv", "text/csv")

        except Exception as e:
            st.error(f"❌ Error processing registration file: {str(e)}")
    else:
        st.info("📁 Please upload the registration file to proceed.")



elif st.session_state.analysis_type == 'team_analysis':
    st.markdown("---")
    st.subheader("👥 Team Registration Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        signup_file = st.file_uploader(
            "📝 Upload Signup Data", 
            type=['xlsx', 'xls', 'csv'], 
            key="signup_team_file",
            help="Upload your signup data file"
        )
    
    with col2:
        registration_file = st.file_uploader(
            "👥 Upload Registration Data", 
            type=['xlsx', 'xls', 'csv'], 
            key="registration_file",
            help="Upload your team registration data file"
        )
    
    if signup_file and registration_file:
        try:
            # Load data files
            df_signup = read_file_safely(signup_file, signup_file.name)
            df_registration = read_file_safely(registration_file, registration_file.name)
            
            st.success(f"✅ Files loaded: {len(df_signup)} signups, {len(df_registration)} team registrations")
            
            # Process data
            with st.spinner("Processing team matching..."):
                # Extract team members from registration data
                df_team_members = process_registration_data(df_registration)
                
                # Match signup users with team members
                df_result = match_users(df_signup, df_team_members)
                
                # Extract state information
                df_result['State'] = extract_state_from_data(df_result)
            
            # Display statistics
            st.subheader("📈 Statistics")
            
            col1, col2, col3, col4 = st.columns(4)
            
            total_signups = len(df_result)
            registered_in_team = len(df_result[df_result['Registered_Team'] == 'Yes'])
            not_registered = total_signups - registered_in_team
            unique_teams = df_result[df_result['Registered_Team'] == 'Yes']['Team_Name'].nunique()
            
            with col1:
                st.metric("Total Signups", total_signups)
            
            with col2:
                st.metric("Registered in Teams", registered_in_team, 
                         delta=f"{(registered_in_team/total_signups*100):.1f}%")
            
            with col3:
                st.metric("Not in Teams", not_registered, 
                         delta=f"{(not_registered/total_signups*100):.1f}%")
            
            with col4:
                st.metric("Unique Teams", unique_teams)
            
            # State-wise statistics
            display_state_statistics(df_result, show_registration_status=True)
            
            # Download section
            st.subheader("💾 Download Results")
            
            # Create downloadable file
            excel_data = create_downloadable_excel(df_result)
            
            st.download_button(
                label="📥 Download Complete Team Analysis Report",
                data=excel_data,
                file_name=f"team_registration_report_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
            # Team-wise breakdown
            if registered_in_team > 0:
                st.subheader("🏆 Team-wise Breakdown")
                
                for team in df_result[df_result['Registered_Team'] == 'Yes']['Team_Name'].unique():
                    team_data = df_result[df_result['Team_Name'] == team]
                    with st.expander(f"Team: {team} ({len(team_data)} members)"):
                        st.dataframe(team_data[['Full Name', 'Email ID', 'Phone Number', 'Team_Role', 'University Name']], 
                                   use_container_width=True)
            
        except Exception as e:
            st.error(f"❌ Error processing files: {str(e)}")
            st.write("Please ensure your files have the correct format and column names.")
    
    elif signup_file or registration_file:
        st.info("📁 Please upload both signup and registration files for complete analysis")
# elif st.session_state.analysis_type == 'registration_only':
#     st.markdown("---")
#     st.subheader("📋 Registration Analysis")

#     reg_file = st.file_uploader(
#         "📝 Upload Registration Data", 
#         type=['xlsx', 'xls', 'csv'], 
#         key="reg_file",
#         help="Upload your team registration data file"
#     )

#     if reg_file:
#         try:
#             # Load registration data safely
#             df = read_file_safely(reg_file, reg_file.name)

#             # Convert Registration_Date if column exists
#             if "Registration_Date" in df.columns:
#                 df["Registration_Date"] = pd.to_datetime(df["Registration_Date"], errors="coerce")

#             # Remove duplicate teams
#             if "Team Name" in df.columns and "Team Leader Name" in df.columns:
#                 df_clean = df.drop_duplicates(subset=["Team Name", "Team Leader Name"])
#             else:
#                 df_clean = df.copy()

#             # Find missing PPT if column exists
#             if "PPT Link / File Name" in df_clean.columns:
#                 missing_ppt = df_clean[df_clean["PPT Link / File Name"].isna()]
#             else:
#                 missing_ppt = pd.DataFrame()

#             # Calculate team size if member columns exist
#             member_cols = [col for col in df_clean.columns if "Member" in col and "Name" in col]
#             if member_cols:
#                 df_clean["Team Size"] = df_clean[member_cols].notna().sum(axis=1) + 1
#                 avg_team_size = df_clean["Team Size"].mean()
#             else:
#                 avg_team_size = 0

#             # Sidebar filters
#             st.sidebar.header("🔍 Filters")
#             if "Theme" in df_clean.columns:
#                 theme_filter = st.sidebar.multiselect(
#                     "Select Theme(s)", 
#                     options=df_clean["Theme"].dropna().unique()
#                 )
#             else:
#                 theme_filter = []

#             if "Team Leader University Name with address" in df_clean.columns:
#                 uni_filter = st.sidebar.multiselect(
#                     "Select University(s)", 
#                     options=df_clean["Team Leader University Name with address"].dropna().unique()
#                 )
#             else:
#                 uni_filter = []

#             # Date range filter if available
#             if "Registration_Date" in df_clean.columns:
#                 min_date = df_clean["Registration_Date"].min()
#                 max_date = df_clean["Registration_Date"].max()
#                 date_range = st.sidebar.date_input("Select Date Range", [min_date, max_date])
#             else:
#                 date_range = None

#             # Apply filters
#             filtered_df = df_clean.copy()
#             if theme_filter and "Theme" in filtered_df.columns:
#                 filtered_df = filtered_df[filtered_df["Theme"].isin(theme_filter)]
#             if uni_filter and "Team Leader University Name with address" in filtered_df.columns:
#                 filtered_df = filtered_df[filtered_df["Team Leader University Name with address"].isin(uni_filter)]
#             if date_range and len(date_range) == 2 and "Registration_Date" in filtered_df.columns:
#                 start_date, end_date = date_range
#                 filtered_df = filtered_df[
#                     (filtered_df["Registration_Date"] >= pd.to_datetime(start_date)) &
#                     (filtered_df["Registration_Date"] <= pd.to_datetime(end_date))
#                 ]

#             # Tabs
#             tab1, tab2, tab3, tab4 = st.tabs(["📄 Data Preview", "📊 Charts", "⚠ Missing PPT", "📥 Downloads"])

#             # Tab 1 - Data Preview
#             with tab1:
#                 st.subheader("📌 Key Stats")
#                 col1, col2, col3, col4 = st.columns(4)
#                 col1.metric("Total Teams", len(filtered_df))
#                 if "Team Leader University Name with address" in filtered_df.columns:
#                     col2.metric("Unique Universities", filtered_df["Team Leader University Name with address"].nunique())
#                 else:
#                     col2.metric("Unique Universities", "N/A")
#                 col3.metric("Avg Team Size", f"{avg_team_size:.2f}")
#                 col4.metric("Missing PPT", len(missing_ppt))

#                 st.subheader("📄 Filtered Data")
#                 st.dataframe(filtered_df)

#             # Tab 2 - Charts
#             with tab2:
#                 if "Theme" in filtered_df.columns and not filtered_df.empty:
#                     col1, col2 = st.columns(2)

#                     with col1:
#                         st.subheader("🎯 Teams per Theme")
#                         theme_counts = filtered_df["Theme"].value_counts()
#                         fig1, ax1 = plt.subplots()
#                         ax1.pie(theme_counts, labels=theme_counts.index, autopct='%1.1f%%', startangle=90)
#                         ax1.axis('equal')
#                         st.pyplot(fig1)

#                     with col2:
#                         if "Team Leader University Name with address" in filtered_df.columns:
#                             st.subheader("🏫 Top 5 Universities by Participation")
#                             top_unis = filtered_df["Team Leader University Name with address"].value_counts().head(5)
#                             fig2, ax2 = plt.subplots()
#                             ax2.bar(top_unis.index, top_unis.values)
#                             plt.xticks(rotation=45, ha='right')
#                             st.pyplot(fig2)

#                 # Line Chart - Registrations Over Time
#                 if "Registration_Date" in filtered_df.columns:
#                     st.subheader("📅 Registrations Over Time")
#                     registrations_by_date = filtered_df.groupby(filtered_df["Registration_Date"].dt.date).size()
#                     st.line_chart(registrations_by_date)

#                 # 📌 NEW: Theme-wise Data with Download
#                 if "Theme" in filtered_df.columns:
#                     st.markdown("---")
#                     st.subheader("📂 Theme-wise Data & Downloads")
                    
#                     theme_groups = filtered_df.groupby("Theme")
#                     for theme_name, theme_df in theme_groups:
#                         st.write(f"### 🎯 {theme_name} — {len(theme_df)} Teams")
#                         theme_excel = BytesIO()
#                         with pd.ExcelWriter(theme_excel, engine='openpyxl') as writer:
#                             theme_df.to_excel(writer, index=False, sheet_name="Theme Data")
#                         theme_excel.seek(0)

#                         st.download_button(
#                             label=f"📥 Download '{theme_name}' Data",
#                             data=theme_excel,
#                             file_name=f"{theme_name.replace(' ', '_')}_teams.xlsx",
#                             mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
#                         )

#             # Tab 3 - Missing PPT
#             with tab3:
#                 st.subheader("⚠ Teams Missing PPT")
#                 if not missing_ppt.empty:
#                     def highlight_missing(s):
#                         return ['background-color: #ffcccc' if pd.isna(v) else '' for v in s]
#                     st.dataframe(missing_ppt.style.apply(highlight_missing, subset=["PPT Link / File Name"]))
#                 else:
#                     st.info("✅ No missing PPTs found.")

#             # Tab 4 - Downloads
#             with tab4:
#                 st.subheader("📥 Download Data")
#                 st.download_button("Download Cleaned CSV", df_clean.to_csv(index=False), "registrations_cleaned.csv", "text/csv")
#                 if not missing_ppt.empty:
#                     st.download_button("Download Missing PPT List", missing_ppt.to_csv(index=False), "teams_missing_ppt.csv", "text/csv")

#         except Exception as e:
#             st.error(f"❌ Error processing registration file: {str(e)}")
#     else:
#         st.info("📁 Please upload the registration file to proceed.")
 

else:
    st.info("👆 Please choose an analysis type to begin")
