"""
Al-Hayah Real Estate Development Company - Appointment Booking App

This Streamlit application allows booking presentation appointments for real estate developers.
Features include booking, rescheduling, and canceling appointments.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import calendar
import os
import sys
from PIL import Image

# Add the current directory to the path to import local modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from sheets_integration import SheetsIntegration

# Import logo utilities from the root directory instead of assets folder
from logo_utils import get_logo_as_base64

# Set page configuration
st.set_page_config(
    page_title="Al-Hayah Appointment Booking",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state variables if they don't exist
if 'view' not in st.session_state:
    st.session_state.view = 'calendar'  # Default view
if 'selected_date' not in st.session_state:
    st.session_state.selected_date = None
if 'edit_appointment_id' not in st.session_state:
    st.session_state.edit_appointment_id = None
if 'show_success' not in st.session_state:
    st.session_state.show_success = False
if 'success_message' not in st.session_state:
    st.session_state.success_message = ""
if 'current_page' not in st.session_state:
    st.session_state.current_page = 1
if 'appointments_per_page' not in st.session_state:
    st.session_state.appointments_per_page = 12
if 'current_status_filter' not in st.session_state:
    st.session_state.current_status_filter = None
if 'data_source' not in st.session_state:
    st.session_state.data_source = 'app'  # 'app' or 'sheet'

# Initialize Google Sheets integration
@st.cache_resource
def get_sheets_integration():
    """Get or create a cached instance of SheetsIntegration."""
    # Path to credentials file - set to None for development with dummy data
    credentials_path = None
    if os.path.exists('credentials.json'):
        credentials_path = 'credentials.json'
    
    return SheetsIntegration(credentials_path)

sheets = get_sheets_integration()

# Custom CSS for styling
def load_css():
    """Load custom CSS styles."""
    st.markdown("""
    <style>
        /* Main container styling */
        .main {
            padding: 1rem;
        }
        
        /* Header styling */
        .header-container {
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 2rem;
            flex-direction: column;
        }
        
        /* Logo styling */
        .logo-container {
            display: flex;
            justify-content: center;
            margin-bottom: 1rem;
        }
        .logo-image {
            height: 100px;
        }
        
        /* Card styling */
        .card {
            border-radius: 10px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            background-color: #f8f9fa;
            border-left: 5px solid #008080;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .card-title {
            color: #008080;
            font-size: 1.2rem;
            font-weight: bold;
            margin-bottom: 0.5rem;
        }
        .card-subtitle {
            color: #daa520;
            font-size: 1rem;
            margin-bottom: 0.5rem;
        }
        .card-content {
            margin-bottom: 0.5rem;
        }
        .card-footer {
            display: flex;
            justify-content: space-between;
            margin-top: 1rem;
        }
        
        /* Status badges */
        .badge {
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-size: 0.8rem;
            font-weight: bold;
        }
        .badge-confirmed {
            background-color: #d4edda;
            color: #155724;
        }
        .badge-cancelled {
            background-color: #f8d7da;
            color: #721c24;
        }
        .badge-rescheduled {
            background-color: #fff3cd;
            color: #856404;
        }
        
        /* Calendar styling */
        .calendar-day {
            text-align: center;
            padding: 1rem;
            border-radius: 5px;
            margin: 0.25rem;
            cursor: pointer;
        }
        .calendar-day-available {
            background-color: #d4edda;
            color: #155724;
        }
        .calendar-day-unavailable {
            background-color: #f8d7da;
            color: #721c24;
        }
        .calendar-day-selected {
            background-color: #008080;
            color: white;
        }
        
        /* Success message */
        .success-message {
            padding: 1rem;
            background-color: #d4edda;
            color: #155724;
            border-radius: 5px;
            margin-bottom: 1rem;
        }
        
        /* Form styling */
        .form-container {
            background-color: #f8f9fa;
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        /* Tabs styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 2rem;
        }
        .stTabs [data-baseweb="tab"] {
            height: 4rem;
            white-space: pre-wrap;
            background-color: white;
            border-radius: 4px 4px 0 0;
            gap: 1rem;
            padding-top: 10px;
            padding-bottom: 10px;
        }
        .stTabs [aria-selected="true"] {
            background-color: #008080;
            color: white;
        }
        
        /* Pagination styling */
        .pagination {
            display: flex;
            justify-content: center;
            margin-top: 1rem;
            margin-bottom: 1rem;
        }
        .pagination-info {
            text-align: center;
            margin-bottom: 0.5rem;
            color: #6c757d;
        }
        
        /* Data source toggle */
        .data-source-toggle {
            display: flex;
            justify-content: center;
            margin-bottom: 1rem;
        }
        .data-source-toggle button {
            margin: 0 0.5rem;
        }
    </style>
    """, unsafe_allow_html=True)

# Display logo and header
def display_header():
    """Display the application header with logo."""
    logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "logo.png")
    
    if os.path.exists(logo_path):
        logo = Image.open(logo_path)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image(logo, width=300)
    else:
        # Use base64 encoded logo as fallback
        logo_base64 = get_logo_as_base64()
        st.markdown(f"""
        <div class="logo-container">
            <img src="{logo_base64}" class="logo-image">
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<h1 style='text-align: center; color: #008080;'>Presentation Appointment Booking</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #daa520; font-size: 1.2rem;'>Schedule, manage, and track real estate project presentations</p>", unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)

# Generate available dates (only Saturdays and Tuesdays)
def get_available_dates(num_weeks=4):
    """
    Generate a list of available dates (Saturdays and Tuesdays) for the next few weeks.
    
    Args:
        num_weeks: Number of weeks to generate dates for
        
    Returns:
        list: List of date objects
    """
    today = datetime.now().date()
    dates = []
    
    # Start from today and go forward
    current_date = today
    
    # Generate dates for the specified number of weeks
    for _ in range(num_weeks * 7):  # 7 days per week
        # Check if the day is Saturday (5) or Tuesday (1)
        if current_date.weekday() == 5 or current_date.weekday() == 1:
            # Only include dates from today onwards
            if current_date >= today:
                dates.append(current_date)
        
        # Move to the next day
        current_date += timedelta(days=1)
    
    return dates

# Format date for display
def format_date(date_obj, include_day=True):
    """
    Format a date object for display.
    
    Args:
        date_obj: Date object to format
        include_day: Whether to include the day name
        
    Returns:
        str: Formatted date string
    """
    if include_day:
        return date_obj.strftime("%A, %d %B %Y")
    return date_obj.strftime("%d %B %Y")

# Check if a date is available for booking
def is_date_available(date_obj):
    """
    Check if a date is available for booking.
    
    Args:
        date_obj: Date object to check
        
    Returns:
        bool: True if the date is available, False otherwise
    """
    # Convert date object to string format used in the sheet
    date_str = date_obj.strftime("%Y-%m-%d")
    
    # Check if the slot is available
    return sheets.is_slot_available(date_str, "12:00")

# Display calendar view
def display_calendar_view():
    """Display the calendar view for selecting dates."""
    st.markdown("### Select a Date for Presentation")
    st.markdown("Presentations are available on **Saturdays** and **Tuesdays** at **12:00 PM** for 30 minutes.")
    
    # Get available dates
    available_dates = get_available_dates(num_weeks=4)
    
    # Group dates by week for better display
    weeks = {}
    for date in available_dates:
        # Get the week number
        week_num = date.isocalendar()[1]
        if week_num not in weeks:
            weeks[week_num] = []
        weeks[week_num].append(date)
    
    # Display weeks
    for week_num, dates in weeks.items():
        cols = st.columns(len(dates))
        for i, date in enumerate(dates):
            # Check if the date is available
            is_available = is_date_available(date)
            
            # Check if this is the selected date
            is_selected = st.session_state.selected_date == date
            
            # Determine the CSS class
            if is_selected:
                css_class = "calendar-day calendar-day-selected"
            elif is_available:
                css_class = "calendar-day calendar-day-available"
            else:
                css_class = "calendar-day calendar-day-unavailable"
            
            # Display the date
            with cols[i]:
                day_name = date.strftime("%A")
                day_num = date.strftime("%d")
                month = date.strftime("%b")
                
                # Create a clickable date card
                if st.button(
                    f"{day_name}\n{day_num} {month}",
                    key=f"date_{date}",
                    disabled=not is_available and not is_selected,
                    use_container_width=True
                ):
                    # Update the selected date
                    if is_selected:
                        st.session_state.selected_date = None
                    else:
                        st.session_state.selected_date = date
                    
                    # Rerun the app to update the UI
                    st.rerun()

# Display booking form
def display_booking_form():
    """Display the booking form for the selected date."""
    if st.session_state.selected_date:
        st.markdown(f"### Book Presentation for {format_date(st.session_state.selected_date)}")
        st.markdown("Please fill in the details below to book your presentation slot.")
        
        # Create a form
        with st.form(key="booking_form"):
            # Company details
            company_name = st.text_input("Company Name", key="company_name")
            project_name = st.text_input("Project Name", key="project_name")
            area = st.text_input("Area/Location", key="area")
            representative = st.text_input("Developer Representative Name", key="representative")
            
            # Submit button
            submit_button = st.form_submit_button("Book Appointment")
            
            if submit_button:
                # Validate form
                if not company_name or not project_name or not area or not representative:
                    st.error("Please fill in all fields.")
                else:
                    # Format date for the sheet
                    date_str = st.session_state.selected_date.strftime("%Y-%m-%d")
                    
                    # Add the appointment
                    success = sheets.add_appointment(
                        company_name,
                        project_name,
                        area,
                        date_str,
                        "12:00",
                        representative
                    )
                    
                    if success:
                        # Show success message
                        st.session_state.show_success = True
                        st.session_state.success_message = f"Appointment booked successfully for {format_date(st.session_state.selected_date)} at 12:00 PM."
                        
                        # Reset the selected date
                        st.session_state.selected_date = None
                        
                        # Rerun the app to update the UI
                        st.rerun()
                    else:
                        st.error("Failed to book appointment. Please try again.")

# Display appointment card
def display_appointment_card(appointment, index):
    """
    Display an appointment card.
    
    Args:
        appointment: Dictionary containing appointment details
        index: Unique index for this card to avoid duplicate keys
    """
    # Parse the date
    try:
        date_obj = datetime.strptime(appointment['Presentation Date'], "%Y-%m-%d").date()
        formatted_date = format_date(date_obj)
    except:
        formatted_date = appointment['Presentation Date']
    
    # Determine the status badge class
    status = appointment['Status']
    if status == "Confirmed":
        badge_class = "badge badge-confirmed"
    elif status == "Cancelled":
        badge_class = "badge badge-cancelled"
    else:  # Rescheduled
        badge_class = "badge badge-rescheduled"
    
    # Create the card
    st.markdown(f"""
    <div class="card">
        <div class="card-title">{appointment['Company Name']} - {appointment['Project Name']}</div>
        <div class="card-subtitle">{appointment['Area']}</div>
        <div class="card-content">
            <p><strong>Date:</strong> {formatted_date}</p>
            <p><strong>Time:</strong> {appointment['Time']} PM</p>
            <p><strong>Representative:</strong> {appointment['Developer Representative']}</p>
        </div>
        <div class="card-footer">
            <span class="{badge_class}">{status}</span>
            <div>
                <button onclick="document.getElementById('edit_{index}').click()">Edit</button>
                <button onclick="document.getElementById('cancel_{index}').click()">Cancel</button>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Hidden buttons for edit and cancel actions
    if st.button("Edit", key=f"edit_{index}", help="Edit this appointment", type="primary", use_container_width=True):
        st.session_state.edit_appointment_id = appointment['ID']
        st.session_state.view = 'edit'
        st.rerun()
    
    if st.button("Cancel", key=f"cancel_{index}", help="Cancel this appointment", type="secondary", use_container_width=True):
        # Cancel the appointment
        success = sheets.cancel_appointment(appointment['ID'])
        
        if success:
            # Show success message
            st.session_state.show_success = True
            st.session_state.success_message = f"Appointment cancelled successfully."
            
            # Rerun the app to update the UI
            st.rerun()
        else:
            st.error("Failed to cancel appointment. Please try again.")

# Display pagination controls
def display_pagination_controls(total_pages):
    """
    Display pagination controls.
    
    Args:
        total_pages: Total number of pages
    """
    if total_pages <= 1:
        return
    
    # Display pagination info
    st.markdown(f"""
    <div class="pagination-info">
        Page {st.session_state.current_page} of {total_pages}
    </div>
    """, unsafe_allow_html=True)
    
    # Create columns for pagination buttons
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    
    with col1:
        if st.button("⏮️ First", key="first_page", disabled=st.session_state.current_page == 1):
            st.session_state.current_page = 1
            st.rerun()
    
    with col2:
        if st.button("◀️ Previous", key="prev_page", disabled=st.session_state.current_page == 1):
            st.session_state.current_page = max(1, st.session_state.current_page - 1)
            st.rerun()
    
    with col3:
        if st.button("Next ▶️", key="next_page", disabled=st.session_state.current_page == total_pages):
            st.session_state.current_page = min(total_pages, st.session_state.current_page + 1)
            st.rerun()
    
    with col4:
        if st.button("Last ⏭️", key="last_page", disabled=st.session_state.current_page == total_pages):
            st.session_state.current_page = total_pages
            st.rerun()

# Display data source toggle
def display_data_source_toggle():
    """Display toggle for switching between app data and sheet data."""
    st.markdown("### Data Source")
    st.markdown("Choose where to get appointment data from:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📱 App Data", 
                    key="app_data_btn",
                    help="Use data entered through this app",
                    use_container_width=True,
                    type="primary" if st.session_state.data_source == 'app' else "secondary"):
            st.session_state.data_source = 'app'
            st.session_state.current_page = 1  # Reset to first page
            st.rerun()
    
    with col2:
        if st.button("📊 Sheet Data", 
                    key="sheet_data_btn",
                    help="Import data directly from Google Sheets",
                    use_container_width=True,
                    type="primary" if st.session_state.data_source == 'sheet' else "secondary"):
            st.session_state.data_source = 'sheet'
            st.session_state.current_page = 1  # Reset to first page
            st.rerun()
    
    if st.session_state.data_source == 'sheet':
        st.info("📊 Displaying data imported directly from Google Sheets. Any changes made in the sheet will be reflected here.")
    else:
        st.info("📱 Displaying data entered through this app.")
    
    # Add refresh button for sheet data
    if st.session_state.data_source == 'sheet':
        if st.button("🔄 Refresh Data", key="refresh_btn", help="Refresh data from Google Sheets"):
            st.session_state.show_success = True
            st.session_state.success_message = "Data refreshed from Google Sheets."
            st.rerun()

# Display all appointments with pagination
def display_appointments_paginated():
    """Display all appointments with pagination."""
    # Display data source toggle
    display_data_source_toggle()
    
    # Get appointments based on data source
    if st.session_state.data_source == 'sheet':
        # Import data directly from Google Sheets
        df = sheets.import_appointments_from_sheet()
    else:
        # Use data from the app
        df = sheets.get_all_appointments()
    
    if df.empty:
        st.info("No appointments found.")
        return
    
    # Display tabs for different status groups
    tab1, tab2, tab3, tab4 = st.tabs(["All", "Confirmed", "Rescheduled", "Cancelled"])
    
    with tab1:
        # Get paginated appointments for All status
        st.session_state.current_status_filter = None
        appointments_df, total_pages = sheets.get_paginated_appointments(
            page=st.session_state.current_page,
            per_page=st.session_state.appointments_per_page,
            status_filter=None
        )
        
        if not appointments_df.empty:
            # Convert DataFrame to list of dictionaries
            appointments = appointments_df.to_dict('records')
            
            # Display appointments
            for i, appointment in enumerate(appointments):
                display_appointment_card(appointment, f"all_{i}")
            
            # Display pagination controls
            display_pagination_controls(total_pages)
        else:
            st.info("No appointments found.")
    
    with tab2:
        # Get paginated appointments for Confirmed status
        if st.session_state.current_status_filter != 'Confirmed':
            st.session_state.current_status_filter = 'Confirmed'
            st.session_state.current_page = 1  # Reset to first page
        
        appointments_df, total_pages = sheets.get_paginated_appointments(
            page=st.session_state.current_page,
            per_page=st.session_state.appointments_per_page,
            status_filter='Confirmed'
        )
        
        if not appointments_df.empty:
            # Convert DataFrame to list of dictionaries
            appointments = appointments_df.to_dict('records')
            
            # Display appointments
            for i, appointment in enumerate(appointments):
                display_appointment_card(appointment, f"confirmed_{i}")
            
            # Display pagination controls
            display_pagination_controls(total_pages)
        else:
            st.info("No confirmed appointments found.")
    
    with tab3:
        # Get paginated appointments for Rescheduled status
        if st.session_state.current_status_filter != 'Rescheduled':
            st.session_state.current_status_filter = 'Rescheduled'
            st.session_state.current_page = 1  # Reset to first page
        
        appointments_df, total_pages = sheets.get_paginated_appointments(
            page=st.session_state.current_page,
            per_page=st.session_state.appointments_per_page,
            status_filter='Rescheduled'
        )
        
        if not appointments_df.empty:
            # Convert DataFrame to list of dictionaries
            appointments = appointments_df.to_dict('records')
            
            # Display appointments
            for i, appointment in enumerate(appointments):
                display_appointment_card(appointment, f"rescheduled_{i}")
            
            # Display pagination controls
            display_pagination_controls(total_pages)
        else:
            st.info("No rescheduled appointments found.")
    
    with tab4:
        # Get paginated appointments for Cancelled status
        if st.session_state.current_status_filter != 'Cancelled':
            st.session_state.current_status_filter = 'Cancelled'
            st.session_state.current_page = 1  # Reset to first page
        
        appointments_df, total_pages = sheets.get_paginated_appointments(
            page=st.session_state.current_page,
            per_page=st.session_state.appointments_per_page,
            status_filter='Cancelled'
        )
        
        if not appointments_df.empty:
            # Convert DataFrame to list of dictionaries
            appointments = appointments_df.to_dict('records')
            
            # Display appointments
            for i, appointment in enumerate(appointments):
                display_appointment_card(appointment, f"cancelled_{i}")
            
            # Display pagination controls
            display_pagination_controls(total_pages)
        else:
            st.info("No cancelled appointments found.")

# Display edit form
def display_edit_form():
    """Display the form for editing an appointment."""
    if st.session_state.edit_appointment_id:
        # Get the appointment details
        appointment = sheets.get_appointment_by_id(st.session_state.edit_appointment_id)
        
        if appointment:
            st.markdown(f"### Edit Appointment")
            st.markdown("Update the details below and click 'Update Appointment' to save changes.")
            
            # Create a form
            with st.form(key="edit_form"):
                # Company details
                company_name = st.text_input("Company Name", value=appointment['Company Name'])
                project_name = st.text_input("Project Name", value=appointment['Project Name'])
                area = st.text_input("Area/Location", value=appointment['Area'])
                representative = st.text_input("Developer Representative Name", value=appointment['Developer Representative'])
                
                # Get available dates for the dropdown
                available_dates = get_available_dates(num_weeks=8)
                
                # Format dates for the dropdown
                date_options = [format_date(date) for date in available_dates]
                
                # Add the current date to the options if it's not already there
                current_date_obj = datetime.strptime(appointment['Presentation Date'], "%Y-%m-%d").date()
                current_date_str = format_date(current_date_obj)
                if current_date_str not in date_options:
                    date_options.insert(0, current_date_str)
                
                # Date selection
                selected_date_str = st.selectbox("Presentation Date", date_options, index=date_options.index(current_date_str))
                
                # Submit button
                submit_button = st.form_submit_button("Update Appointment")
                
                if submit_button:
                    # Validate form
                    if not company_name or not project_name or not area or not representative:
                        st.error("Please fill in all fields.")
                    else:
                        # Parse the selected date
                        try:
                            selected_date_obj = datetime.strptime(selected_date_str, "%A, %d %B %Y").date()
                            date_str = selected_date_obj.strftime("%Y-%m-%d")
                        except:
                            date_str = appointment['Presentation Date']
                        
                        # Determine if this is a reschedule
                        is_reschedule = date_str != appointment['Presentation Date']
                        
                        if is_reschedule:
                            # Reschedule the appointment
                            success = sheets.reschedule_appointment(
                                st.session_state.edit_appointment_id,
                                date_str,
                                "12:00"
                            )
                        else:
                            # Update the appointment
                            success = sheets.update_appointment(
                                st.session_state.edit_appointment_id,
                                company_name=company_name,
                                project_name=project_name,
                                area=area,
                                developer_representative=representative
                            )
                        
                        if success:
                            # Show success message
                            st.session_state.show_success = True
                            st.session_state.success_message = f"Appointment updated successfully."
                            
                            # Reset the edit appointment ID
                            st.session_state.edit_appointment_id = None
                            
                            # Go back to the appointments view
                            st.session_state.view = 'appointments'
                            
                            # Rerun the app to update the UI
                            st.rerun()
                        else:
                            st.error("Failed to update appointment. Please try again.")
            
            # Cancel button
            if st.button("Cancel", key="cancel_edit", help="Cancel editing", type="secondary"):
                # Reset the edit appointment ID
                st.session_state.edit_appointment_id = None
                
                # Go back to the appointments view
                st.session_state.view = 'appointments'
                
                # Rerun the app to update the UI
                st.rerun()
        else:
            st.error("Appointment not found.")
            
            # Reset the edit appointment ID
            st.session_state.edit_appointment_id = None
            
            # Go back to the appointments view
            st.session_state.view = 'appointments'
            
            # Rerun the app to update the UI
            st.rerun()

# Main application
def main():
    """Main application function."""
    # Load custom CSS
    load_css()
    
    # Display header
    display_header()
    
    # Display success message if needed
    if st.session_state.show_success:
        st.markdown(f"""
        <div class="success-message">
            {st.session_state.success_message}
        </div>
        """, unsafe_allow_html=True)
        
        # Reset the success message after displaying it
        st.session_state.show_success = False
        st.session_state.success_message = ""
    
    # Create tabs for booking and viewing appointments
    tab1, tab2 = st.tabs(["📅 Book Appointment", "📋 View Appointments"])
    
    with tab1:
        # Display calendar view
        display_calendar_view()
        
        # Display booking form if a date is selected
        display_booking_form()
    
    with tab2:
        # Check if we're in edit mode
        if st.session_state.view == 'edit':
            display_edit_form()
        else:
            # Display all appointments with pagination
            display_appointments_paginated()

if __name__ == "__main__":
    main()
