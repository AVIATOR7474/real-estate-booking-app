import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from datetime import datetime, timedelta
import os
import json
from utils import format_date, get_day_name, get_available_dates as utils_get_available_dates, generate_booking_id

# إعداد الاتصال بـ Google Sheets API
def connect_to_sheets():
    """
    الاتصال بـ Google Sheets API باستخدام ملف الاعتماد
    """
    try:
        # تحديد نطاق الوصول
        scope = ['https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive']
        
        # مسار ملف الاعتماد
        creds_path = 'credentials/google_sheets_creds.json'
        
        # إذا لم يكن ملف الاعتماد موجوداً، استخدم اعتماد مؤقت للتطوير
        if not os.path.exists(creds_path):
            return create_temp_credentials()
        
        # إنشاء اعتماد من ملف JSON
        creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
        
        # الاتصال بـ Google Sheets
        client = gspread.authorize(creds)
        
        return client
    
    except Exception as e:
        raise Exception(f"خطأ في الاتصال بـ Google Sheets API: {str(e)}")

# إنشاء اعتماد مؤقت للتطوير
def create_temp_credentials():
    """
    إنشاء اعتماد مؤقت للتطوير المحلي
    """
    try:
        # إنشاء بيانات وهمية للتطوير
        bookings = pd.DataFrame({
            'booking_id': ['BK20250401001', 'BK20250401002', 'BK20250401003'],
            'company_name': ['شركة الأفق للتطوير العقاري', 'شركة الرياض للاستثمار', 'شركة المستقبل العقارية'],
            'area_name': ['الرياض', 'جدة', 'الدمام'],
            'project_name': ['برج الأفق', 'واحة الرياض', 'مجمع المستقبل'],
            'company_representative': ['أحمد محمد', 'خالد عبدالله', 'سارة علي'],
            'contact_info': ['ahmed@example.com', 'khalid@example.com', 'sara@example.com'],
            'booking_date': ['2025-04-20', '2025-04-27', '2025-05-03'],
            'booking_time': ['12:00 - 12:30', '12:00 - 12:30', '12:00 - 12:30'],
            'status': ['مؤكد', 'مؤكد', 'ملغي'],
            'notes': ['', '', 'تم الإلغاء بناءً على طلب العميل']
        })
        
        # إنشاء تواريخ متاحة
        available_dates = utils_get_available_dates(8)
        available_slots = pd.DataFrame({
            'date': available_dates,  # تأكد من استخدام 'date' كاسم للعمود
            'time': ['12:00 - 12:30'] * len(available_dates),
            'is_available': [True] * len(available_dates)
        })
        
        # تحديث حالة المواعيد المحجوزة
        for date in bookings['booking_date']:
            if date in available_slots['date'].values:
                available_slots.loc[available_slots['date'] == date, 'is_available'] = False
        
        # إنشاء قاموس يحتوي على البيانات
        temp_data = {
            'bookings': bookings,
            'available_slots': available_slots
        }
        
        return temp_data
    
    except Exception as e:
        raise Exception(f"خطأ في إنشاء بيانات مؤقتة: {str(e)}")

# الحصول على جميع الحجوزات
def get_all_bookings():
    """
    الحصول على جميع الحجوزات من Google Sheets
    """
    try:
        client = connect_to_sheets()
        
        # إذا كان الاتصال مؤقتاً، استخدم البيانات المؤقتة
        if isinstance(client, dict):
            return client['bookings']
        
        # فتح جدول البيانات
        sheet = client.open('Real Estate Presentation Bookings')
        
        # الوصول إلى ورقة الحجوزات
        bookings_sheet = sheet.worksheet('Bookings')
        
        # الحصول على جميع البيانات
        data = bookings_sheet.get_all_records()
        
        # تحويل البيانات إلى DataFrame
        bookings_df = pd.DataFrame(data)
        
        return bookings_df
    
    except Exception as e:
        raise Exception(f"خطأ في الحصول على الحجوزات: {str(e)}")

# الحصول على حجز محدد
def get_booking_by_id(booking_id):
    """
    الحصول على حجز محدد بواسطة المعرف
    """
    try:
        # الحصول على جميع الحجوزات
        bookings = get_all_bookings()
        
        # البحث عن الحجز المطلوب
        booking = bookings[bookings['booking_id'] == booking_id]
        
        if booking.empty:
            return None
        
        return booking.iloc[0].to_dict()
    
    except Exception as e:
        raise Exception(f"خطأ في الحصول على الحجز: {str(e)}")

