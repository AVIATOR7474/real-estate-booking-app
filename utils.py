import pandas as pd
from datetime import datetime, timedelta
import calendar

# تنسيق التاريخ بالصيغة العربية
def format_date(date_str):
    """
    تحويل التاريخ من صيغة YYYY-MM-DD إلى صيغة DD/MM/YYYY
    """
    if not date_str:
        return ""
    
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        return date_obj.strftime("%d/%m/%Y")
    except:
        return date_str

# الحصول على اسم اليوم بالعربية
def get_day_name(date_str):
    """
    الحصول على اسم اليوم بالعربية من تاريخ بصيغة YYYY-MM-DD
    """
    if not date_str:
        return ""
    
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        day_name = date_obj.strftime("%A")
        
        # ترجمة اسم اليوم إلى العربية
        day_map = {
            "Monday": "الإثنين",
            "Tuesday": "الثلاثاء",
            "Wednesday": "الأربعاء",
            "Thursday": "الخميس",
            "Friday": "الجمعة",
            "Saturday": "السبت",
            "Sunday": "الأحد"
        }
        
        return day_map.get(day_name, day_name)
    except:
        return ""

# الحصول على التواريخ المتاحة للحجز
def get_available_dates(weeks_ahead=8):
    """
    إنشاء قائمة بالتواريخ المتاحة للحجز (أيام السبت والثلاثاء) للأسابيع القادمة
    """
    available_dates = []
    
    # تاريخ اليوم
    today = datetime.now().date()
    
    # إنشاء تواريخ للأسابيع القادمة
    for i in range(weeks_ahead * 7):
        date = today + timedelta(days=i)
        
        # التحقق من أن اليوم هو السبت (5) أو الثلاثاء (1)
        if date.weekday() == 5 or date.weekday() == 1:
            available_dates.append(date.strftime("%Y-%m-%d"))
    
    return available_dates

# التحقق من توفر تاريخ للحجز
def is_date_available(date_str, available_dates, booked_dates):
    """
    التحقق مما إذا كان التاريخ متاحاً للحجز
    """
    # التحقق من أن التاريخ ضمن التواريخ المتاحة
    if date_str not in available_dates:
        return False
    
    # التحقق من أن التاريخ غير محجوز مسبقاً
    if date_str in booked_dates:
        return False
    
    # التحقق من أن التاريخ ليس في الماضي
    today = datetime.now().date()
    date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
    
    if date_obj < today:
        return False
    
    return True

# إنشاء معرف فريد للحجز
def generate_booking_id():
    """
    إنشاء معرف فريد للحجز بناءً على الوقت الحالي
    """
    now = datetime.now()
    booking_id = now.strftime("BK%Y%m%d%H%M%S")
    return booking_id

# تحويل التاريخ إلى تنسيق قابل للفرز
def get_sortable_date(date_str):
    """
    تحويل التاريخ من صيغة DD/MM/YYYY إلى صيغة YYYY-MM-DD للفرز
    """
    if not date_str:
        return ""
    
    try:
        date_parts = date_str.split("/")
        if len(date_parts) == 3:
            day, month, year = date_parts
            return f"{year}-{month}-{day}"
        else:
            return date_str
    except:
        return date_str
