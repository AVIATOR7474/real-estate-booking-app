import streamlit as st

st.set_page_config(
    page_title="Real Estate Presentation Booking App - Deployment Guide",
    page_icon="🏢",
    layout="wide"
)

st.title("Real Estate Presentation Booking App - Deployment Guide")

st.markdown("""
## How to Deploy This Application

This guide will help you deploy the Real Estate Presentation Booking application to GitHub and Streamlit Cloud.

### Prerequisites

1. A GitHub account
2. A Streamlit Cloud account
3. Google Sheets API credentials

### Step 1: Set Up Google Sheets API

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable the Google Sheets API and Google Drive API
4. Create a service account and download the JSON credentials file
5. Place the credentials file in the `credentials` directory as `google_sheets_creds.json`

### Step 2: Deploy to GitHub

1. Create a new repository on GitHub
2. Initialize Git in your local project folder:
   ```bash
   cd real_estate_booking_app
   git init
   ```
3. Add your files to Git:
   ```bash
   git add .
   ```
4. Commit your changes:
   ```bash
   git commit -m "Initial commit"
   ```
5. Link your local repository to GitHub:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/real-estate-booking-app.git
   ```
6. Push your code to GitHub:
   ```bash
   git push -u origin main
   ```

### Step 3: Deploy to Streamlit Cloud

1. Go to [Streamlit Cloud](https://streamlit.io/cloud)
2. Sign in with your GitHub account
3. Click "New app"
4. Select your repository, branch, and main file (app.py)
5. Click "Deploy"
6. Add your Google Sheets credentials as a secret in the Streamlit Cloud dashboard

### Step 4: Configure Secrets

In Streamlit Cloud:

1. Go to your app settings
2. Click on "Secrets"
3. Add your Google Sheets credentials as a JSON secret

### Step 5: Test Your Deployed Application

1. Once deployed, Streamlit Cloud will provide a URL for your application
2. Open the URL in your browser to test the application
3. Verify that all features are working correctly

### Troubleshooting

If you encounter any issues:

1. Check the Streamlit Cloud logs
2. Verify your Google Sheets API credentials
3. Ensure all dependencies are listed in requirements.txt
""")

st.success("Follow these steps to deploy your application to GitHub and Streamlit Cloud!")

# Add a button to download the deployment guide
deployment_guide = """
# Real Estate Presentation Booking App - Deployment Guide

## How to Deploy This Application

This guide will help you deploy the Real Estate Presentation Booking application to GitHub and Streamlit Cloud.

### Prerequisites

1. A GitHub account
2. A Streamlit Cloud account
3. Google Sheets API credentials

### Step 1: Set Up Google Sheets API

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable the Google Sheets API and Google Drive API
4. Create a service account and download the JSON credentials file
5. Place the credentials file in the `credentials` directory as `google_sheets_creds.json`

### Step 2: Deploy to GitHub

1. Create a new repository on GitHub
2. Initialize Git in your local project folder:
   ```bash
   cd real_estate_booking_app
   git init
   ```
3. Add your files to Git:
   ```bash
   git add .
   ```
4. Commit your changes:
   ```bash
   git commit -m "Initial commit"
   ```
5. Link your local repository to GitHub:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/real-estate-booking-app.git
   ```
6. Push your code to GitHub:
   ```bash
   git push -u origin main
   ```

### Step 3: Deploy to Streamlit Cloud

1. Go to [Streamlit Cloud](https://streamlit.io/cloud)
2. Sign in with your GitHub account
3. Click "New app"
4. Select your repository, branch, and main file (app.py)
5. Click "Deploy"
6. Add your Google Sheets credentials as a secret in the Streamlit Cloud dashboard

### Step 4: Configure Secrets

In Streamlit Cloud:

1. Go to your app settings
2. Click on "Secrets"
3. Add your Google Sheets credentials as a JSON secret

### Step 5: Test Your Deployed Application

1. Once deployed, Streamlit Cloud will provide a URL for your application
2. Open the URL in your browser to test the application
3. Verify that all features are working correctly

### Troubleshooting

If you encounter any issues:

1. Check the Streamlit Cloud logs
2. Verify your Google Sheets API credentials
3. Ensure all dependencies are listed in requirements.txt
"""

with open("deployment_guide.md", "w") as f:
    f.write(deployment_guide)

st.download_button(
    label="Download Deployment Guide",
    data=deployment_guide,
    file_name="deployment_guide.md",
    mime="text/markdown"
)