# الحصول على المواعيد المتاحة
def get_available_slots():
    """
    الحصول على المواعيد المتاحة من Google Sheets
    """
    try:
        client = connect_to_sheets()
        
        # إذا كان الاتصال مؤقتاً، استخدم البيانات المؤقتة
        if isinstance(client, dict):
            return client['available_slots']
        
        # فتح جدول البيانات
        sheet = client.open('Real Estate Presentation Bookings')
        
        # الوصول إلى ورقة المواعيد المتاحة
        slots_sheet = sheet.worksheet('Available_Slots')
        
        # الحصول على جميع البيانات
        data = slots_sheet.get_all_records()
        
        # تحويل البيانات إلى DataFrame
        slots_df = pd.DataFrame(data)
        
        return slots_df
    
    except Exception as e:
        raise Exception(f"خطأ في الحصول على المواعيد المتاحة: {str(e)}")

# الحصول على التواريخ المتاحة للحجز
def get_available_dates():
    """
    الحصول على التواريخ المتاحة للحجز
    """
    try:
        # الحصول على المواعيد المتاحة
        slots = get_available_slots()
        
        # تصفية المواعيد المتاحة فقط
        if 'is_available' in slots.columns:
            available_slots = slots[slots['is_available'] == True]
            
            # الحصول على التواريخ المتاحة
            date_column = 'date' if 'date' in available_slots.columns else 'booking_date'
            available_dates = available_slots[date_column].tolist()
            
            return available_dates
        else:
            # إذا لم يكن هناك عمود is_available، استخدم وظيفة get_available_dates من utils
            return utils_get_available_dates()
    
    except Exception as e:
        raise Exception(f"خطأ في الحصول على التواريخ المتاحة: {str(e)}")

# الحصول على التواريخ المحجوزة
def get_booked_dates():
    """
    الحصول على التواريخ المحجوزة
    """
    try:
        # الحصول على المواعيد المتاحة
        slots = get_available_slots()
        
        # تصفية المواعيد المحجوزة فقط
        if 'is_available' in slots.columns:
            booked_slots = slots[slots['is_available'] == False]
            
            # الحصول على التواريخ المحجوزة
            date_column = 'date' if 'date' in booked_slots.columns else 'booking_date'
            booked_dates = booked_slots[date_column].tolist()
            
            return booked_dates
        else:
            # إذا لم يكن هناك عمود is_available، استخدم قائمة فارغة
            return []
    
    except Exception as e:
        raise Exception(f"خطأ في الحصول على التواريخ المحجوزة: {str(e)}")

# الحصول على الحجوزات القادمة
def get_upcoming_bookings(limit=5):
    """
    الحصول على الحجوزات القادمة
    """
    try:
        # الحصول على جميع الحجوزات
        bookings = get_all_bookings()
        
        # تصفية الحجوزات المؤكدة فقط
        confirmed_bookings = bookings[bookings['status'] == 'مؤكد']
        
        # تحويل التاريخ إلى نوع datetime
        confirmed_bookings['booking_date_obj'] = pd.to_datetime(confirmed_bookings['booking_date'])
        
        # تصفية الحجوزات المستقبلية فقط
        today = datetime.now().date()
        upcoming_bookings = confirmed_bookings[confirmed_bookings['booking_date_obj'].dt.date >= today]
        
        # ترتيب الحجوزات حسب التاريخ
        upcoming_bookings = upcoming_bookings.sort_values('booking_date_obj')
        
        # تحديد عدد الحجوزات المطلوبة
        upcoming_bookings = upcoming_bookings.head(limit)
        
        # تحويل DataFrame إلى قائمة من القواميس
        upcoming_bookings_list = upcoming_bookings.to_dict('records')
        
        return upcoming_bookings_list
    
    except Exception as e:
        raise Exception(f"خطأ في الحصول على الحجوزات القادمة: {str(e)}")

