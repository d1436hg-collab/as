import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import datetime

# --- 1. إعدادات الصفحة والتصميم ---
st.set_page_config(
    page_title="نظام تقارير الدرجات",
    layout="centered",
    initial_sidebar_state="collapsed",
    page_icon="🎓"
)

# --- 2. CSS مخصص للطباعة والتجميل (هذا هو السر في الاحترافية) ---
st.markdown("""
    <style>
        /* تحسين الخطوط والتصميم العام */
        @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Tajawal', sans-serif;
        }
        
        /* تصميم الكروت (Cards) */
        .metric-card {
            background-color: #f8f9fa;
            border-radius: 10px;
            padding: 15px;
            border: 1px solid #e9ecef;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            text-align: center;
        }

        /* --- إعدادات الطباعة وتصدير PDF --- */
        @media print {
            /* إخفاء العناصر غير الضرورية عند الطباعة */
            [data-testid="stSidebar"], 
            header, 
            footer, 
            .stFileUploader, 
            .stButton, 
            .no-print {
                display: none !important;
            }
            
            /* توسيع المحتوى ليشمل كامل الورقة */
            .main .block-container {
                max-width: 100% !important;
                padding: 1rem !important;
            }
            
            /* تنسيق الجداول للطباعة */
            table {
                width: 100% !important;
                border-collapse: collapse !important;
                font-size: 12px !important;
            }
            
            /* ضمان عدم قص الرسوم البيانية بين الصفحات */
            .plotly-graph-div {
                break-inside: avoid;
            }
        }
    </style>
""", unsafe_allow_html=True)

# --- 3. المنطق البرمجي ---

