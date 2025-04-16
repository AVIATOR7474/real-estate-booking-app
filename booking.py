"""
صفحة حجز موعد جديد
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

import config
from utils import (
    validate_booking_form, 
    create_success_message, 
    create_error_message, 
    is_valid_booking_date,
    get_next_available_dates,
    format_date
)
import sheets_api

def render_booking_page():
    """
    عرض صفحة حجز موعد جديد
    """
    st.title("حجز موعد عرض تقديمي جديد")
    
    st.markdown("""
    يرجى ملء النموذج التالي لحجز موعد عرض تقديمي جديد.
    
    **ملاحظة**: المواعيد متاحة فقط أيام السبت والثلاثاء من الساعة 12:00 ظهرًا إلى 12:30 ظهرًا.
    """)
    
    # نموذج الحجز
    with st.form("booking_form"):
        # بيانات الشركة
        st.subheader("بيانات الشركة")
        
        col1, col2 = st.columns(2)
        with col1:
            company_name = st.text_input(config.BOOKING_FORM_LABELS["company_name"], key="company_name")
        
        with col2:
            area_name = st.text_input(config.BOOKING_FORM_LABELS["area_name"], key="area_name")
        
        col1, col2 = st.columns(2)
        with col1:
            project_name = st.text_input(config.BOOKING_FORM_LABELS["project_name"], key="project_name")
        
        with col2:
            representative_name = st.text_input(config.BOOKING_FORM_LABELS["representative_name"], key="representative_name")
        
        # بيانات الاتصال
        st.subheader("بيانات الاتصال")
        
        col1, col2 = st.columns(2)
        with col1:
            contact_email = st.text_input(config.BOOKING_FORM_LABELS["contact_email"], key="contact_email")
        
        with col2:
            contact_phone = st.text_input(config.BOOKING_FORM_LABELS["contact_phone"], key="contact_phone")
        
        # بيانات الحجز
        st.subheader("بيانات الحجز")
        
        # الحصول على المواعيد المتاحة
        available_slots = sheets_api.get_available_slots()
        
        # تحويل البيانات إلى DataFrame
        if available_slots:
            df = pd.DataFrame(available_slots)
            
            # تصفية المواعيد المتاحة فقط
            df = df[df["is_available"] == "Yes"]
            
            # ترتيب المواعيد حسب التاريخ
            df = df.sort_values(by="slot_date")
            
            # إنشاء قائمة بالتواريخ المتاحة
            available_dates = df["slot_date"].unique().tolist()
            
            # تنسيق التواريخ لعرضها في القائمة المنسدلة
            date_options = []
            for date_str in available_dates:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
                day_name = date_obj.strftime("%A")
                
                # ترجمة اسم اليوم إلى العربية
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
                date_options.append((date_str, f"{day_name_ar} - {date_formatted}"))
            
            # إذا كانت هناك تواريخ متاحة
            if date_options:
                # إنشاء قائمة منسدلة بالتواريخ المتاحة
                date_dict = {label: value for value, label in date_options}
                selected_date_label = st.selectbox(
                    config.BOOKING_FORM_LABELS["booking_date"],
                    options=list(date_dict.keys()),
                    key="booking_date_label"
                )
                booking_date = date_dict[selected_date_label]
                
                # عرض وقت الحجز (ثابت)
                st.info(f"{config.BOOKING_FORM_LABELS['booking_time']}: {config.BOOKING_TIME}")
                booking_time = config.BOOKING_TIME
            else:
                st.error("لا توجد مواعيد متاحة حاليًا. يرجى المحاولة لاحقًا.")
                booking_date = None
                booking_time = None
        else:
            st.error("لا توجد مواعيد متاحة حاليًا. يرجى المحاولة لاحقًا.")
            booking_date = None
            booking_time = None
        
        # ملاحظات إضافية
        notes = st.text_area(config.BOOKING_FORM_LABELS["notes"], key="notes")
        
        # زر تأكيد الحجز
        submit_button = st.form_submit_button("تأكيد الحجز")
        
        # معالجة النموذج عند الضغط على زر التأكيد
        if submit_button:
            # التحقق من توفر المواعيد
            if not booking_date or not booking_time:
                st.error("لا توجد مواعيد متاحة للحجز.")
                return
            
            # جمع بيانات النموذج
            form_data = {
                "company_name": company_name,
                "area_name": area_name,
                "project_name": project_name,
                "representative_name": representative_name,
                "contact_email": contact_email,
                "contact_phone": contact_phone,
                "booking_date": booking_date,
                "booking_time": booking_time,
                "notes": notes
            }
            
            # التحقق من صحة البيانات
            required_fields = [
                "company_name", 
                "area_name", 
                "project_name", 
                "representative_name", 
                "contact_email", 
                "contact_phone", 
                "booking_date"
            ]
            
            errors = validate_booking_form(form_data, required_fields)
            
            if errors:
                for error in errors:
                    st.error(error)
            else:
                # إنشاء الحجز
                booking_id = sheets_api.create_booking(form_data)
                
                if booking_id:
                    st.success(f"تم إنشاء الحجز بنجاح! رقم الحجز: {booking_id}")
                    
                    # عرض تفاصيل الحجز
                    st.markdown("### تفاصيل الحجز")
                    
                    # تنسيق التاريخ
                    date_obj = datetime.strptime(booking_date, "%Y-%m-%d").date()
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
                    
                    st.markdown(f"""
                    <div class="booking-card">
                        <div class="booking-header">تفاصيل الحجز</div>
                        <div class="booking-info">رقم الحجز: {booking_id}</div>
                        <div class="booking-info">اسم الشركة: {company_name}</div>
                        <div class="booking-info">اسم المنطقة: {area_name}</div>
                        <div class="booking-info">اسم المشروع: {project_name}</div>
                        <div class="booking-info">اسم ممثل الشركة: {representative_name}</div>
                        <div class="booking-info">تاريخ الحجز: {day_name_ar} - {date_formatted}</div>
                        <div class="booking-info">وقت الحجز: {booking_time}</div>
                        <div class="booking-info">حالة الحجز: <span class="booking-status-confirmed">مؤكد</span></div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # زر العودة إلى الصفحة الرئيسية
                    if st.button("العودة إلى الصفحة الرئيسية"):
                        st.session_state.page = "home"
                        st.rerun()
                else:
                    st.error("حدث خطأ أثناء إنشاء الحجز. يرجى المحاولة مرة أخرى.")
