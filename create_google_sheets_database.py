"""
وحدة إنشاء قاعدة البيانات في Google Sheets
"""

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from datetime import datetime, timedelta
import os
import json

# نطاق الوصول المطلوب لـ Google Sheets API
SCOPES = ['https://www.googleapis.com/auth/spreadsheets',
          'https://www.googleapis.com/auth/drive']

# اسم ملف Google Sheets
SPREADSHEET_NAME = "Real Estate Presentation Bookings"

def create_service_account_file():
    """
    إنشاء ملف حساب الخدمة للاتصال بـ Google Sheets API
    يجب استبدال هذا بملف حساب خدمة حقيقي في بيئة الإنتاج
    """
    # إنشاء مجلد للاعتمادات إذا لم يكن موجودًا
    os.makedirs('credentials', exist_ok=True)
    
    # إنشاء ملف اعتماد مؤقت للتطوير
    # ملاحظة: هذا للتطوير فقط، في بيئة الإنتاج يجب استخدام ملف اعتماد حقيقي
    creds_content = {
        "type": "service_account",
        "project_id": "real-estate-booking-app",
        "private_key_id": "placeholder_key_id",
        "private_key": "-----BEGIN PRIVATE KEY-----\nplaceholder_key\n-----END PRIVATE KEY-----\n",
        "client_email": "placeholder@real-estate-booking-app.iam.gserviceaccount.com",
        "client_id": "placeholder_client_id",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/placeholder.iam.gserviceaccount.com"
    }
    
    with open('credentials/google_sheets_creds.json', 'w') as f:
        json.dump(creds_content, f)
    
    return 'credentials/google_sheets_creds.json'

def connect_to_sheets():
    """
    الاتصال بـ Google Sheets API
    """
    # التحقق من وجود ملف الاعتماد أو إنشائه
    creds_file = 'credentials/google_sheets_creds.json'
    if not os.path.exists(creds_file):
        creds_file = create_service_account_file()
    
    # الاتصال بـ Google Sheets API
    try:
        creds = ServiceAccountCredentials.from_json_keyfile_name(creds_file, SCOPES)
        client = gspread.authorize(creds)
        
        # محاولة فتح جدول البيانات أو إنشائه إذا لم يكن موجودًا
        try:
            spreadsheet = client.open(SPREADSHEET_NAME)
            print(f"تم فتح جدول البيانات الموجود: {SPREADSHEET_NAME}")
        except gspread.exceptions.SpreadsheetNotFound:
            spreadsheet = client.create(SPREADSHEET_NAME)
            # مشاركة الجدول مع الجميع للقراءة
            spreadsheet.share(None, perm_type='anyone', role='reader')
            print(f"تم إنشاء جدول بيانات جديد: {SPREADSHEET_NAME}")
        
        return spreadsheet
    except Exception as e:
        print(f"خطأ في الاتصال بـ Google Sheets: {e}")
        return None

def create_bookings_sheet(spreadsheet):
    """
    إنشاء ورقة الحجوزات
    """
    try:
        # محاولة الوصول إلى ورقة الحجوزات أو إنشائها إذا لم تكن موجودة
        try:
            bookings_sheet = spreadsheet.worksheet("Bookings")
            print("تم العثور على ورقة الحجوزات الموجودة")
        except gspread.exceptions.WorksheetNotFound:
            bookings_sheet = spreadsheet.add_worksheet(title="Bookings", rows=1000, cols=20)
            print("تم إنشاء ورقة الحجوزات الجديدة")
        
        # إضافة رؤوس الأعمدة
        headers = [
            "booking_id", 
            "company_name", 
            "area_name", 
            "project_name", 
            "representative_name", 
            "contact_email", 
            "contact_phone",
            "booking_date", 
            "booking_time", 
            "status", 
            "notes", 
            "created_at",
            "updated_at"
        ]
        
        # التحقق مما إذا كانت الرؤوس موجودة بالفعل
        existing_headers = bookings_sheet.row_values(1)
        if not existing_headers or existing_headers != headers:
            bookings_sheet.clear()  # مسح أي بيانات موجودة
            bookings_sheet.append_row(headers)
            print("تم إضافة رؤوس الأعمدة إلى ورقة الحجوزات")
        
        # تنسيق الورقة
        bookings_sheet.format('A1:M1', {'textFormat': {'bold': True}})
        
        return bookings_sheet
    except Exception as e:
        print(f"خطأ في إنشاء ورقة الحجوزات: {e}")
        return None

