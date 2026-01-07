import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# إعدادات الصفحة لتناسب الجوال وسطح المكتب
st.set_page_config(
    page_title="تحليل الدرجات الاحترافي",
    layout="centered",  # التخطيط المتمركز أفضل للجوال من wide
    initial_sidebar_state="collapsed" # القائمة الجانبية مغلقة لتوفير المساحة
)

# تخصيص الألوان لكل فئة
COLORS = {
    "فوق المتوسط (متميز)": "#2ecc71",  # أخضر زمردي
    "متوسط": "#f1c40f",               # أصفر ذهبي
    "دون المتوسط": "#e74c3c"          # أحمر هادئ
}

# العنوان الرئيسي
st.title("📱📊 نظام تحليل الدرجات الذكي")
st.caption("تحليل متقدم متوافق مع كافة الأجهزة")
st.markdown("---")

# --- القائمة الجانبية (الإعدادات) ---
with st.sidebar:
    st.header("⚙️ الإعدادات والرفع")
    max_grade = st.number_input("الدرجة العظمى للاختبار:", min_value=1, value=100)
    uploaded_file = st.file_uploader("ارفع ملف Excel:", type=["xlsx", "xls"])
    st.info("💡 نصيحة: تأكد أن الملف يحتوي على عمودين فقط: الاسم والدرجة.")

# --- المعالجة الرئيسية ---
if uploaded_file is not None:
    try:
        # قراءة البيانات
        df = pd.read_excel(uploaded_file, usecols=[0, 1])
        df.columns = ['Student_Name', 'Grade']
        df['Grade'] = pd.to_numeric(df['Grade'], errors='coerce')
        df.dropna(subset=['Grade'], inplace=True)
        
        # دالة التصنيف
        def classify(g):
            pct = (g / max_grade) * 100
            if pct >= 85: return "فوق المتوسط (متميز)"
            elif pct >= 60: return "متوسط"
            else: return "دون المتوسط"
            
        df['Classification'] = df['Grade'].apply(classify)

        # ترتيب البيانات تنازلياً حسب الدرجة
        df = df.sort_values(by='Grade', ascending=False)

        # --- لوحة المؤشرات (KPIs) ---
        # عرض المؤشرات بشكل متجاوب
        col1, col2, col3 = st.columns(3)
        col1.metric("عدد الطلاب", len(df))
        col2.metric("متوسط الدرجات", f"{df['Grade'].mean():.1f}")
        col3.metric("أعلى درجة", df['Grade'].max())
        st.markdown("---")

        # --- نظام التبويبات للتنظيم ---
        tab1, tab2, tab3 = st.tabs(["📈 الرسوم البيانية", "📋 جداول التصنيف", "📥 تحميل البيانات"])

        with tab1:
            st.subheader("تحليل بصري للنتائج")
            
            # 1. رسم الدونات (Donut Chart) لتوزيع المستويات
            counts = df['Classification'].value_counts().reset_index()
            counts.columns = ['المستوى', 'العدد']
            
            fig_pie = px.pie(counts, values='العدد', names='المستوى', 
                             color='المستوى', color_discrete_map=COLORS,
                             hole=0.5, title="نسب توزيع مستويات الطلاب")
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_pie, use_container_width=True)

            # 2. رسم توزيع الدرجات (Histogram) مع خط المتوسط
            fig_hist = px.histogram(df, x="Grade", nbins=15, title="توزيع تكرار الدرجات",
                                    color_discrete_sequence=['#3498db'])
            
            # إضافة خط يمثل المتوسط
            avg_val = df['Grade'].mean()
            fig_hist.add_vline(x=avg_val, line_dash="dash", line_color="red", 
                               annotation_text=f"المتوسط: {avg_val:.1f}")
            
            fig_hist.update_layout(showlegend=False, xaxis_title="الدرجة", yaxis_title="عدد الطلاب")
            st.plotly_chart(fig_hist, use_container_width=True)

        with tab2:
            st.subheader("تفاصيل الطلاب حسب الفئة")
            
            # تقسيم البيانات إلى 3 جداول منفصلة
            df_high = df[df['Classification'] == "فوق المتوسط (متميز)"]
            df_mid = df[df['Classification'] == "متوسط"]
            df_low = df[df['Classification'] == "دون المتوسط"]

            # 1. جدول المتميزين
            with st.expander(f"🌟 فوق المتوسط (العدد: {len(df_high)})", expanded=True):
                st.dataframe(df_high[['Student_Name', 'Grade']].style.format({"Grade": "{:.1f}"}), use_container_width=True)

            # 2. جدول المتوسطين
            with st.expander(f"⚖️ متوسط (العدد: {len(df_mid)})"):
                st.dataframe(df_mid[['Student_Name', 'Grade']].style.format({"Grade": "{:.1f}"}), use_container_width=True)

            # 3. جدول المتعثرين
            with st.expander(f"⚠️ دون المتوسط (العدد: {len(df_low)})"):
                st.dataframe(df_low[['Student_Name', 'Grade']].style.format({"Grade": "{:.1f}"}), use_container_width=True)

        with tab3:
            st.subheader("تصدير النتائج")
            st.write("يمكنك تحميل الملف كاملاً مع عمود التصنيف الجديد:")
            
            csv = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="📥 تحميل ملف Excel (CSV)",
                data=csv,
                file_name='final_grades_analysis.csv',
                mime='text/csv',
                use_container_width=True
            )

    except Exception as e:
        st.error("عذراً، حدث خطأ في قراءة الملف. تأكد أنه ملف Excel سليم.")
        st.error(f"تفاصيل الخطأ: {e}")

else:
    # شاشة الترحيب عند فتح التطبيق لأول مرة
    st.write("👋 مرحباً! القائمة الجانبية مغلقة في الجوال، اضغط على السهم في الأعلى لفتحها ورفع الملف.")