# إنشاء حجز جديد
def create_booking(booking_data):
    """
    إنشاء حجز جديد
    """
    try:
        client = connect_to_sheets()
        
        # إذا كان الاتصال مؤقتاً، استخدم البيانات المؤقتة
        if isinstance(client, dict):
            # إنشاء معرف فريد للحجز
            booking_id = generate_booking_id()
            
            # إضافة المعرف إلى بيانات الحجز
            booking_data['booking_id'] = booking_id
            
            # إضافة الحجز إلى قائمة الحجوزات
            client['bookings'] = pd.concat([client['bookings'], pd.DataFrame([booking_data])], ignore_index=True)
            
            # تحديث حالة الموعد
            update_slot_availability(booking_data['booking_date'], False)
            
            return booking_id
        
        # فتح جدول البيانات
        sheet = client.open('Real Estate Presentation Bookings')
        
        # الوصول إلى ورقة الحجوزات
        bookings_sheet = sheet.worksheet('Bookings')
        
        # إنشاء معرف فريد للحجز
        booking_id = generate_booking_id()
        
        # إضافة المعرف إلى بيانات الحجز
        booking_data['booking_id'] = booking_id
        
        # إضافة الحجز إلى الجدول
        bookings_sheet.append_row([
            booking_id,
            booking_data['company_name'],
            booking_data['area_name'],
            booking_data['project_name'],
            booking_data['company_representative'],
            booking_data['contact_info'],
            booking_data['booking_date'],
            booking_data['booking_time'],
            'مؤكد',  # حالة الحجز
            ''  # ملاحظات
        ])
        
        # تحديث حالة الموعد
        update_slot_availability(booking_data['booking_date'], False)
        
        return booking_id
    
    except Exception as e:
        raise Exception(f"خطأ في إنشاء الحجز: {str(e)}")

# تحديث حجز موجود
def update_booking(booking_id, updated_data):
    """
    تحديث حجز موجود
    """
    try:
        client = connect_to_sheets()
        
        # إذا كان الاتصال مؤقتاً، استخدم البيانات المؤقتة
        if isinstance(client, dict):
            # الحصول على الحجز الحالي
            bookings = client['bookings']
            booking_index = bookings[bookings['booking_id'] == booking_id].index
            
            if booking_index.empty:
                return False
            
            # تحديث بيانات الحجز
            for key, value in updated_data.items():
                bookings.loc[booking_index, key] = value
            
            # إذا تم تغيير التاريخ، تحديث حالة المواعيد
            if 'booking_date' in updated_data:
                # الحصول على التاريخ القديم
                old_booking = get_booking_by_id(booking_id)
                old_date = old_booking['booking_date']
                
                # تحديث حالة المواعيد
                update_slot_availability(old_date, True)  # جعل الموعد القديم متاحاً
                update_slot_availability(updated_data['booking_date'], False)  # جعل الموعد الجديد محجوزاً
            
            return True
        
        # فتح جدول البيانات
        sheet = client.open('Real Estate Presentation Bookings')
        
        # الوصول إلى ورقة الحجوزات
        bookings_sheet = sheet.worksheet('Bookings')
        
        # البحث عن الحجز
        cell = bookings_sheet.find(booking_id)
        
        if not cell:
            return False
        
        # الحصول على الحجز الحالي
        old_booking = get_booking_by_id(booking_id)
        
        # تحديث بيانات الحجز
        row = cell.row
        
        for key, value in updated_data.items():
            if key == 'company_name':
                bookings_sheet.update_cell(row, 2, value)
            elif key == 'area_name':
                bookings_sheet.update_cell(row, 3, value)
            elif key == 'project_name':
                bookings_sheet.update_cell(row, 4, value)
            elif key == 'company_representative':
                bookings_sheet.update_cell(row, 5, value)
            elif key == 'contact_info':
                bookings_sheet.update_cell(row, 6, value)
            elif key == 'booking_date':
                bookings_sheet.update_cell(row, 7, value)
                
                # تحديث حالة المواعيد
                update_slot_availability(old_booking['booking_date'], True)  # جعل الموعد القديم متاحاً
                update_slot_availability(value, False)  # جعل الموعد الجديد محجوزاً
            elif key == 'booking_time':
                bookings_sheet.update_cell(row, 8, value)
            elif key == 'status':
                bookings_sheet.update_cell(row, 9, value)
            elif key == 'notes':
                bookings_sheet.update_cell(row, 10, value)
        
        return True
    
    except Exception as e:
        raise Exception(f"خطأ في تحديث الحجز: {str(e)}")

