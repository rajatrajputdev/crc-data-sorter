import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
import re

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

# Streamlit App
st.set_page_config(page_title="Team Registration Tracker", page_icon="📊", layout="wide")

st.title("📊 Team Registration Tracker")
st.markdown("Upload your signup and registration files to track team formation status")

# File upload section
col1, col2 = st.columns(2)

with col1:
    st.subheader("📝 Signup Data")
    signup_file = st.file_uploader("Upload Signup Excel/CSV", type=['xlsx', 'xls', 'csv'], key="signup")

with col2:
    st.subheader("👥 Registration Data")
    registration_file = st.file_uploader("Upload Registration Excel/CSV", type=['xlsx', 'xls', 'csv'], key="registration")

if signup_file and registration_file:
    try:
        # Function to safely read files with validation
        def read_file_safely(file, file_name):
            import tempfile
            
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

        
        # Load signup data
        df_signup = read_file_safely(signup_file, signup_file.name)
        
        # Load registration data  
        df_registration = read_file_safely(registration_file, registration_file.name)
        
        # Show file info
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"📊 **Signup Data**: {len(df_signup)} rows loaded from {signup_file.name}")
        with col2:
            st.write(f"👥 **Registration Data**: {len(df_registration)} rows loaded from {registration_file.name}")
        
        st.success("✅ Files processed successfully!")
        
        # Process data
        with st.spinner("Processing data..."):
            # Extract team members from registration data
            df_team_members = process_registration_data(df_registration)
            
            # Match signup users with team members
            df_result = match_users(df_signup, df_team_members)
        
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
        

        # Team-wise breakdown

        # Download section
        st.subheader("💾 Download Results")
        
        # Create downloadable file
        excel_data = create_downloadable_excel(df_result)
        
        st.download_button(
            label="📥 Download Complete Report (Excel)",
            data=excel_data,
            file_name=f"team_registration_report_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        if registered_in_team > 0:
            st.subheader("🏆 Team-wise Breakdown")
            team_breakdown = df_result[df_result['Registered_Team'] == 'Yes'].groupby(['Team_Name', 'Team_Role']).size().reset_index(name='Count')
            
            for team in df_result[df_result['Registered_Team'] == 'Yes']['Team_Name'].unique():
                team_data = df_result[df_result['Team_Name'] == team]
                with st.expander(f"Team: {team} ({len(team_data)} members)"):
                    st.dataframe(team_data[['Full Name', 'Email ID', 'Phone Number', 'Team_Role', 'University Name']], 
                               use_container_width=True)
        
    except Exception as e:
        st.error(f"❌ Error processing files: {str(e)}")
        st.write("Please ensure your files have the correct format and column names.")

else:
    st.info("👆 Please upload both signup and registration files to begin analysis")
    
# Footer