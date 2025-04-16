"""
صفحة إدارة الحجوزات
"""

import streamlit as st
import pandas as pd
from datetime import datetime

import config
from utils import create_success_message, create_error_message, format_date
import sheets_api

def render_manage_page():
    """
    عرض صفحة إدارة الحجوزات
    """
    st.title("إدارة الحجوزات")
    
    st.markdown("""
    في هذه الصفحة يمكنك عرض وإدارة الحجوزات الحالية.
    """)
    
    # الحصول على جميع الحجوزات
    bookings = sheets_api.get_bookings()
    
    if not bookings:
        st.info("لا توجد حجوزات حالية.")
        return
    
    # تحويل البيانات إلى DataFrame
    df = pd.DataFrame(bookings)
    
    # إضافة عمود لتنسيق التاريخ
    if "booking_date" in df.columns:
        df["booking_date_formatted"] = df["booking_date"].apply(format_date)
    
    # إضافة عمود لترجمة الحالة
    if "status" in df.columns:
        status_map = {
            "Confirmed": "مؤكد",
            "Cancelled": "ملغي",
            "Rescheduled": "مرحل"
        }
        df["status_ar"] = df["status"].map(status_map)
    
    # تصفية الحجوزات حسب الحالة
    status_filter = st.selectbox(
        "تصفية حسب الحالة",
        options=["الكل", "مؤكد", "ملغي", "مرحل"],
        index=0
    )
    
    if status_filter != "الكل":
        status_en = {v: k for k, v in status_map.items()}.get(status_filter)
        filtered_df = df[df["status"] == status_en]
    else:
        filtered_df = df
    
    # البحث عن حجز
    search_query = st.text_input("البحث عن حجز (اسم الشركة، اسم المشروع، رقم الحجز)")
    
    if search_query:
        # البحث في عدة أعمدة
        search_columns = ["booking_id", "company_name", "project_name", "representative_name"]
        search_mask = pd.Series(False, index=filtered_df.index)
        
        for column in search_columns:
            if column in filtered_df.columns:
                search_mask = search_mask | filtered_df[column].astype(str).str.contains(search_query, case=False)
        
        filtered_df = filtered_df[search_mask]
    
    # عرض الحجوزات
    if not filtered_df.empty:
        st.markdown(f"### الحجوزات ({len(filtered_df)})")
        
        for _, booking in filtered_df.iterrows():
            # تحديد لون حالة الحجز
            status_class = {
                "Confirmed": "booking-status-confirmed",
                "Cancelled": "booking-status-cancelled",
                "Rescheduled": "booking-status-rescheduled"
            }.get(booking["status"], "")
            
            # تنسيق التاريخ
            date_obj = datetime.strptime(booking["booking_date"], "%Y-%m-%d").date()
            day_name = date_obj.strftime("%A")
            day_name_ar = {
                "Saturday": "السبت",
                "Sunday": "الأحد",
                "Monday": "الاثنين",
                "Tuesday": "الثلاثاء",
                "Wednesday": "الأربعاء",
                "Thursday": "الخميس",
                "Friday": "الجمعة"
            }.get(day_name, day_name)
            date_formatted = date_obj.strftime("%d/%m/%Y")
            
            # عرض بطاقة الحجز
            st.markdown(f"""
            <div class="booking-card">
                <div class="booking-header">{booking["company_name"]} - {booking["project_name"]}</div>
                <div class="booking-info">رقم الحجز: {booking["booking_id"]}</div>
                <div class="booking-info">اسم المنطقة: {booking["area_name"]}</div>
                <div class="booking-info">اسم ممثل الشركة: {booking["representative_name"]}</div>
                <div class="booking-info">تاريخ الحجز: {day_name_ar} - {date_formatted}</div>
                <div class="booking-info">وقت الحجز: {booking["booking_time"]}</div>
                <div class="booking-info">حالة الحجز: <span class="{status_class}">{booking.get("status_ar", booking["status"])}</span></div>
            </div>
            """, unsafe_allow_html=True)
            
            # أزرار الإجراءات
            col1, col2 = st.columns(2)
            
            with col1:
                if booking["status"] == "Confirmed":
                    if st.button(f"ترحيل الموعد", key=f"reschedule_{booking['booking_id']}"):
                        # تخزين معرف الحجز في حالة الجلسة
                        st.session_state.selected_booking_id = booking["booking_id"]
                        st.session_state.page = "reschedule"
                        st.rerun()
            
            with col2:
                if booking["status"] == "Confirmed":
                    if st.button(f"إلغاء الحجز", key=f"cancel_{booking['booking_id']}"):
                        # تخزين معرف الحجز في حالة الجلسة
                        st.session_state.selected_booking_id = booking["booking_id"]
                        st.session_state.page = "cancel"
                        st.rerun()
            
            st.markdown("---")
    else:
        st.info("لا توجد حجوزات تطابق معايير البحث.")
    
    # زر العودة إلى الصفحة الرئيسية
    if st.button("العودة إلى الصفحة الرئيسية"):
        st.session_state.page = "home"
        st.rerun()
