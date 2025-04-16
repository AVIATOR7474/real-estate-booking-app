"""
صفحة إلغاء الحجز
"""

import streamlit as st
from datetime import datetime

import config
from utils import create_success_message, create_error_message, format_date
import sheets_api

def render_cancel_page():
    """
    عرض صفحة إلغاء الحجز
    """
    st.title("إلغاء الحجز")
    
    # التحقق من وجود معرف الحجز في حالة الجلسة
    if "selected_booking_id" not in st.session_state:
        st.error("لم يتم تحديد حجز لإلغائه.")
        
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
    
    # عرض بيانات الحجز
    st.markdown("### بيانات الحجز")
    
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
        <div class="booking-info">تاريخ الحجز: {day_name_ar} - {date_formatted}</div>
        <div class="booking-info">وقت الحجز: {booking["booking_time"]}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # تأكيد الإلغاء
    st.warning("هل أنت متأكد من رغبتك في إلغاء هذا الحجز؟ لا يمكن التراجع عن هذا الإجراء.")
    
    # سبب الإلغاء
    cancel_reason = st.text_area("سبب الإلغاء (اختياري)")
    
    # أزرار الإجراءات
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("تأكيد الإلغاء", key="confirm_cancel"):
            # تحديث بيانات الحجز
            updated_data = {
                "status": "Cancelled",
                "notes": f"{booking.get('notes', '')} | سبب الإلغاء: {cancel_reason}" if cancel_reason else booking.get('notes', '')
            }
            
            # إلغاء الحجز
            cancel_result = sheets_api.cancel_booking(booking_id)
            
            if cancel_result:
                st.success("تم إلغاء الحجز بنجاح!")
                
                # عرض تفاصيل الحجز بعد الإلغاء
                st.markdown("### تفاصيل الحجز بعد الإلغاء")
                
                st.markdown(f"""
                <div class="booking-card">
                    <div class="booking-header">{booking["company_name"]} - {booking["project_name"]}</div>
                    <div class="booking-info">رقم الحجز: {booking["booking_id"]}</div>
                    <div class="booking-info">اسم المنطقة: {booking["area_name"]}</div>
                    <div class="booking-info">اسم ممثل الشركة: {booking["representative_name"]}</div>
                    <div class="booking-info">تاريخ الحجز: {day_name_ar} - {date_formatted}</div>
                    <div class="booking-info">وقت الحجز: {booking["booking_time"]}</div>
                    <div class="booking-info">حالة الحجز: <span class="booking-status-cancelled">ملغي</span></div>
                </div>
                """, unsafe_allow_html=True)
                
                # إزالة معرف الحجز من حالة الجلسة
                if "selected_booking_id" in st.session_state:
                    del st.session_state.selected_booking_id
                
                # زر العودة إلى صفحة إدارة الحجوزات
                if st.button("العودة إلى إدارة الحجوزات", key="back_to_manage_after_cancel"):
                    st.session_state.page = "manage"
                    st.rerun()
            else:
                st.error("حدث خطأ أثناء إلغاء الحجز. يرجى المحاولة مرة أخرى.")
    
    with col2:
        if st.button("إلغاء", key="cancel_cancel"):
            # إزالة معرف الحجز من حالة الجلسة
            if "selected_booking_id" in st.session_state:
                del st.session_state.selected_booking_id
            
            # العودة إلى صفحة إدارة الحجوزات
            st.session_state.page = "manage"
            st.rerun()
