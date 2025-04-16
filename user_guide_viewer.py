import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

def main():
    st.set_page_config(
        page_title="دليل المستخدم",
        page_icon="📚",
        layout="wide"
    )
    
    st.title("دليل المستخدم - تطبيق حجز مواعيد العروض التقديمية")
    
    # قراءة محتوى دليل المستخدم
    with open("user_guide.md", "r", encoding="utf-8") as f:
        user_guide_content = f.read()
    
    # عرض دليل المستخدم
    st.markdown(user_guide_content)
    
    # إضافة زر لتنزيل دليل المستخدم
    st.download_button(
        label="تنزيل دليل المستخدم (PDF)",
        data=user_guide_content,
        file_name="user_guide.md",
        mime="text/markdown"
    )

if __name__ == "__main__":
    main()
