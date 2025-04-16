from PIL import Image, ImageDraw, ImageFont
import os
import io
import numpy as np

def create_logo():
    """
    إنشاء شعار لشركة التطوير العقاري
    """
    # إنشاء صورة فارغة بخلفية بيضاء
    width, height = 500, 300
    background_color = (255, 255, 255)
    logo = Image.new('RGBA', (width, height), background_color)
    
    # إنشاء كائن الرسم
    draw = ImageDraw.Draw(logo)
    
    # رسم شكل مبنى
    building_color = (30, 136, 229)  # أزرق
    
    # رسم المبنى الرئيسي
    building_points = [
        (150, 250),  # أسفل يسار
        (150, 100),  # أعلى يسار
        (250, 50),   # أعلى وسط
        (350, 100),  # أعلى يمين
        (350, 250),  # أسفل يمين
    ]
    draw.polygon(building_points, fill=building_color)
    
    # رسم نوافذ المبنى
    window_color = (255, 193, 7)  # أصفر ذهبي
    
    # الصف الأول من النوافذ
    draw.rectangle([180, 120, 210, 150], fill=window_color)
    draw.rectangle([240, 120, 270, 150], fill=window_color)
    draw.rectangle([290, 120, 320, 150], fill=window_color)
    
    # الصف الثاني من النوافذ
    draw.rectangle([180, 170, 210, 200], fill=window_color)
    draw.rectangle([240, 170, 270, 200], fill=window_color)
    draw.rectangle([290, 170, 320, 200], fill=window_color)
    
    # رسم باب المبنى
    door_color = (76, 175, 80)  # أخضر
    draw.rectangle([230, 200, 270, 250], fill=door_color)
    
    # إضافة دائرة تمثل الشمس
    sun_color = (255, 193, 7)  # أصفر ذهبي
    draw.ellipse([50, 50, 100, 100], fill=sun_color)
    
    # إضافة أشعة الشمس
    for i in range(8):
        angle = i * 45
        x1 = 75 + 30 * np.cos(np.radians(angle))
        y1 = 75 + 30 * np.sin(np.radians(angle))
        x2 = 75 + 50 * np.cos(np.radians(angle))
        y2 = 75 + 50 * np.sin(np.radians(angle))
        draw.line([(x1, y1), (x2, y2)], fill=sun_color, width=3)
    
    # إضافة نص اسم الشركة
    company_name = "شركة التطوير العقاري الرائدة"
    
    # محاولة تحميل خط عربي، إذا لم يكن متاحًا استخدم الخط الافتراضي
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", 24)
    except IOError:
        font = ImageFont.load_default()
    
    # حساب موضع النص
    text_width = draw.textlength(company_name, font=font)
    text_position = ((width - text_width) / 2, height - 40)
    
    # إضافة النص
    draw.text(text_position, company_name, fill=(33, 33, 33), font=font)
    
    # حفظ الشعار
    logo_path = os.path.join("assets", "logo.png")
    logo.save(logo_path)
    
    return logo_path

def create_favicon():
    """
    إنشاء أيقونة للموقع
    """
    # إنشاء صورة فارغة بخلفية شفافة
    size = 32
    favicon = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    
    # إنشاء كائن الرسم
    draw = ImageDraw.Draw(favicon)
    
    # رسم مبنى مبسط
    building_color = (30, 136, 229, 255)  # أزرق
    
    # رسم المبنى
    building_points = [
        (8, 28),   # أسفل يسار
        (8, 12),   # أعلى يسار
        (16, 4),   # أعلى وسط
        (24, 12),  # أعلى يمين
        (24, 28),  # أسفل يمين
    ]
    draw.polygon(building_points, fill=building_color)
    
    # رسم نوافذ المبنى
    window_color = (255, 193, 7, 255)  # أصفر ذهبي
    
    # نوافذ
    draw.rectangle([12, 14, 14, 18], fill=window_color)
    draw.rectangle([18, 14, 20, 18], fill=window_color)
    draw.rectangle([12, 20, 14, 24], fill=window_color)
    draw.rectangle([18, 20, 20, 24], fill=window_color)
    
    # حفظ الأيقونة
    favicon_path = os.path.join("assets", "favicon.ico")
    favicon.save(favicon_path)
    
    return favicon_path

def create_css_file():
    """
    إنشاء ملف CSS للتنسيق
    """
    css_content = """
    /* أنماط عامة */
    body {
        font-family: 'Arial', 'Tahoma', sans-serif;
        direction: rtl;
        text-align: right;
        background-color: #F5F5F5;
        color: #212121;
    }
    
    /* أنماط الرأس */
    .app-header {
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .app-logo {
        max-width: 200px;
        margin-bottom: 1rem;
    }
    
    /* أنماط الأزرار */
    .stButton > button {
        background-color: #1E88E5;
        color: white;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-weight: bold;
        transition: background-color 0.3s;
    }
    
    .stButton > button:hover {
        background-color: #1565C0;
    }
    
    /* أنماط بطاقات الحجز */
    .booking-card {
        background-color: white;
        padding: 1rem;
        border-radius: 5px;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
        transition: transform 0.3s;
    }
    
    .booking-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
    }
    
    .booking-header {
        font-weight: bold;
        color: #1E88E5;
        margin-bottom: 0.5rem;
        font-size: 1.2rem;
    }
    
    .booking-info {
        margin-bottom: 0.5rem;
    }
    
    /* أنماط حالات الحجز */
    .booking-status-confirmed {
        color: #4CAF50;
        font-weight: bold;
    }
    
    .booking-status-cancelled {
        color: #F44336;
        font-weight: bold;
    }
    
    .booking-status-rescheduled {
        color: #FFC107;
        font-weight: bold;
    }
    
    /* أنماط الرسائل */
    .success-message {
        background-color: #4CAF50;
        color: white;
        padding: 1rem;
        border-radius: 5px;
        margin-bottom: 1rem;
    }
    
    .error-message {
        background-color: #F44336;
        color: white;
        padding: 1rem;
        border-radius: 5px;
        margin-bottom: 1rem;
    }
    
    /* أنماط النماذج */
    .stTextInput > div > div > input {
        text-align: right;
    }
    
    .stSelectbox div[data-baseweb="select"] > div {
        text-align: right;
    }
    
    /* أنماط الصفحة الرئيسية */
    .home-feature {
        background-color: white;
        padding: 1rem;
        border-radius: 5px;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
        text-align: center;
    }
    
    .home-feature-icon {
        font-size: 2rem;
        color: #1E88E5;
        margin-bottom: 0.5rem;
    }
    
    .home-feature-title {
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    
    /* أنماط التذييل */
    .footer {
        text-align: center;
        margin-top: 2rem;
        padding-top: 1rem;
        border-top: 1px solid #E0E0E0;
        color: #757575;
    }
    """
    
    # حفظ ملف CSS
    css_path = os.path.join("assets", "styles.css")
    with open(css_path, "w") as f:
        f.write(css_content)
    
    return css_path

if __name__ == "__main__":
    # إنشاء الشعار
    logo_path = create_logo()
    print(f"تم إنشاء الشعار في: {logo_path}")
    
    # إنشاء الأيقونة
    favicon_path = create_favicon()
    print(f"تم إنشاء الأيقونة في: {favicon_path}")
    
    # إنشاء ملف CSS
    css_path = create_css_file()
    print(f"تم إنشاء ملف CSS في: {css_path}")
