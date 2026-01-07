import streamlit as st
import pandas as pd
import plotly.express as px

# إعدادات الصفحة
st.set_page_config(page_title="نظام تحليل وتصنيف الدرجات", layout="wide")

# العنوان
st.title("📊 نظام تحليل وتصنيف درجات الطلاب")
st.markdown("---")

# 1. القائمة الجانبية والإعدادات
st.sidebar.header("⚙️ إعدادات التحليل")

# خانة لتحديد الدرجة النهائية (العظمى)
max_grade = st.sidebar.number_input("أدخل الدرجة النهائية للاختبار (مثلاً 100 أو 50):", min_value=1, value=100)

# رفع الملف
uploaded_file = st.sidebar.file_uploader("ارفع ملف الدرجات (Excel):", type=["xlsx", "xls"])

if uploaded_file is not None:
    try:
        # قراءة الملف (أول عمودين فقط: الاسم والدرجة)
        # usecols=[0, 1] تعني اقرأ العمود الأول والثاني فقط
        df = pd.read_excel(uploaded_file, usecols=[0, 1])
        
        # إعادة تسمية الأعمدة لتسهيل التعامل معها (الاسم، الدرجة)
        df.columns = ['Student_Name', 'Grade']
        
        # التأكد من أن عمود الدرجات رقمي (لتحويل أي نصوص خاطئة إلى أرقام)
        df['Grade'] = pd.to_numeric(df['Grade'], errors='coerce')
        df.dropna(subset=['Grade'], inplace=True) # حذف الصفوف التي لا تحتوي درجات

        st.success("تم استيراد البيانات بنجاح! ✅")

        # 2. منطق التصنيف (فوق المتوسط - متوسط - دون المتوسط)
        # سنستخدم النسب المئوية بناءً على الدرجة النهائية المدخلة
        def classify_student(grade, max_g):
            percentage = (grade / max_g) * 100
            if percentage >= 85: # يمكنك تعديل النسبة من هنا (مثلاً 85% فأكثر)
                return "فوق المتوسط (متميز)"
            elif 60 <= percentage < 85: # من 60% إلى أقل من 85%
                return "متوسط"
            else:
                return "دون المتوسط"

        # تطبيق التصنيف
        df['Classification'] = df['Grade'].apply(lambda x: classify_student(x, max_grade))

        # 3. عرض النتائج
        col1, col2 = st.columns([2, 1])

        with col1:
            st.subheader("📋 قائمة الطلاب والتصنيف")
            st.dataframe(df, use_container_width=True)
            
            # زر لتحميل النتائج الجديدة
            csv = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="📥 تحميل النتائج كملف CSV",
                data=csv,
                file_name='classified_grades.csv',
                mime='text/csv',
            )

        with col2:
            st.subheader("📊 ملخص التحليل")
            
            # عرض المقاييس
            avg_grade = df['Grade'].mean()
            st.metric("متوسط الدرجات الفعلي", f"{avg_grade:.2f} / {max_grade}")
            
            # رسم بياني دائري لتوزيع المستويات
            counts = df['Classification'].value_counts().reset_index()
            counts.columns = ['المستوى', 'العدد']
            
            fig = px.pie(counts, values='العدد', names='المستوى', 
                         title='توزيع الطلاب حسب المستوى',
                         color='المستوى',
                         color_discrete_map={
                             "فوق المتوسط (متميز)": "green",
                             "متوسط": "gold",
                             "دون المتوسط": "red"
                         })
            st.plotly_chart(fig, use_container_width=True)
            
            # رسم بياني للأعمدة (اختياري)
            st.markdown("##### توزيع الدرجات")
            fig_bar = px.bar(df, x='Student_Name', y='Grade', color='Classification', title="درجات الطلاب")
            st.plotly_chart(fig_bar, use_container_width=True)

    except Exception as e:
        st.error(f"حدث خطأ أثناء قراءة الملف. تأكد أن الملف اكسل وأن العمود الأول هو الاسم والثاني هو الدرجة.\nتفاصيل الخطأ: {e}")

else:
    st.info("يرجى رفع ملف Excel يحتوي على: العمود الأول (الاسم) والعمود الثاني (الدرجة).")
