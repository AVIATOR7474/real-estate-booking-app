"""
Enhanced Google Sheets Integration for Al-Hayah Real Estate Development Company Appointment Booking App

This module handles all interactions with Google Sheets, which serves as the database
for the appointment booking application. It supports both importing data from and
exporting data to Google Sheets.
"""

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from datetime import datetime
import json
import os

class SheetsIntegration:
    def __init__(self, credentials_path="C:\\Users\\DELL\\Documents\\Python\\Project\\al-hayah-booking-app\\credentials.json"):
        """
        Initialize the Google Sheets integration.
        
        Args:
            credentials_path: Path to the Google Sheets API credentials JSON file.
                             If None, will look for credentials in environment or create dummy data.
        """
        self.scope = ['https://spreadsheets.google.com/feeds',
                     'https://www.googleapis.com/auth/drive']
        
        self.credentials_path = credentials_path
        self.client = None
        self.sheet = None
        self.worksheet = None
        
        # For development without actual credentials
        self.use_dummy_data = credentials_path is None
        self.dummy_data = []
        
        # Initialize the connection
        self.initialize_connection()
        
    def initialize_connection(self):
        """Initialize connection to Google Sheets or set up dummy data."""
        if not self.use_dummy_data and os.path.exists(self.credentials_path):
            try:
                # Connect to Google Sheets
                credentials = ServiceAccountCredentials.from_json_keyfile_name(
                    self.credentials_path, self.scope)
                self.client = gspread.authorize(credentials)
                
                # Open the spreadsheet - you'll need to replace with your actual spreadsheet name
                self.sheet = self.client.open("Al-Hayah Appointment Bookings")
                
                # Select the first worksheet
                self.worksheet = self.sheet.get_worksheet(0)
                
                # If worksheet doesn't exist or is empty, initialize it with headers
                if not self.worksheet or len(self.worksheet.get_all_values()) == 0:
                    self.initialize_worksheet()
                    
                print("Successfully connected to Google Sheets")
                return True
            except Exception as e:
                print(f"Error connecting to Google Sheets: {e}")
                self.use_dummy_data = True
        else:
            print("Using dummy data for development")
            self.use_dummy_data = True
            
            # Initialize dummy data with headers
            self.dummy_data = [
                ["ID", "Company Name", "Project Name", "Area", "Presentation Date", 
                 "Time", "Developer Representative", "Status", "Created At", "Updated At"]
            ]
            
            # Create sample data for development
            self.create_sample_data()
        
        return False
    
    def initialize_worksheet(self):
        """Initialize the worksheet with headers if it doesn't exist."""
        headers = ["ID", "Company Name", "Project Name", "Area", "Presentation Date", 
                  "Time", "Developer Representative", "Status", "Created At", "Updated At"]
        
        if not self.use_dummy_data:
            # Create a new worksheet if it doesn't exist
            if not self.worksheet:
                self.worksheet = self.sheet.add_worksheet(title="Appointments", rows=1000, cols=10)
            
            # Add headers
            self.worksheet.update('A1:J1', [headers])
            
            # Format headers (make bold, freeze row)
            self.worksheet.format('A1:J1', {'textFormat': {'bold': True}})
            self.worksheet.freeze(rows=1)
        
    def get_all_appointments(self):
        """
        Get all appointments from the Google Sheet.
        
        Returns:
            pandas.DataFrame: DataFrame containing all appointments
        """
        if not self.use_dummy_data:
            try:
                # Get all data from the worksheet
                data = self.worksheet.get_all_values()
                
                # Convert to DataFrame
                if len(data) > 1:  # If there's data beyond headers
                    df = pd.DataFrame(data[1:], columns=data[0])
                    return df
                else:
                    # Return empty DataFrame with correct columns
                    return pd.DataFrame(columns=data[0])
            except Exception as e:
                print(f"Error getting appointments: {e}")
                return pd.DataFrame()
        else:
            # Return dummy data
            if len(self.dummy_data) > 1:  # If there's data beyond headers
                df = pd.DataFrame(self.dummy_data[1:], columns=self.dummy_data[0])
                return df
            else:
                # Return empty DataFrame with correct columns
                return pd.DataFrame(columns=self.dummy_data[0])
    
    def add_appointment(self, company_name, project_name, area, presentation_date, 
                       time, developer_representative):
        """
        Add a new appointment to the Google Sheet.
        
        Args:
            company_name: Name of the real estate development company
            project_name: Name of the project
            area: Area/location of the project
            presentation_date: Date of the presentation (YYYY-MM-DD)
            time: Time of the presentation (HH:MM)
            developer_representative: Name of the developer representative
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Generate a unique ID
            now = datetime.now()
            appointment_id = now.strftime("%Y%m%d%H%M%S")
            
            # Create new row
            new_row = [
                appointment_id,
                company_name,
                project_name,
                area,
                presentation_date,
                time,
                developer_representative,
                "Confirmed",  # Initial status
                now.strftime("%Y-%m-%d %H:%M:%S"),  # Created at
                now.strftime("%Y-%m-%d %H:%M:%S")   # Updated at
            ]
            
            if not self.use_dummy_data:
                # Append to worksheet
                self.worksheet.append_row(new_row)
            else:
                # Append to dummy data
                self.dummy_data.append(new_row)
                
            return True
        except Exception as e:
            print(f"Error adding appointment: {e}")
            return False
    
    def update_appointment(self, appointment_id, **kwargs):
        """
        Update an existing appointment.
        
        Args:
            appointment_id: Unique ID of the appointment to update
            **kwargs: Fields to update (company_name, project_name, area, 
                     presentation_date, time, developer_representative, status)
                     
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not self.use_dummy_data:
                # Find the row with the matching ID
                cell = self.worksheet.find(appointment_id)
                if not cell:
                    return False
                
                row_num = cell.row
                
                # Get the current row data
                row_data = self.worksheet.row_values(row_num)
                
                # Update fields
                if 'company_name' in kwargs:
                    self.worksheet.update_cell(row_num, 2, kwargs['company_name'])
                if 'project_name' in kwargs:
                    self.worksheet.update_cell(row_num, 3, kwargs['project_name'])
                if 'area' in kwargs:
                    self.worksheet.update_cell(row_num, 4, kwargs['area'])
                if 'presentation_date' in kwargs:
                    self.worksheet.update_cell(row_num, 5, kwargs['presentation_date'])
                if 'time' in kwargs:
                    self.worksheet.update_cell(row_num, 6, kwargs['time'])
                if 'developer_representative' in kwargs:
                    self.worksheet.update_cell(row_num, 7, kwargs['developer_representative'])
                if 'status' in kwargs:
                    self.worksheet.update_cell(row_num, 8, kwargs['status'])
                
                # Update the 'updated_at' timestamp
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.worksheet.update_cell(row_num, 10, now)
            else:
                # Update dummy data
                for i, row in enumerate(self.dummy_data):
                    if i > 0 and row[0] == appointment_id:  # Skip header row
                        if 'company_name' in kwargs:
                            row[1] = kwargs['company_name']
                        if 'project_name' in kwargs:
                            row[2] = kwargs['project_name']
                        if 'area' in kwargs:
                            row[3] = kwargs['area']
                        if 'presentation_date' in kwargs:
                            row[4] = kwargs['presentation_date']
                        if 'time' in kwargs:
                            row[5] = kwargs['time']
                        if 'developer_representative' in kwargs:
                            row[6] = kwargs['developer_representative']
                        if 'status' in kwargs:
                            row[7] = kwargs['status']
                        
                        # Update the 'updated_at' timestamp
                        row[9] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        break
            
            return True
        except Exception as e:
            print(f"Error updating appointment: {e}")
            return False
    
    def cancel_appointment(self, appointment_id):
        """
        Cancel an appointment by setting its status to 'Cancelled'.
        
        Args:
            appointment_id: Unique ID of the appointment to cancel
            
        Returns:
            bool: True if successful, False otherwise
        """
        return self.update_appointment(appointment_id, status="Cancelled")
    
    def reschedule_appointment(self, appointment_id, new_date, new_time):
        """
        Reschedule an appointment to a new date and time.
        
        Args:
            appointment_id: Unique ID of the appointment to reschedule
            new_date: New presentation date (YYYY-MM-DD)
            new_time: New presentation time (HH:MM)
            
        Returns:
            bool: True if successful, False otherwise
        """
        return self.update_appointment(
            appointment_id, 
            presentation_date=new_date,
            time=new_time,
            status="Rescheduled"
        )
    
    def get_appointment_by_id(self, appointment_id):
        """
        Get a specific appointment by ID.
        
        Args:
            appointment_id: Unique ID of the appointment
            
        Returns:
            dict: Appointment data or None if not found
        """
        if not self.use_dummy_data:
            try:
                # Find the row with the matching ID
                cell = self.worksheet.find(appointment_id)
                if not cell:
                    return None
                
                row_num = cell.row
                
                # Get the row data
                row_data = self.worksheet.row_values(row_num)
                
                # Get headers
                headers = self.worksheet.row_values(1)
                
                # Create dictionary
                appointment = dict(zip(headers, row_data))
                return appointment
            except Exception as e:
                print(f"Error getting appointment: {e}")
                return None
        else:
            # Search dummy data
            for i, row in enumerate(self.dummy_data):
                if i > 0 and row[0] == appointment_id:  # Skip header row
                    # Create dictionary
                    appointment = dict(zip(self.dummy_data[0], row))
                    return appointment
            
            return None
    
    def get_appointments_by_date(self, date):
        """
        Get all appointments for a specific date.
        
        Args:
            date: Date to filter by (YYYY-MM-DD)
            
        Returns:
            pandas.DataFrame: DataFrame containing filtered appointments
        """
        # Get all appointments
        df = self.get_all_appointments()
        
        # Filter by date
        if not df.empty:
            return df[df['Presentation Date'] == date]
        
        return df
    
    def is_slot_available(self, date, time):
        """
        Check if a specific date and time slot is available.
        
        Args:
            date: Date to check (YYYY-MM-DD)
            time: Time to check (HH:MM)
            
        Returns:
            bool: True if slot is available, False otherwise
        """
        # Get appointments for the date
        df = self.get_appointments_by_date(date)
        
        # Check if there's an appointment at the specified time
        if not df.empty:
            # Filter by time and active statuses
            active_statuses = ['Confirmed', 'Rescheduled']
            filtered = df[(df['Time'] == time) & (df['Status'].isin(active_statuses))]
            
            # If there are any active appointments at this time, the slot is not available
            return filtered.empty
        
        # No appointments for this date, so the slot is available
        return True
    
    def import_appointments_from_sheet(self):
        """
        Import appointments directly from Google Sheets.
        This function is used when data is entered directly into the Google Sheet
        and needs to be displayed in the Streamlit app.
        
        Returns:
            pandas.DataFrame: DataFrame containing all appointments from the sheet
        """
        if not self.use_dummy_data:
            try:
                # Refresh the connection to get the latest data
                credentials = ServiceAccountCredentials.from_json_keyfile_name(
                    self.credentials_path, self.scope)
                self.client = gspread.authorize(credentials)
                self.sheet = self.client.open("Al-Hayah Appointment Bookings")
                self.worksheet = self.sheet.get_worksheet(0)
                
                # Get all data from the worksheet
                data = self.worksheet.get_all_values()
                
                # Convert to DataFrame
                if len(data) > 1:  # If there's data beyond headers
                    df = pd.DataFrame(data[1:], columns=data[0])
                    return df
                else:
                    # Return empty DataFrame with correct columns
                    return pd.DataFrame(columns=data[0])
            except Exception as e:
                print(f"Error importing appointments from sheet: {e}")
                return pd.DataFrame()
        else:
            # Return dummy data
            if len(self.dummy_data) > 1:  # If there's data beyond headers
                df = pd.DataFrame(self.dummy_data[1:], columns=self.dummy_data[0])
                return df
            else:
                # Return empty DataFrame with correct columns
                return pd.DataFrame(columns=self.dummy_data[0])
    
    def get_paginated_appointments(self, page=1, per_page=12, status_filter=None):
        """
        Get appointments with pagination support.
        
        Args:
            page: Page number (1-based)
            per_page: Number of appointments per page
            status_filter: Optional filter for appointment status
            
        Returns:
            tuple: (DataFrame of appointments for the current page, total number of pages)
        """
        # Get all appointments
        df = self.get_all_appointments()
        
        if df.empty:
            return df, 0
        
        # Apply status filter if provided
        if status_filter:
            df = df[df['Status'] == status_filter]
        
        # Calculate total pages
        total_records = len(df)
        total_pages = (total_records + per_page - 1) // per_page  # Ceiling division
        
        # Ensure page is within bounds
        page = max(1, min(page, total_pages)) if total_pages > 0 else 1
        
        # Calculate start and end indices
        start_idx = (page - 1) * per_page
        end_idx = min(start_idx + per_page, total_records)
        
        # Return the slice for the current page
        return df.iloc[start_idx:end_idx], total_pages
    
    def create_sample_data(self):
        """Create sample data for testing purposes."""
        # Only create sample data if we're using dummy data and it's empty
        if self.use_dummy_data and len(self.dummy_data) <= 1:
            sample_data = [
                {
                    'company_name': 'Al-Manar Development',
                    'project_name': 'Oasis Gardens',
                    'area': 'New Cairo',
                    'presentation_date': '2025-04-20',  # Saturday
                    'time': '12:00',
                    'developer_representative': 'Ahmed Hassan'
                },
                {
                    'company_name': 'Palm Hills',
                    'project_name': 'Palm Valley',
                    'area': '6th of October',
                    'presentation_date': '2025-04-23',  # Tuesday
                    'time': '12:00',
                    'developer_representative': 'Sara Mahmoud'
                },
                {
                    'company_name': 'SODIC',
                    'project_name': 'The Estates',
                    'area': 'Sheikh Zayed',
                    'presentation_date': '2025-04-27',  # Saturday
                    'time': '12:00',
                    'developer_representative': 'Mohamed Ali'
                },
                {
                    'company_name': 'Talaat Moustafa Group',
                    'project_name': 'Madinaty',
                    'area': 'New Cairo',
                    'presentation_date': '2025-04-30',  # Tuesday
                    'time': '12:00',
                    'developer_representative': 'Laila Ahmed'
                },
                {
                    'company_name': 'Emaar Misr',
                    'project_name': 'Mivida',
                    'area': 'New Cairo',
                    'presentation_date': '2025-05-04',  # Saturday
                    'time': '12:00',
                    'developer_representative': 'Khaled Ibrahim'
                },
                {
                    'company_name': 'Hyde Park',
                    'project_name': 'Hyde Park New Cairo',
                    'area': 'New Cairo',
                    'presentation_date': '2025-05-07',  # Tuesday
                    'time': '12:00',
                    'developer_representative': 'Nour Saleh'
                },
                {
                    'company_name': 'Mountain View',
                    'project_name': 'iCity',
                    'area': 'New Cairo',
                    'presentation_date': '2025-05-11',  # Saturday
                    'time': '12:00',
                    'developer_representative': 'Tarek Fouad'
                },
                {
                    'company_name': 'Madinet Nasr Housing',
                    'project_name': 'Taj City',
                    'area': 'New Cairo',
                    'presentation_date': '2025-05-14',  # Tuesday
                    'time': '12:00',
                    'developer_representative': 'Heba Mahmoud'
                },
                {
                    'company_name': 'MNHD',
                    'project_name': 'Sarai',
                    'area': 'New Cairo',
                    'presentation_date': '2025-05-18',  # Saturday
                    'time': '12:00',
                    'developer_representative': 'Omar Nabil'
                },
                {
                    'company_name': 'Misr Italia Properties',
                    'project_name': 'IL Bosco',
                    'area': 'New Administrative Capital',
                    'presentation_date': '2025-05-21',  # Tuesday
                    'time': '12:00',
                    'developer_representative': 'Dina Samir'
                },
                {
                    'company_name': 'Inertia',
                    'project_name': 'Joulz',
                    'area': 'Sheikh Zayed',
                    'presentation_date': '2025-05-25',  # Saturday
                    'time': '12:00',
                    'developer_representative': 'Amr Hossam'
                },
                {
                    'company_name': 'Memaar Al Morshedy',
                    'project_name': 'Skyline',
                    'area': 'New Cairo',
                    'presentation_date': '2025-05-28',  # Tuesday
                    'time': '12:00',
                    'developer_representative': 'Rania Kamel'
                },
                {
                    'company_name': 'Orascom Development',
                    'project_name': 'O West',
                    'area': '6th of October',
                    'presentation_date': '2025-06-01',  # Saturday
                    'time': '12:00',
                    'developer_representative': 'Mostafa Sherif'
                },
                {
                    'company_name': 'Arkan Palm',
                    'project_name': 'Arkan Plaza',
                    'area': 'Sheikh Zayed',
                    'presentation_date': '2025-06-04',  # Tuesday
                    'time': '12:00',
                    'developer_representative': 'Yasmin Adel'
                },
                {
                    'company_name': 'Sabbour Developments',
                    'project_name': 'Mustakbal City',
                    'area': 'New Cairo',
                    'presentation_date': '2025-06-08',  # Saturday
                    'time': '12:00',
                    'developer_representative': 'Karim Sabbour'
                }
            ]
            
            for appointment in sample_data:
                self.add_appointment(
                    appointment['company_name'],
                    appointment['project_name'],
                    appointment['area'],
                    appointment['presentation_date'],
                    appointment['time'],
                    appointment['developer_representative']
                )
            
            print("Sample data created successfully")

# For testing
if __name__ == "__main__":
    sheets = SheetsIntegration()
    sheets.create_sample_data()
    print(sheets.get_all_appointments())
