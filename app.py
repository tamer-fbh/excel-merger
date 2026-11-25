import io
import pandas as pd
import streamlit as st

# 1. إعدادات الصفحة
st.set_page_config(
    page_title="أداة دمج وتنظيف الإكسل",
    page_icon="📊",
    layout="wide",
)

# 2. تنسيق الواجهة للغة العربية (RTL) وخط Cairo الاحترافي
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Cairo', sans-serif !important;
        direction: rtl;
        text-align: right;
    }
    
    /* تجميل الكروت والأزرار */
    div[data-testid="stMetric"] {
        background-color: #f8f9fa;
        border: 1px solid #e0e4e8;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
    }
    
    .stDownloadButton button {
        width: 100%;
        background-color: #0f9d58 !important;
        color: white !important;
        font-size: 18px !important;
        font-weight: bold !important;
        padding: 12px !important;
        border-radius: 8px !important;
        border: none !important;
    }
    
    .stDownloadButton button:hover {
        background-color: #0b8043 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# 3. القائمة الجانبية (Sidebar) للإعدادات
with st.sidebar:
    st.header("⚙️ إعدادات التنظيف")
    st.write("تحكم في طريقة معالجة ملفاتك:")
    remove_empty = st.checkbox("حذف الصفوف الفاضية تماماً", value=True)
    remove_dups = st.checkbox("حذف الصفوف المكررة", value=True)
    add_source = st.checkbox("إضافة عمود باسم الملف الأصلي", value=True)
    
    st.divider()
    st.info("🔒 **الخصوصية:** يتم معالجة ملفاتك لحظياً ولا يتم حفظ أي بيانات على السيرفر.")

# 4. الواجهة الرئيسية
st.title("📊 أداة دمج وتنظيف ملفات الإكسل")
st.markdown("ارفع ملفات الإكسل الخاصة بك (بأي عدد وأي أعمدة)، وستقوم الأداة بدمجها وتنظيفها في ثوانٍ.")

uploaded_files = st.file_uploader(
    "📂 اسحب ملفات الإكسل هنا أو اضغط للاختيار",
    type=["xlsx"],
    accept_multiple_files=True,
)

if uploaded_files:
    with st.spinner("جاري دمج وتنظيف الملفات..."):
        dataframes = []
        for file in uploaded_files:
            df = pd.read_excel(file)
            if add_source:
                df["اسم_الملف_المصدر"] = file.name
            dataframes.append(df)

        merged_df = pd.concat(dataframes, ignore_index=True)
        rows_before = len(merged_df)

        cols_to_check = [c for c in merged_df.columns if c != "اسم_الملف_المصدر"]
        if remove_empty:
            merged_df.dropna(subset=cols_to_check, how="all", inplace=True)
        if remove_dups:
            merged_df.drop_duplicates(subset=cols_to_check, inplace=True)

        rows_after = len(merged_df)
        removed_rows = rows_before - rows_after

    st.success(f"✅ تم دمج {len(uploaded_files)} ملفات بنجاح!")

    # عرض الإحصائيات في كروت شيك
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📁 عدد الملفات", len(uploaded_files))
    c2.metric("📄 الصفوف قبل التنظيف", rows_before)
    c3.metric("🧹 صفوف تم حذفها", removed_rows)
    c4.metric("✨ الصفوف النهائية", rows_after)

    st.divider()

    # تجهيز الملف للتحميل
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        merged_df.to_excel(writer, index=False, sheet_name="البيانات_المدمجة")
    excel_data = output.getvalue()

    # زرار التحميل الكبير
    st.download_button(
        label="⬇️ تحميل ملف الإكسل المدمج والمنظف",
        data=excel_data,
        file_name="التقرير_المدمج.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

    # معاينة البيانات
    st.subheader("👀 معاينة البيانات الناتجة (أول 15 صف):")
    st.dataframe(merged_df.head(15), use_container_width=True)
else:
    st.warning("👆 ابدأ برفع ملفين إكسل أو أكثر من الصندوق بالأعلى لتجربة الأداة.")