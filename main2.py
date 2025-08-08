import streamlit as st
import pandas as pd

st.set_page_config(page_title="Team Registration Analysis", layout="wide")

st.title("📊 Team Registration Data Dashboard")

# File upload
uploaded_file = st.file_uploader("Upload your registration CSV", type=["csv"])

if uploaded_file is not None:
    # Load Data
    df = pd.read_csv(uploaded_file)
    
    # Convert dates safely
    if "Registration_Date" in df.columns:
        df["Registration_Date"] = pd.to_datetime(df["Registration_Date"], errors="coerce")

    # Remove duplicates
    df_clean = df.drop_duplicates(subset=["Team Name", "Team Leader Name"])

    # Find missing PPT
    missing_ppt = df_clean[df_clean["PPT Link / File Name"].isna()]

    # Theme counts
    theme_counts = df_clean["Theme"].value_counts()

    # Unique universities
    unique_unis = df_clean["Team Leader University Name with address"].nunique()

    # Registrations over time
    if "Registration_Date" in df_clean.columns:
        registrations_by_date = df_clean.groupby(df_clean["Registration_Date"].dt.date).size()
    else:
        registrations_by_date = pd.Series()

    # Members per team
    member_cols = [col for col in df_clean.columns if "Team Member" in col and "Name" in col]
    df_clean["Team Size"] = df_clean[member_cols].notna().sum(axis=1) + 1
    avg_team_size = df_clean["Team Size"].mean()

    # Filters
    st.sidebar.header("🔍 Filters")
    theme_filter = st.sidebar.multiselect("Select Theme(s)", options=df_clean["Theme"].dropna().unique())
    uni_filter = st.sidebar.multiselect("Select University(s)", options=df_clean["Team Leader University Name with address"].dropna().unique())

    filtered_df = df_clean.copy()
    if theme_filter:
        filtered_df = filtered_df[filtered_df["Theme"].isin(theme_filter)]
    if uni_filter:
        filtered_df = filtered_df[filtered_df["Team Leader University Name with address"].isin(uni_filter)]

    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📄 Data Preview", "📊 Charts", "⚠ Missing PPT", "📥 Downloads"])

    # Tab 1 - Data Preview
    with tab1:
        st.subheader("📌 Key Stats")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Teams", len(filtered_df))
        col2.metric("Unique Universities", filtered_df["Team Leader University Name with address"].nunique())
        col3.metric("Avg Team Size", f"{avg_team_size:.2f}")
        col4.metric("Missing PPT", len(missing_ppt))

        st.subheader("📄 Filtered Data")
        st.dataframe(filtered_df)

    # Tab 2 - Charts
    with tab2:
        st.subheader("📊 Teams per Theme")
        st.bar_chart(filtered_df["Theme"].value_counts())

        if not registrations_by_date.empty:
            st.subheader("📅 Registrations Over Time")
            st.line_chart(registrations_by_date)

    # Tab 3 - Missing PPT
    with tab3:
        st.subheader("⚠ Teams Missing PPT")
        def highlight_missing(s):
            return ['background-color: #ffcccc' if pd.isna(v) else '' for v in s]
        
        st.dataframe(missing_ppt.style.apply(highlight_missing, subset=["PPT Link / File Name"]))

    # Tab 4 - Downloads
    with tab4:
        st.subheader("📥 Download Data")
        st.download_button("Download Cleaned CSV", df_clean.to_csv(index=False), "registrations_cleaned.csv", "text/csv")
        st.download_button("Download Missing PPT List", missing_ppt.to_csv(index=False), "teams_missing_ppt.csv", "text/csv")
