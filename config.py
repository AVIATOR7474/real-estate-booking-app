"""
ملف الإعدادات والتكوين للتطبيق
"""

# عنوان التطبيق
APP_TITLE = "نظام حجز مواعيد العروض التقديمية للتطوير العقاري"

# وصف التطبيق
APP_DESCRIPTION = """
نظام حجز مواعيد العروض التقديمية لشركات التطوير العقاري.
يتيح النظام حجز مواعيد للعروض التقديمية أيام السبت والثلاثاء فقط من الساعة 12:00 ظهراً إلى 12:30 ظهراً.
"""

# اسم الشركة
COMPANY_NAME = "شركة التطوير العقاري الرائدة"

# شعار الشركة (المسار النسبي)
LOGO_PATH = "assets/logo.png"

# ألوان التطبيق
PRIMARY_COLOR = "#1E88E5"  # أزرق
SECONDARY_COLOR = "#FFC107"  # أصفر ذهبي
BACKGROUND_COLOR = "#F5F5F5"  # رمادي فاتح
TEXT_COLOR = "#212121"  # أسود
ACCENT_COLOR = "#4CAF50"  # أخضر

# إعدادات الحجز
BOOKING_DAYS = ["Saturday", "Tuesday"]  # أيام الحجز المسموح بها
BOOKING_TIME = "12:00-12:30"  # وقت الحجز
WEEKS_AHEAD = 8  # عدد الأسابيع المتاحة للحجز مسبقاً

# رسائل النظام
MESSAGES = {
    "booking_success": "تم إنشاء الحجز بنجاح!",
    "booking_error": "حدث خطأ أثناء إنشاء الحجز. يرجى المحاولة مرة أخرى.",
    "reschedule_success": "تم ترحيل الموعد بنجاح!",
    "reschedule_error": "حدث خطأ أثناء ترحيل الموعد. يرجى المحاولة مرة أخرى.",
    "cancel_success": "تم إلغاء الحجز بنجاح!",
    "cancel_error": "حدث خطأ أثناء إلغاء الحجز. يرجى المحاولة مرة أخرى.",
    "no_slots_available": "لا توجد مواعيد متاحة في التاريخ المحدد.",
    "invalid_date": "التاريخ المحدد غير صالح. يرجى اختيار يوم سبت أو ثلاثاء فقط.",
    "required_fields": "يرجى ملء جميع الحقول المطلوبة."
}

# حقول نموذج الحجز
BOOKING_FORM_FIELDS = [
    "company_name",
    "area_name",
    "project_name",
    "representative_name",
    "contact_email",
    "contact_phone",
    "booking_date",
    "notes"
]

# أسماء حقول نموذج الحجز بالعربية
BOOKING_FORM_LABELS = {
    "company_name": "اسم الشركة",
    "area_name": "اسم المنطقة",
    "project_name": "اسم المشروع",
    "representative_name": "اسم ممثل الشركة",
    "contact_email": "البريد الإلكتروني",
    "contact_phone": "رقم الهاتف",
    "booking_date": "تاريخ الحجز",
    "booking_time": "وقت الحجز",
    "notes": "ملاحظات إضافية"
}

# حالات الحجز
BOOKING_STATUS = {
    "confirmed": "مؤكد",
    "cancelled": "ملغي",
    "rescheduled": "مرحل"
}