# إلغاء حجز
def cancel_booking(booking_id, reason=''):
    """
    إلغاء حجز
    """
    try:
        # الحصول على الحجز
        booking = get_booking_by_id(booking_id)
        
        if not booking:
            return False
        
        # تحديث حالة الحجز
        updated_data = {
            'status': 'ملغي',
            'notes': reason
        }
        
        # تحديث الحجز
        update_result = update_booking(booking_id, updated_data)
        
        if update_result:
            # جعل الموعد متاحاً مرة أخرى
            update_slot_availability(booking['booking_date'], True)
        
        return update_result
    
    except Exception as e:
        raise Exception(f"خطأ في إلغاء الحجز: {str(e)}")

# تحديث حالة الموعد
def update_slot_availability(date, is_available):
    """
    تحديث حالة الموعد (متاح/محجوز)
    """
    try:
        client = connect_to_sheets()
        
        # إذا كان الاتصال مؤقتاً، استخدم البيانات المؤقتة
        if isinstance(client, dict):
            # تحديث حالة الموعد
            slots = client['available_slots']
            date_column = 'date' if 'date' in slots.columns else 'booking_date'
            slot_index = slots[slots[date_column] == date].index
            
            if not slot_index.empty:
                slots.loc[slot_index, 'is_available'] = is_available
            
            return True
        
        # فتح جدول البيانات
        sheet = client.open('Real Estate Presentation Bookings')
        
        # الوصول إلى ورقة المواعيد المتاحة
        slots_sheet = sheet.worksheet('Available_Slots')
        
        # البحث عن الموعد
        cell = slots_sheet.find(date)
        
        if not cell:
            return False
        
        # تحديث حالة الموعد
        row = cell.row
        slots_sheet.update_cell(row, 3, 'TRUE' if is_available else 'FALSE')
        
        return True
    
    except Exception as e:
        raise Exception(f"خطأ في تحديث حالة الموعد: {str(e)}")

# الحصول على بيانات التقويم
def get_calendar_data(year, month):
    """
    الحصول على بيانات التقويم لشهر محدد
    """
    try:
        # الحصول على التواريخ المتاحة والمحجوزة
        available_dates = get_available_dates()
        booked_dates = get_booked_dates()
        
        # إنشاء قائمة بجميع أيام الشهر
        import calendar
        cal = calendar.monthcalendar(year, month)
        
        # تحويل التقويم إلى قائمة من القواميس
        calendar_data = []
        
        for week in cal:
            week_data = []
            for day in week:
                if day == 0:
                    # يوم فارغ
                    week_data.append({
                        'day': 0,
                        'date': '',
                        'is_available': False,
                        'is_booked': False,
                        'is_past': False
                    })
                else:
                    # تنسيق التاريخ
                    date_str = f"{year}-{month:02d}-{day:02d}"
                    date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
                    
                    # التحقق من حالة اليوم
                    is_available = date_str in available_dates
                    is_booked = date_str in booked_dates
                    is_past = date_obj < datetime.now().date()
                    
                    week_data.append({
                        'day': day,
                        'date': date_str,
                        'is_available': is_available,
                        'is_booked': is_booked,
                        'is_past': is_past
                    })
            
            calendar_data.append(week_data)
        
        return calendar_data
    
    except Exception as e:
        raise Exception(f"خطأ في الحصول على بيانات التقويم: {str(e)}")

# التحقق من توفر تاريخ للحجز
def check_date_availability(date):
    """
    التحقق من توفر تاريخ للحجز
    """
    try:
        # الحصول على التواريخ المتاحة والمحجوزة
        available_dates = get_available_dates()
        booked_dates = get_booked_dates()
        
        # التحقق من توفر التاريخ
        if date in booked_dates:
            return False, "هذا التاريخ محجوز مسبقاً"
        
        if date not in available_dates:
            return False, "هذا التاريخ غير متاح للحجز"
        
        # التحقق من أن التاريخ ليس في الماضي
        date_obj = datetime.strptime(date, "%Y-%m-%d").date()
        if date_obj < datetime.now().date():
            return False, "لا يمكن الحجز في تاريخ سابق"
        
        return True, "التاريخ متاح للحجز"
    
    except Exception as e:
        raise Exception(f"خطأ في التحقق من توفر التاريخ: {str(e)}")