def main():
    # القائمة الجانبية (ستختفي عند الطباعة)
    with st.sidebar:
        st.header("⚙️ إعدادات التقرير")
        max_grade = st.number_input("الدرجة العظمى:", min_value=1, value=100)
        uploaded_file = st.file_uploader("ارفع ملف الدرجات (Excel):", type=["xlsx", "xls"])
        
        st.markdown("---")
        st.info("💡 **كيفية حفظ التقرير PDF:**\n\nبعد ظهور النتائج، اضغط على زر الطباعة في متصفحك (أو Ctrl+P) واختر **'Save as PDF'**.\n\nسيقوم البرنامج تلقائياً بتنسيق الصفحة وحذف القوائم الجانبية.")

    # العنوان والتاريخ
    col_header1, col_header2 = st.columns([3, 1])
    with col_header1:
        st.title("🎓 تقرير تحليل نتائج الطلاب")
        st.caption("تقرير تحليلي تفصيلي للأداء الأكاديمي")
    with col_header2:
        st.text(f"تاريخ التقرير:\n{datetime.date.today()}")

    if uploaded_file is not None:
        try:
            # معالجة البيانات
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
            
            # ترتيب حسب الدرجة
            df = df.sort_values(by='Grade', ascending=False)
            
            # تقسيم البيانات
            df_high = df[df['Classification'] == "فوق المتوسط (متميز)"]
            df_mid = df[df['Classification'] == "متوسط"]
            df_low = df[df['Classification'] == "دون المتوسط"]

            # --- عرض المؤشرات (KPIs) ---
            st.markdown("### 📌 ملخص الأداء العام")
            kpi1, kpi2, kpi3, kpi4 = st.columns(4)
            
            # استخدام HTML مخصص لعرض أجمل
            def card(title, value, color):
                return f"""
                <div class="metric-card" style="border-top: 5px solid {color};">
                    <p style="margin:0; font-size:0.9rem; color:#666;">{title}</p>
                    <h3 style="margin:0; color:#333;">{value}</h3>
                </div>
                """
            
            kpi1.markdown(card("إجمالي الطلاب", len(df), "#3498db"), unsafe_allow_html=True)
            kpi2.markdown(card("متوسط الدرجات", f"{df['Grade'].mean():.1f}", "#f1c40f"), unsafe_allow_html=True)
            kpi3.markdown(card("أعلى درجة", df['Grade'].max(), "#2ecc71"), unsafe_allow_html=True)
            kpi4.markdown(card("نسبة النجاح", f"{(len(df[df['Grade']>= (max_grade*0.6)])/len(df)*100):.0f}%", "#9b59b6"), unsafe_allow_html=True)

            st.markdown("---")

            # --- الرسوم البيانية ---
            st.markdown("### 📊 التحليل البياني")
            chart_col1, chart_col2 = st.columns(2)
            
            with chart_col1:
                # رسم حلقي (Donut)
                counts = df['Classification'].value_counts().reset_index()
                counts.columns = ['Level', 'Count']
                fig_pie = px.pie(counts, values='Count', names='Level', hole=0.6,
                                 color='Level',
                                 color_discrete_map={
                                     "فوق المتوسط (متميز)": "#27ae60",
                                     "متوسط": "#f39c12",
                                     "دون المتوسط": "#c0392b"
                                 })
                fig_pie.update_layout(title_text="توزيع المستويات", margin=dict(t=30, b=0, l=0, r=0))
                st.plotly_chart(fig_pie, use_container_width=True)
            
            with chart_col2:
                # رسم بياني للأعمدة مع خط المتوسط
                fig_bar = px.histogram(df, x="Grade", nbins=10, 
                                       color_discrete_sequence=['#2980b9'])
                fig_bar.add_vline(x=df['Grade'].mean(), line_dash="dash", line_color="red", 
                                  annotation_text="المتوسط")
                fig_bar.update_layout(title_text="توزيع الدرجات وتكرارها", 
                                      xaxis_title="الدرجة", yaxis_title="عدد الطلاب",
                                      margin=dict(t=30, b=0, l=0, r=0))
                st.plotly_chart(fig_bar, use_container_width=True)

            st.markdown("---")

            # --- الجداول التفصيلية (قسم جديد للطباعة) ---
            st.markdown("### 📋 قوائم الطلاب التفصيلية")
            
            # دالة مساعدة لتنسيق الجدول
            def style_dataframe(dataframe, color_header):
                return dataframe[['Student_Name', 'Grade']].style.format({"Grade": "{:.1f}"})\
                    .set_properties(**{'text-align': 'right', 'background-color': '#ffffff'})\
                    .set_table_styles([{
                        'selector': 'th',
                        'props': [('background-color', color_header), ('color', 'white'), ('text-align', 'right')]
                    }])

            # 1. المتميزون
            if not df_high.empty:
                st.markdown(f"#### 🌟 فوق المتوسط (العدد: {len(df_high)})")
                st.dataframe(df_high[['Student_Name', 'Grade']], use_container_width=True, hide_index=True)
            
            # 2. المتوسطون
            if not df_mid.empty:
                st.markdown(f"#### ⚖️ متوسط (العدد: {len(df_mid)})")
                st.dataframe(df_mid[['Student_Name', 'Grade']], use_container_width=True, hide_index=True)
            
            # 3. المتعثرون
            if not df_low.empty:
                st.markdown(f"#### ⚠️ دون المتوسط (العدد: {len(df_low)})")
                st.dataframe(df_low[['Student_Name', 'Grade']], use_container_width=True, hide_index=True)

            # --- قسم التحميل (يظهر فقط في الشاشة ويختفي عند الطباعة) ---
            st.markdown('<div class="no-print">', unsafe_allow_html=True)
            st.markdown("---")
            st.warning("🖨️ **للحصول على ملف PDF:** اضغط Ctrl+P في لوحة المفاتيح، أو اختر 'طباعة' من المتصفح، ثم اختر الحفظ بتنسيق PDF.")
            
            csv = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="📥 تحميل البيانات (Excel/CSV)",
                data=csv,
                file_name='report.csv',
                mime='text/csv',
                use_container_width=True
            )
            st.markdown('</div>', unsafe_allow_html=True)

        except Exception as e:
            st.error(f"حدث خطأ: {e}")
    else:
        st.info("الرجاء رفع الملف من القائمة الجانبية لبدء التحليل.")

if __name__ == "__main__":
    main()
