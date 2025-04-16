"""
صفحة ترحيل موعد الحجز
"""

import streamlit as st
import pandas as pd
from datetime import datetime

import config
from utils import create_success_message, create_error_message, format_date
import sheets_api

def render_reschedule_page():
    """
    عرض صفحة ترحيل موعد الحجز
    """
    st.title("ترحيل موعد الحجز")
    
    # التحقق من وجود معرف الحجز في حالة الجلسة
    if "selected_booking_id" not in st.session_state:
        st.error("لم يتم تحديد حجز لترحيله.")
        
        # زر العودة إلى صفحة إدارة الحجوزات
        if st.button("العودة إلى إدارة الحجوزات"):
            st.session_state.page = "manage"
            st.rerun()
        
        return
    
    booking_id = st.session_state.selected_booking_id
    
    # الحصول على بيانات الحجز
    booking = sheets_api.get_booking_by_id(booking_id)
    
    if not booking:
        st.error("لم يتم العثور على الحجز المحدد.")
        
        # زر العودة إلى صفحة إدارة الحجوزات
        if st.button("العودة إلى إدارة الحجوزات"):
            st.session_state.page = "manage"
            st.rerun()
        
        return
    
    # عرض بيانات الحجز الحالي
    st.markdown("### بيانات الحجز الحالي")
    
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
    
    st.markdown(f"""
    <div class="booking-card">
        <div class="booking-header">{booking["company_name"]} - {booking["project_name"]}</div>
        <div class="booking-info">رقم الحجز: {booking["booking_id"]}</div>
        <div class="booking-info">اسم المنطقة: {booking["area_name"]}</div>
        <div class="booking-info">اسم ممثل الشركة: {booking["representative_name"]}</div>
        <div class="booking-info">تاريخ الحجز الحالي: {day_name_ar} - {date_formatted}</div>
        <div class="booking-info">وقت الحجز: {booking["booking_time"]}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # نموذج ترحيل الموعد
    st.markdown("### اختيار موعد جديد")
    
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
                "اختر تاريخًا جديدًا",
                options=list(date_dict.keys()),
                key="new_booking_date_label"
            )
            new_booking_date = date_dict[selected_date_label]
            
            # عرض وقت الحجز (ثابت)
            st.info(f"وقت الحجز: {config.BOOKING_TIME}")
            new_booking_time = config.BOOKING_TIME
            
            # زر تأكيد الترحيل
            if st.button("تأكيد ترحيل الموعد"):
                # التحقق من أن التاريخ الجديد مختلف عن التاريخ الحالي
                if new_booking_date == booking["booking_date"]:
                    st.error("التاريخ الجديد هو نفس التاريخ الحالي. يرجى اختيار تاريخ آخر.")
                else:
                    # تحديث بيانات الحجز
                    updated_data = {
                        "booking_date": new_booking_date,
                        "booking_time": new_booking_time,
                        "status": "Confirmed"  # إعادة تعيين الحالة إلى مؤكد
                    }
                    
                    # تحديث الحجز
                    update_result = sheets_api.update_booking(booking_id, updated_data)
                    
                    if update_result:
                        st.success("تم ترحيل الموعد بنجاح!")
                        
                        # تنسيق التاريخ الجديد
                        new_date_obj = datetime.strptime(new_booking_date, "%Y-%m-%d").date()
                        new_day_name = new_date_obj.strftime("%A")
                        new_day_name_ar = {
                            "Saturday": "السبت",
                            "Sunday": "الأحد",
                            "Monday": "الاثنين",
                            "Tuesday": "الثلاثاء",
                            "Wednesday": "الأربعاء",
                            "Thursday": "الخميس",
                            "Friday": "الجمعة"
                        }.get(new_day_name, new_day_name)
                        new_date_formatted = new_date_obj.strftime("%d/%m/%Y")
                        
                        # عرض تفاصيل الحجز بعد الترحيل
                        st.markdown("### تفاصيل الحجز بعد الترحيل")
                        
                        st.markdown(f"""
                        <div class="booking-card">
                            <div class="booking-header">{booking["company_name"]} - {booking["project_name"]}</div>
                            <div class="booking-info">رقم الحجز: {booking["booking_id"]}</div>
                            <div class="booking-info">اسم المنطقة: {booking["area_name"]}</div>
                            <div class="booking-info">اسم ممثل الشركة: {booking["representative_name"]}</div>
                            <div class="booking-info">تاريخ الحجز الجديد: {new_day_name_ar} - {new_date_formatted}</div>
                            <div class="booking-info">وقت الحجز: {new_booking_time}</div>
                            <div class="booking-info">حالة الحجز: <span class="booking-status-confirmed">مؤكد</span></div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # إزالة معرف الحجز من حالة الجلسة
                        if "selected_booking_id" in st.session_state:
                            del st.session_state.selected_booking_id
                        
                        # زر العودة إلى صفحة إدارة الحجوزات
                        if st.button("العودة إلى إدارة الحجوزات"):
                            st.session_state.page = "manage"
                            st.rerun()
                    else:
                        st.error("حدث خطأ أثناء ترحيل الموعد. يرجى المحاولة مرة أخرى.")
        else:
            st.error("لا توجد مواعيد متاحة حاليًا. يرجى المحاولة لاحقًا.")
    else:
        st.error("لا توجد مواعيد متاحة حاليًا. يرجى المحاولة لاحقًا.")
    
    # زر إلغاء الترحيل
    if st.button("إلغاء"):
        # إزالة معرف الحجز من حالة الجلسة
        if "selected_booking_id" in st.session_state:
            del st.session_state.selected_booking_id
        
        # العودة إلى صفحة إدارة الحجوزات
        st.session_state.page = "manage"
        st.rerun()