# الحصول على إحصائيات الحجوزات
def get_booking_statistics():
    """
    الحصول على إحصائيات الحجوزات
    """
    try:
        # الحصول على جميع الحجوزات
        bookings = get_all_bookings()
        
        # إجمالي الحجوزات
        total_bookings = len(bookings)
        
        # الحجوزات حسب الحالة
        confirmed_bookings = len(bookings[bookings['status'] == 'مؤكد'])
        cancelled_bookings = len(bookings[bookings['status'] == 'ملغي'])
        rescheduled_bookings = len(bookings[bookings['status'] == 'مرحل'])
        
        # الحجوزات حسب اليوم
        bookings['booking_date_obj'] = pd.to_datetime(bookings['booking_date'])
        bookings['day_of_week'] = bookings['booking_date_obj'].dt.day_name()
        
        # ترجمة أسماء الأيام إلى العربية
        day_map = {
            'Monday': 'الإثنين',
            'Tuesday': 'الثلاثاء',
            'Wednesday': 'الأربعاء',
            'Thursday': 'الخميس',
            'Friday': 'الجمعة',
            'Saturday': 'السبت',
            'Sunday': 'الأحد'
        }
        
        bookings['day_of_week_ar'] = bookings['day_of_week'].map(day_map)
        
        # الحجوزات حسب اليوم
        bookings_by_day = bookings['day_of_week_ar'].value_counts().to_dict()
        
        # الحجوزات حسب الشهر
        bookings['month'] = bookings['booking_date_obj'].dt.month
        bookings['month_name'] = bookings['booking_date_obj'].dt.month_name()
        
        # ترجمة أسماء الشهور إلى العربية
        month_map = {
            'January': 'يناير',
            'February': 'فبراير',
            'March': 'مارس',
            'April': 'أبريل',
            'May': 'مايو',
            'June': 'يونيو',
            'July': 'يوليو',
            'August': 'أغسطس',
            'September': 'سبتمبر',
            'October': 'أكتوبر',
            'November': 'نوفمبر',
            'December': 'ديسمبر'
        }
        
        bookings['month_name_ar'] = bookings['month_name'].map(month_map)
        
        # الحجوزات حسب الشهر
        bookings_by_month = bookings['month_name_ar'].value_counts().to_dict()
        
        # الحجوزات حسب الشركة
        bookings_by_company = bookings['company_name'].value_counts().to_dict()
        
        # إنشاء قاموس الإحصائيات
        statistics = {
            'total_bookings': total_bookings,
            'confirmed_bookings': confirmed_bookings,
            'cancelled_bookings': cancelled_bookings,
            'rescheduled_bookings': rescheduled_bookings,
            'bookings_by_day': bookings_by_day,
            'bookings_by_month': bookings_by_month,
            'bookings_by_company': bookings_by_company
        }
        
        return statistics
    
    except Exception as e:
        raise Exception(f"خطأ في الحصول على إحصائيات الحجوزات: {str(e)}")

# الحصول على بيانات الشركات
def get_companies():
    """
    الحصول على بيانات الشركات
    """
    try:
        client = connect_to_sheets()
        
        # إذا كان الاتصال مؤقتاً، استخدم البيانات المؤقتة
        if isinstance(client, dict):
            # استخراج الشركات الفريدة من الحجوزات
            bookings = client['bookings']
            companies = bookings[['company_name', 'area_name']].drop_duplicates().to_dict('records')
            return companies
        
        # فتح جدول البيانات
        sheet = client.open('Real Estate Presentation Bookings')
        
        # الوصول إلى ورقة الشركات
        companies_sheet = sheet.worksheet('Companies')
        
        # الحصول على جميع البيانات
        data = companies_sheet.get_all_records()
        
        # تحويل البيانات إلى DataFrame
        companies_df = pd.DataFrame(data)
        
        return companies_df.to_dict('records')
    
    except Exception as e:
        raise Exception(f"خطأ في الحصول على بيانات الشركات: {str(e)}")