def create_available_slots_sheet(spreadsheet):
    """
    إنشاء ورقة المواعيد المتاحة
    """
    try:
        # محاولة الوصول إلى ورقة المواعيد المتاحة أو إنشائها إذا لم تكن موجودة
        try:
            slots_sheet = spreadsheet.worksheet("Available_Slots")
            print("تم العثور على ورقة المواعيد المتاحة الموجودة")
        except gspread.exceptions.WorksheetNotFound:
            slots_sheet = spreadsheet.add_worksheet(title="Available_Slots", rows=1000, cols=10)
            print("تم إنشاء ورقة المواعيد المتاحة الجديدة")
        
        # إضافة رؤوس الأعمدة
        headers = [
            "slot_id", 
            "slot_date", 
            "slot_day", 
            "slot_time", 
            "is_available", 
            "booking_id"
        ]
        
        # التحقق مما إذا كانت الرؤوس موجودة بالفعل
        existing_headers = slots_sheet.row_values(1)
        if not existing_headers or existing_headers != headers:
            slots_sheet.clear()  # مسح أي بيانات موجودة
            slots_sheet.append_row(headers)
            print("تم إضافة رؤوس الأعمدة إلى ورقة المواعيد المتاحة")
        
        # تنسيق الورقة
        slots_sheet.format('A1:F1', {'textFormat': {'bold': True}})
        
        return slots_sheet
    except Exception as e:
        print(f"خطأ في إنشاء ورقة المواعيد المتاحة: {e}")
        return None

def create_companies_sheet(spreadsheet):
    """
    إنشاء ورقة شركات التطوير العقاري
    """
    try:
        # محاولة الوصول إلى ورقة الشركات أو إنشائها إذا لم تكن موجودة
        try:
            companies_sheet = spreadsheet.worksheet("Companies")
            print("تم العثور على ورقة الشركات الموجودة")
        except gspread.exceptions.WorksheetNotFound:
            companies_sheet = spreadsheet.add_worksheet(title="Companies", rows=1000, cols=10)
            print("تم إنشاء ورقة الشركات الجديدة")
        
        # إضافة رؤوس الأعمدة
        headers = [
            "company_id", 
            "company_name", 
            "contact_person", 
            "contact_email", 
            "contact_phone", 
            "address", 
            "notes"
        ]
        
        # التحقق مما إذا كانت الرؤوس موجودة بالفعل
        existing_headers = companies_sheet.row_values(1)
        if not existing_headers or existing_headers != headers:
            companies_sheet.clear()  # مسح أي بيانات موجودة
            companies_sheet.append_row(headers)
            print("تم إضافة رؤوس الأعمدة إلى ورقة الشركات")
        
        # تنسيق الورقة
        companies_sheet.format('A1:G1', {'textFormat': {'bold': True}})
        
        return companies_sheet
    except Exception as e:
        print(f"خطأ في إنشاء ورقة الشركات: {e}")
        return None

def create_projects_sheet(spreadsheet):
    """
    إنشاء ورقة المشاريع
    """
    try:
        # محاولة الوصول إلى ورقة المشاريع أو إنشائها إذا لم تكن موجودة
        try:
            projects_sheet = spreadsheet.worksheet("Projects")
            print("تم العثور على ورقة المشاريع الموجودة")
        except gspread.exceptions.WorksheetNotFound:
            projects_sheet = spreadsheet.add_worksheet(title="Projects", rows=1000, cols=10)
            print("تم إنشاء ورقة المشاريع الجديدة")
        
        # إضافة رؤوس الأعمدة
        headers = [
            "project_id", 
            "project_name", 
            "company_id", 
            "area_name", 
            "project_type", 
            "description", 
            "status"
        ]
        
        # التحقق مما إذا كانت الرؤوس موجودة بالفعل
        existing_headers = projects_sheet.row_values(1)
        if not existing_headers or existing_headers != headers:
            projects_sheet.clear()  # مسح أي بيانات موجودة
            projects_sheet.append_row(headers)
            print("تم إضافة رؤوس الأعمدة إلى ورقة المشاريع")
        
        # تنسيق الورقة
        projects_sheet.format('A1:G1', {'textFormat': {'bold': True}})
        
        return projects_sheet
    except Exception as e:
        print(f"خطأ في إنشاء ورقة المشاريع: {e}")
        return None

