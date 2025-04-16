import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import calendar
import os
import json
from PIL import Image
import matplotlib.pyplot as plt
import io

# Import custom modules
import config
import sheets_api
from utils import format_date, get_day_name, get_available_dates

# Set page configuration
st.set_page_config(
    page_title="نظام حجز مواعيد العروض التقديمية",
    page_icon="assets/favicon.ico",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load CSS
def load_css():
    with open("assets/styles.css") as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Initialize session state
def init_session_state():
    if "page" not in st.session_state:
        st.session_state.page = "home"
    if "selected_date" not in st.session_state:
        st.session_state.selected_date = None
    if "booking_success" not in st.session_state:
        st.session_state.booking_success = False
    if "booking_id" not in st.session_state:
        st.session_state.booking_id = None
    if "current_month" not in st.session_state:
        st.session_state.current_month = datetime.now().month
    if "current_year" not in st.session_state:
        st.session_state.current_year = datetime.now().year

# Navigation functions
def navigate_to(page):
    st.session_state.page = page
    st.session_state.booking_success = False
    st.session_state.booking_id = None

# Display sidebar
def display_sidebar():
    with st.sidebar:
        # Display logo
        try:
            logo = Image.open("assets/logo.png")
            st.image(logo, use_container_width=True)
        except:
            st.title("نظام حجز مواعيد العروض التقديمية")
        
        st.markdown("---")
        
        # Navigation buttons
        st.button("الصفحة الرئيسية", on_click=navigate_to, args=["home"], use_container_width=True)
        st.button("حجز موعد جديد", on_click=navigate_to, args=["booking"], use_container_width=True)
        st.button("إدارة الحجوزات", on_click=navigate_to, args=["manage"], use_container_width=True)
        st.button("ترحيل موعد", on_click=navigate_to, args=["reschedule"], use_container_width=True)
        st.button("إلغاء موعد", on_click=navigate_to, args=["cancel"], use_container_width=True)
        
        st.markdown("---")
        
        # Additional pages
        st.button("تحليلات", on_click=navigate_to, args=["analytics"], use_container_width=True)
        st.button("التقارير", on_click=navigate_to, args=["reports"], use_container_width=True)
        st.button("الإعدادات", on_click=navigate_to, args=["settings"], use_container_width=True)
        
        st.markdown("---")
        
        # Help and documentation
        st.button("دليل المستخدم", on_click=navigate_to, args=["help"], use_container_width=True)
        
        st.markdown("---")
        
        # Footer
        st.markdown("© 2025 شركة التطوير العقاري الرائدة")

# Display calendar
def display_calendar(available_dates=None, booked_dates=None):
    if available_dates is None:
        available_dates = []
    if booked_dates is None:
        booked_dates = []
    
    # Get current month and year from session state
    month = st.session_state.current_month
    year = st.session_state.current_year
    
    # Create calendar
    cal = calendar.monthcalendar(year, month)
    
    # Month navigation
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col1:
        if st.button("◀️ الشهر السابق"):
            if st.session_state.current_month > 1:
                st.session_state.current_month -= 1
            else:
                st.session_state.current_month = 12
                st.session_state.current_year -= 1
            st.rerun()
    
    with col2:
        month_name = calendar.month_name[month]
        st.markdown(f"<h3 style='text-align: center;'>{month_name} {year}</h3>", unsafe_allow_html=True)
    
    with col3:
        if st.button("الشهر التالي ▶️"):
            if st.session_state.current_month < 12:
                st.session_state.current_month += 1
            else:
                st.session_state.current_month = 1
                st.session_state.current_year += 1
            st.rerun()
    
    # Display calendar
    st.markdown("<div class='calendar-container'>", unsafe_allow_html=True)
    
    # Day names
    days = ["الأحد", "الإثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة", "السبت"]
    cols = st.columns(7)
    for i, day in enumerate(days):
        with cols[i]:
            st.markdown(f"<div style='text-align: center; font-weight: bold;'>{day}</div>", unsafe_allow_html=True)
    
    # Calendar days
    for week in cal:
        cols = st.columns(7)
        for i, day in enumerate(week):
            with cols[i]:
                if day == 0:
                    # Empty cell
                    st.markdown("<div class='calendar-day'></div>", unsafe_allow_html=True)
                else:
                    date_str = f"{year}-{month:02d}-{day:02d}"
                    date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
                    
                    # Check if date is available (Saturday or Tuesday)
                    is_available = date_str in available_dates
                    is_booked = date_str in booked_dates
                    is_past = date_obj < datetime.now().date()
                    
                    # Determine day class
                    if is_past:
                        day_class = "calendar-day-disabled"
                    elif is_booked:
                        day_class = "calendar-day-booked"
                    elif is_available:
                        day_class = "calendar-day-available"
                    else:
                        day_class = "calendar-day-unavailable"
                    
                    # Display day with appropriate class
                    if is_available and not is_booked and not is_past:
                        # Clickable day
                        if st.button(f"{day}", key=f"day_{date_str}", use_container_width=True):
                            st.session_state.selected_date = date_str
                            st.rerun()
                    else:
                        # Non-clickable day
                        st.markdown(f"<div class='calendar-day {day_class}'>{day}</div>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Legend
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("<div style='display: flex; align-items: center;'><div style='width: 20px; height: 20px; background-color: #ccffcc; border-radius: 50%; margin-right: 10px;'></div> متاح</div>", unsafe_allow_html=True)
    with col2:
        st.markdown("<div style='display: flex; align-items: center;'><div style='width: 20px; height: 20px; background-color: #ffcccc; border-radius: 50%; margin-right: 10px;'></div> محجوز</div>", unsafe_allow_html=True)
    with col3:
        st.markdown("<div style='display: flex; align-items: center;'><div style='width: 20px; height: 20px; background-color: #f0f0f0; border-radius: 50%; margin-right: 10px;'></div> غير متاح</div>", unsafe_allow_html=True)
    
    return st.session_state.selected_date

# Render home page
def render_home_page():
    st.title("نظام حجز مواعيد العروض التقديمية للتطوير العقاري")
    
    st.markdown("""
    مرحباً بك في نظام حجز مواعيد العروض التقديمية لشركات التطوير العقاري.
    
    يمكنك استخدام هذا النظام لحجز مواعيد للعروض التقديمية أيام السبت والثلاثاء فقط، من الساعة 12:00 ظهراً وحتى 12:30 ظهراً.
    """)
    
    # Get available and booked dates
    try:
        available_dates = sheets_api.get_available_dates()
        booked_dates = sheets_api.get_booked_dates()
        
        st.markdown("### التقويم")
        st.markdown("اختر تاريخاً من التقويم أدناه لعرض المواعيد المتاحة:")
        
        display_calendar(available_dates, booked_dates)
        
        # Display upcoming bookings
        st.markdown("### الحجوزات القادمة")
        upcoming_bookings = sheets_api.get_upcoming_bookings(limit=5)
        
        if upcoming_bookings:
            for booking in upcoming_bookings:
                with st.container():
                    st.markdown(f"""
                    <div class='booking-card'>
                        <div class='booking-header'>{booking['company_name']} - {booking['project_name']}</div>
                        <div class='booking-info'>التاريخ: {format_date(booking['booking_date'])} ({get_day_name(booking['booking_date'])})</div>
                        <div class='booking-info'>الوقت: {booking['booking_time']}</div>
                        <div class='booking-info'>ممثل الشركة: {booking['company_representative']}</div>
                        <div class='booking-info'>الحالة: <span class='booking-status-{booking['status'].lower()}'>{booking['status']}</span></div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("لا توجد حجوزات قادمة.")
        
        # Quick actions
        st.markdown("### إجراءات سريعة")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("حجز موعد جديد", use_container_width=True):
                navigate_to("booking")
        
        with col2:
            if st.button("إدارة الحجوزات", use_container_width=True):
                navigate_to("manage")
        
        with col3:
            if st.button("عرض التحليلات", use_container_width=True):
                navigate_to("analytics")
    
    except Exception as e:
        st.error(f"حدث خطأ أثناء إعداد قاعدة البيانات. يرجى التحقق من الاتصال بالإنترنت وإعادة تحميل الصفحة.")
        st.error(f"تفاصيل الخطأ: {str(e)}")
        
        # Create a placeholder for credentials
        st.markdown("### إعداد الاتصال بـ Google Sheets")
        st.markdown("""
        لاستخدام هذا التطبيق، تحتاج إلى إعداد الاتصال بـ Google Sheets API:
        
        1. إنشاء مشروع في [Google Cloud Console](https://console.cloud.google.com/)
        2. تمكين Google Sheets API و Google Drive API
        3. إنشاء حساب خدمة وتنزيل ملف اعتماد JSON
        4. وضع ملف الاعتماد في مجلد `credentials` باسم `google_sheets_creds.json`
        
        لمزيد من التفاصيل، راجع دليل النشر.
        """)
        
        # Create credentials directory if it doesn't exist
        os.makedirs("credentials", exist_ok=True)
        
        # Allow user to upload credentials file
        uploaded_file = st.file_uploader("تحميل ملف اعتماد Google Sheets", type=["json"])
        if uploaded_file is not None:
            # Save the uploaded file
            with open("credentials/google_sheets_creds.json", "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success("تم تحميل ملف الاعتماد بنجاح. يرجى إعادة تحميل الصفحة.")

# Render page based on session state
def render_page():
    # Display sidebar
    display_sidebar()
    
    # Display selected page
    if st.session_state.page == "home":
        render_home_page()
    elif st.session_state.page == "booking":
        from pages.booking import render_booking_page
        render_booking_page()
    elif st.session_state.page == "manage":
        from pages.manage import render_manage_page
        render_manage_page()
    elif st.session_state.page == "reschedule":
        from pages.reschedule import render_reschedule_page
        render_reschedule_page()
    elif st.session_state.page == "cancel":
        from pages.cancel import render_cancel_page
        render_cancel_page()
    elif st.session_state.page == "analytics":
        from pages.analytics import render_analytics_page
        render_analytics_page()
    elif st.session_state.page == "reports":
        from pages.reports import render_reports_page
        render_reports_page()
    elif st.session_state.page == "settings":
        from pages.settings import render_settings_page
        render_settings_page()
    elif st.session_state.page == "help":
        # Load user guide
        try:
            with open("user_guide.md", "r", encoding="utf-8") as f:
                user_guide_content = f.read()
            st.markdown(user_guide_content)
            
            # Add download button
            st.download_button(
                label="تنزيل دليل المستخدم",
                data=user_guide_content,
                file_name="user_guide.md",
                mime="text/markdown"
            )
        except:
            st.error("لم يتم العثور على دليل المستخدم.")
    else:
        # If page is unknown, redirect to home
        st.session_state.page = "home"
        render_home_page()

# Main function
def main():
    try:
        # Load CSS
        load_css()
        
        # Initialize session state
        init_session_state()
        
        # Render page
        render_page()
    
    except Exception as e:
        st.error(f"حدث خطأ غير متوقع: {str(e)}")

if __name__ == "__main__":
    main()
