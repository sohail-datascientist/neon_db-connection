import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text

# -----------------------
# 1. Database Connection (via SQLAlchemy)
# -----------------------
DB_URL = "postgresql+psycopg2://neondb_owner:npg_LBOw3u0GyCpR@ep-lively-bar-ad4bzrb3-pooler.c-2.us-east-1.aws.neon.tech/exam?sslmode=require"

@st.cache_resource
def get_engine():
    return create_engine(DB_URL, pool_pre_ping=True)

def run_query(query, params=None):
    engine = get_engine()
    with engine.connect() as conn:
        df = pd.read_sql(text(query), conn, params=params)
    return df


# -----------------------
# 2. Streamlit Page Setup
# -----------------------
st.set_page_config(page_title="🎓 GPA Drill-Down", layout="wide")
st.title("📊 Student GPA Drill-Down")

# -----------------------
# 3. Step 1 - Select Year
# -----------------------
years = run_query("SELECT DISTINCT year FROM dashboard ORDER BY year;")["year"].tolist()
selected_year = st.selectbox("📅 Select Year", years)

# -----------------------
# 4. Step 2 - Select Semester (filtered by year)
# -----------------------
semesters = run_query(
    "SELECT DISTINCT semester FROM dashboard WHERE year = :year ORDER BY semester;",
    {"year": selected_year}
)["semester"].tolist()
selected_semester = st.selectbox("📝 Select Semester", semesters)

# -----------------------
# 5. Step 3 - Select Batch (filtered by year + semester)
# -----------------------
batches = run_query(
    "SELECT DISTINCT class FROM dashboard WHERE year = :year AND semester = :semester ORDER BY class;",
    {"year": selected_year, "semester": selected_semester}
)["class"].tolist()
selected_batch = st.selectbox("🏫 Select Batch (Class)", batches)

# -----------------------
# 6. Step 4 - Show Students GPA + CGPA
# -----------------------
students_df = run_query(
    """
    SELECT DISTINCT ON (sg.regno, sg.semester, sg.year)
        sg.regno,
        s.name AS student_name,
        sg.semester_gpa,
        c.cgpa
    FROM semester_gpa sg
    JOIN student s ON sg.regno = s.regno
    JOIN cgpa c ON sg.regno = c.regno
    WHERE sg.year = :year AND sg.semester = :semester AND sg.class = :batch
    ORDER BY sg.regno, sg.semester, sg.year, sg.semester_gpa DESC;
    """,
    {"year": selected_year, "semester": selected_semester, "batch": selected_batch}
)

st.subheader(f"🎓 Results for {selected_batch} - {selected_semester} {selected_year}")

if not students_df.empty:
    # Show Table
    st.dataframe(students_df, use_container_width=True)

    # Batch Cumulative GPA (only 1 value for batch)
    batch_cgpa = run_query(
        """
        SELECT ROUND(AVG(cgpa), 2) AS batch_cgpa
        FROM cgpa
        WHERE class = :batch;
        """,
        {"batch": selected_batch}
    )
    if not batch_cgpa.empty:
        st.metric(label="📌 Batch Cumulative GPA", value=batch_cgpa["batch_cgpa"].iloc[0])

    # Top 5 Students
    st.markdown("🏆 **Top 5 Students by Semester GPA**")
    st.dataframe(students_df.head(5), use_container_width=True)

    # Chart: Semester GPA vs CGPA
    st.bar_chart(students_df.set_index("student_name")[["semester_gpa", "cgpa"]])

    # Download Option
    st.download_button(
        "⬇ Download CSV",
        students_df.to_csv(index=False),
        f"{selected_batch}_{selected_semester}_{selected_year}.csv"
    )
else:
    st.warning("No students found for this selection.")
