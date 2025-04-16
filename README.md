# Real Estate Presentation Booking System

This is a Streamlit application for booking presentation slots for real estate development companies. The application allows companies to book 30-minute presentation slots on Tuesdays and Saturdays from 12:00 PM to 12:30 PM.

## Features

- Book new presentation slots
- Reschedule existing bookings
- Cancel bookings
- View all bookings
- Automatic slot generation for Tuesdays and Saturdays

## Installation

1. Clone this repository
2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```
3. Set up Google Sheets API credentials (see below)
4. Run the application:
   ```
   streamlit run app.py
   ```

## Google Sheets API Setup

To use this application, you need to set up Google Sheets API credentials:

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable the Google Sheets API and Google Drive API
4. Create a service account and download the JSON credentials file
5. Place the credentials file in the `credentials` directory as `google_sheets_creds.json`

## Project Structure

```
real_estate_booking_app/
│
├── app.py                  # Main application file
├── config.py               # Configuration settings
├── utils.py                # Utility functions
├── sheets_api.py           # Google Sheets API functions
│
├── pages/                  # Application pages
│   ├── booking.py          # New booking page
│   ├── manage.py           # Manage bookings page
│   ├── reschedule.py       # Reschedule booking page
│   └── cancel.py           # Cancel booking page
│
├── assets/                 # Static assets
│   ├── logo.png            # Company logo
│   ├── styles.css          # CSS styles
│   └── favicon.ico         # Website favicon
│
├── credentials/            # API credentials
│   └── google_sheets_creds.json  # Google Sheets API credentials
│
└── requirements.txt        # Required packages
```

## Deployment

This application can be deployed to Streamlit Cloud:

1. Push the code to GitHub
2. Connect your GitHub repository to Streamlit Cloud
3. Deploy the application

## License

This project is licensed under the MIT License - see the LICENSE file for details.
