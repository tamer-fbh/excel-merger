import io
import pandas as pd
import streamlit as st

# 1. إعدادات الصفحة
st.set_page_config(
    page_title="أداة دمج وتنظيف الإكسل",
    page_icon="📊",
    layout="centered",
)

# 2. تنسيق عربي متجاوب مع الموبايل والكمبيوتر بدون تداخل
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Cairo', sans-serif !important;
    }

    /* تطبيق الاتجاه العربي على محتوى الصفحة فقط لتجنب مشاكل شاشة الموبايل */
    .block-container, [data-testid="stMainBlockContainer"] {
        direction: rtl;
        text-align: right;
    }

    div[data-testid="stMarkdownContainer"] p,
    div[data-testid="stMarkdownContainer"] h1,
    div[data-testid="stMarkdownContainer"] h2,
    div[data-testid="stMarkdownContainer"] h3,
    label[data-testid="stWidgetLabel"] {
        direction: rtl;
        text-align: right;
    }

    /* تجميل كروت الإحصائيات */
    div[data-testid="stMetric"] {
        background-color: #f8f9fa;
        border: 1px solid #e0e4e8;
        padding: 12px;
        border-radius: 10px;
        text-align: center;
    }

    /* تجميل زرار التحميل */
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

# 3. العنوان والوصف
st.title("📊 أداة دمج وتنظيف ملفات الإكسل")
st.write("ارفع ملفات الإكسل الخاصة بك (بأي عدد وأي أعمدة)، وستقوم الأداة بدمجها وتنظيفها في ثوانٍ.")

# 4. رفع الملفات
uploaded_files = st.file_uploader(
    "📂 اضغط لاختيار ملفات الإكسل (يمكنك اختيار أكثر من ملف)",
    type=["xlsx"],
    accept_multiple_files=True,
)

# 5. خيارات التنظيف داخل الصفحة (بدل القائمة الجانبية)
with st.expander("⚙️ خيارات التنظيف (مفعّلة افتراضياً)", expanded=True):
    remove_empty = st.checkbox("حذف الصفوف الفاضية تماماً", value=True)
    remove_dups = st.checkbox("حذف الصفوف المكررة", value=True)
    add_source = st.checkbox("إضافة عمود باسم الملف الأصلي", value=True)

# 6. المعالجة وعرض النتيجة
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

    c1, c2 = st.columns(2)
    c1.metric("📁 عدد الملفات", len(uploaded_files))
    c2.metric("✨ الصفوف النهائية", rows_after)

    c3, c4 = st.columns(2)
    c3.metric("📄 الصفوف قبل التنظيف", rows_before)
    c4.metric("🧹 صفوف تم حذفها", removed_rows)

    st.divider()

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        merged_df.to_excel(writer, index=False, sheet_name="البيانات_المدمجة")
    excel_data = output.getvalue()

    st.download_button(
        label="⬇️ تحميل ملف الإكسل المدمج والمنظف",
        data=excel_data,
        file_name="التقرير_المدمج.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

    st.subheader("👀 معاينة البيانات الناتجة:")
    st.dataframe(merged_df.head(15), use_container_width=True)
else:
    st.info("👆 ابدأ برفع ملفين إكسل أو أكثر من الأعلى لتجربة الأداة.\n\n🔒 يتم معالجة ملفاتك لحظياً ولا يتم حفظ أي بيانات.")