def create_settings_sheet(spreadsheet):
    """
    إنشاء ورقة الإعدادات
    """
    try:
        # محاولة الوصول إلى ورقة الإعدادات أو إنشائها إذا لم تكن موجودة
        try:
            settings_sheet = spreadsheet.worksheet("Settings")
            print("تم العثور على ورقة الإعدادات الموجودة")
        except gspread.exceptions.WorksheetNotFound:
            settings_sheet = spreadsheet.add_worksheet(title="Settings", rows=100, cols=5)
            print("تم إنشاء ورقة الإعدادات الجديدة")
        
        # إضافة رؤوس الأعمدة
        headers = [
            "setting_name", 
            "setting_value", 
            "description"
        ]
        
        # التحقق مما إذا كانت الرؤوس موجودة بالفعل
        existing_headers = settings_sheet.row_values(1)
        if not existing_headers or existing_headers != headers:
            settings_sheet.clear()  # مسح أي بيانات موجودة
            settings_sheet.append_row(headers)
            print("تم إضافة رؤوس الأعمدة إلى ورقة الإعدادات")
            
            # إضافة بعض الإعدادات الافتراضية
            default_settings = [
                ["booking_days", "Saturday,Tuesday", "أيام الحجز المسموح بها"],
                ["booking_time", "12:00-12:30", "وقت الحجز"],
                ["weeks_ahead", "8", "عدد الأسابيع المتاحة للحجز مسبقًا"],
                ["company_name", "شركة التطوير العقاري الرائدة", "اسم الشركة"],
                ["app_title", "نظام حجز مواعيد العروض التقديمية للتطوير العقاري", "عنوان التطبيق"]
            ]
            settings_sheet.append_rows(default_settings)
            print("تم إضافة الإعدادات الافتراضية")
        
        # تنسيق الورقة
        settings_sheet.format('A1:C1', {'textFormat': {'bold': True}})
        
        return settings_sheet
    except Exception as e:
        print(f"خطأ في إنشاء ورقة الإعدادات: {e}")
        return None

def generate_available_slots(slots_sheet, weeks_ahead=8):
    """
    إنشاء المواعيد المتاحة للأسابيع القادمة
    فقط أيام السبت والثلاثاء من الساعة 12:00 إلى 12:30
    """
    try:
        # الحصول على المواعيد الموجودة
        existing_slots = slots_sheet.get_all_records()
        existing_dates = [slot["slot_date"] for slot in existing_slots]
        
        # تاريخ اليوم
        today = datetime.now().date()
        
        # إنشاء قائمة بالمواعيد المتاحة
        available_slots = []
        
        # إنشاء المواعيد للأسابيع القادمة
        for i in range(weeks_ahead * 7):
            # تاريخ اليوم + i أيام
            date = today + timedelta(days=i)
            
            # التحقق مما إذا كان اليوم سبت (5) أو ثلاثاء (1)
            if date.weekday() == 5 or date.weekday() == 1:
                # تنسيق التاريخ بصيغة YYYY-MM-DD
                date_str = date.strftime("%Y-%m-%d")
                
                # التحقق مما إذا كان التاريخ موجودًا بالفعل
                if date_str not in existing_dates:
                    # إنشاء معرف فريد للموعد
                    slot_id = f"SL{date_str.replace('-', '')}"
                    
                    # اسم اليوم بالإنجليزية
                    day_name = "Saturday" if date.weekday() == 5 else "Tuesday"
                    
                    # إضافة الموعد المتاح (12:00 - 12:30)
                    available_slots.append([
                        slot_id,
                        date_str,
                        day_name,
                        "12:00-12:30",
                        "Yes",
                        ""
                    ])
        
        # إضافة المواعيد المتاحة إلى ورقة العمل
        if available_slots:
            slots_sheet.append_rows(available_slots)
            print(f"تم إضافة {len(available_slots)} موعد متاح جديد")
        else:
            print("لا توجد مواعيد جديدة لإضافتها")
        
        return len(available_slots)
    except Exception as e:
        print(f"خطأ في إنشاء المواعيد المتاحة: {e}")
        return 0