# الحصول على بيانات المشاريع
def get_projects():
    """
    الحصول على بيانات المشاريع
    """
    try:
        client = connect_to_sheets()
        
        # إذا كان الاتصال مؤقتاً، استخدم البيانات المؤقتة
        if isinstance(client, dict):
            # استخراج المشاريع الفريدة من الحجوزات
            bookings = client['bookings']
            projects = bookings[['project_name', 'company_name']].drop_duplicates().to_dict('records')
            return projects
        
        # فتح جدول البيانات
        sheet = client.open('Real Estate Presentation Bookings')
        
        # الوصول إلى ورقة المشاريع
        projects_sheet = sheet.worksheet('Projects')
        
        # الحصول على جميع البيانات
        data = projects_sheet.get_all_records()
        
        # تحويل البيانات إلى DataFrame
        projects_df = pd.DataFrame(data)
        
        return projects_df.to_dict('records')
    
    except Exception as e:
        raise Exception(f"خطأ في الحصول على بيانات المشاريع: {str(e)}")

# الحصول على إعدادات التطبيق
def get_settings():
    """
    الحصول على إعدادات التطبيق
    """
    try:
        client = connect_to_sheets()
        
        # إذا كان الاتصال مؤقتاً، استخدم إعدادات افتراضية
        if isinstance(client, dict):
            settings = {
                'company_name': 'شركة التطوير العقاري الرائدة',
                'app_title': 'نظام حجز مواعيد العروض التقديمية',
                'booking_time': '12:00 - 12:30',
                'weeks_ahead': 8
            }
            return settings
        
        # فتح جدول البيانات
        sheet = client.open('Real Estate Presentation Bookings')
        
        # الوصول إلى ورقة الإعدادات
        settings_sheet = sheet.worksheet('Settings')
        
        # الحصول على جميع البيانات
        data = settings_sheet.get_all_records()
        
        # تحويل البيانات إلى قاموس
        settings = {}
        for row in data:
            settings[row['key']] = row['value']
        
        return settings
    
    except Exception as e:
        raise Exception(f"خطأ في الحصول على إعدادات التطبيق: {str(e)}")

# تحديث إعدادات التطبيق
def update_settings(updated_settings):
    """
    تحديث إعدادات التطبيق
    """
    try:
        client = connect_to_sheets()
        
        # إذا كان الاتصال مؤقتاً، تجاهل التحديث
        if isinstance(client, dict):
            return True
        
        # فتح جدول البيانات
        sheet = client.open('Real Estate Presentation Bookings')
        
        # الوصول إلى ورقة الإعدادات
        settings_sheet = sheet.worksheet('Settings')
        
        # تحديث الإعدادات
        for key, value in updated_settings.items():
            # البحث عن الإعداد
            cell = settings_sheet.find(key)
            
            if cell:
                # تحديث قيمة الإعداد
                row = cell.row
                settings_sheet.update_cell(row, 2, value)
        
        return True
    
    except Exception as e:
        raise Exception(f"خطأ في تحديث إعدادات التطبيق: {str(e)}")

# إعادة توليد المواعيد المتاحة
def regenerate_available_slots(weeks_ahead=8):
    """
    إعادة توليد المواعيد المتاحة للأسابيع القادمة
    """
    try:
        client = connect_to_sheets()
        
        # إذا كان الاتصال مؤقتاً، تجاهل العملية
        if isinstance(client, dict):
            return True
        
        # فتح جدول البيانات
        sheet = client.open('Real Estate Presentation Bookings')
        
        # الوصول إلى ورقة المواعيد المتاحة
        slots_sheet = sheet.worksheet('Available_Slots')
        
        # حذف جميع البيانات الحالية (باستثناء الصف الأول)
        rows = slots_sheet.row_count
        if rows > 1:
            slots_sheet.delete_rows(2, rows - 1)
        
        # إنشاء المواعيد المتاحة للأسابيع القادمة
        available_dates = utils_get_available_dates(weeks_ahead)
        
        # إضافة المواعيد إلى الجدول
        for date in available_dates:
            slots_sheet.append_row([
                date,
                '12:00 - 12:30',
                'TRUE'
            ])
        
        return True
    
    except Exception as e:
        raise Exception(f"خطأ في إعادة توليد المواعيد المتاحة: {str(e)}")