def add_sample_data(spreadsheet):
    """
    إضافة بيانات نموذجية للتجربة
    """
    try:
        # إضافة شركات نموذجية
        companies_sheet = spreadsheet.worksheet("Companies")
        sample_companies = [
            ["CP001", "شركة الأفق للتطوير العقاري", "أحمد محمد", "ahmed@horizon.example.com", "0123456789", "القاهرة، مصر", ""],
            ["CP002", "شركة النخبة للاستثمار العقاري", "سارة علي", "sara@elite.example.com", "0123456788", "الإسكندرية، مصر", ""],
            ["CP003", "مجموعة الرواد العقارية", "محمد خالد", "mohamed@pioneers.example.com", "0123456787", "الجيزة، مصر", ""]
        ]
        
        # التحقق من وجود بيانات
        existing_data = companies_sheet.get_all_records()
        if len(existing_data) == 0:
            companies_sheet.append_rows(sample_companies)
            print("تم إضافة شركات نموذجية")
        
        # إضافة مشاريع نموذجية
        projects_sheet = spreadsheet.worksheet("Projects")
        sample_projects = [
            ["PR001", "أبراج النيل", "CP001", "المعادي", "سكني", "مجمع سكني فاخر بإطلالة على النيل", "قيد الإنشاء"],
            ["PR002", "واحة الزهور", "CP002", "التجمع الخامس", "سكني", "كمبوند سكني متكامل الخدمات", "مكتمل"],
            ["PR003", "مول المستقبل", "CP003", "6 أكتوبر", "تجاري", "مركز تسوق عصري", "قيد الإنشاء"],
            ["PR004", "أبراج السلام", "CP001", "نصر سيتي", "سكني", "أبراج سكنية فاخرة", "مكتمل"]
        ]
        
        # التحقق من وجود بيانات
        existing_data = projects_sheet.get_all_records()
        if len(existing_data) == 0:
            projects_sheet.append_rows(sample_projects)
            print("تم إضافة مشاريع نموذجية")
        
        # إضافة حجوزات نموذجية
        bookings_sheet = spreadsheet.worksheet("Bookings")
        
        # الحصول على المواعيد المتاحة
        slots_sheet = spreadsheet.worksheet("Available_Slots")
        available_slots = slots_sheet.get_all_records()
        
        # اختيار موعدين متاحين للحجوزات النموذجية
        sample_slots = []
        for slot in available_slots:
            if slot["is_available"] == "Yes" and len(sample_slots) < 2:
                sample_slots.append(slot)
        
        # إضافة حجوزات نموذجية إذا كانت هناك مواعيد متاحة
        if len(sample_slots) >= 2:
            now = datetime.now()
            sample_bookings = [
                [
                    f"BK{now.strftime('%Y%m%d%H%M%S')}1",
                    "شركة الأفق للتطوير العقاري",
                    "المعادي",
                    "أبراج النيل",
                    "أحمد محمد",
                    "ahmed@horizon.example.com",
                    "0123456789",
                    sample_slots[0]["slot_date"],
                    sample_slots[0]["slot_time"],
                    "Confirmed",
                    "عرض تقديمي للمرحلة الأولى من المشروع",
                    now.strftime("%Y-%m-%d %H:%M:%S"),
                    now.strftime("%Y-%m-%d %H:%M:%S")
                ],
                [
                    f"BK{now.strftime('%Y%m%d%H%M%S')}2",
                    "شركة النخبة للاستثمار العقاري",
                    "التجمع الخامس",
                    "واحة الزهور",
                    "سارة علي",
                    "sara@elite.example.com",
                    "0123456788",
                    sample_slots[1]["slot_date"],
                    sample_slots[1]["slot_time"],
                    "Confirmed",
                    "عرض تقديمي للمرحلة النهائية من المشروع",
                    now.strftime("%Y-%m-%d %H:%M:%S"),
                    now.strftime("%Y-%m-%d %H:%M:%S")
                ]
            ]
            
            # التحقق من وجود بيانات
            existing_data = bookings_sheet.get_all_records()
            if len(existing_data) == 0:
                bookings_s
(Content truncated due to size limit. Use line ranges to read in chunks)