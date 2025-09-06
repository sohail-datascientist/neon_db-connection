import streamlit as st
import psycopg2
import pandas as pd
import plotly.express as px

# -----------------------
# 1. Database Connection
# -----------------------
DB_URL = "postgresql://neondb_owner:npg_LBOw3u0GyCpR@ep-lively-bar-ad4bzrb3-pooler.c-2.us-east-1.aws.neon.tech/exam?sslmode=require&channel_binding=require"

@st.cache_resource
def get_connection():
    return psycopg2.connect(DB_URL)

def run_query(query):
    conn = get_connection()
    df = pd.read_sql(query, conn)
    return df

# -----------------------
# 2. Streamlit UI
# -----------------------
st.set_page_config(page_title="📊 GPA Dashboard", layout="wide")
st.title("🎓 GPA Dashboard (Neon + Streamlit)")

tabs = st.tabs([
    "📘 Student Total Marks",
    "📊 Student Percentage",
    "📚 Student Course GPA",
    "📝 Semester GPA",
    "📈 CGPA",
    "🏫 Batch GPA",
    "🏆 Batch CGPA",
    "📉 Batch GPA Trend",
    "📋 Dashboard"
])

# -----------------------
# 3. Tab Contents
# -----------------------

with tabs[0]:
    st.subheader("Student Total Marks")
    df = run_query("SELECT * FROM student_total_marks ORDER BY regno, rid LIMIT 100;")
    st.dataframe(df, use_container_width=True)
    st.download_button("⬇ Download CSV", df.to_csv(index=False), "student_total_marks.csv")

with tabs[1]:
    st.subheader("Student Percentage")
    df = run_query("SELECT * FROM student_percentage ORDER BY regno, rid LIMIT 150;")
    st.dataframe(df, use_container_width=True)
    st.download_button("⬇ Download CSV", df.to_csv(index=False), "student_percentage.csv")

with tabs[2]:
    st.subheader("Student Course GPA")
    df = run_query("SELECT * FROM student_course_gpa ORDER BY regno, year, semester LIMIT 150;")
    st.dataframe(df, use_container_width=True)
    st.download_button("⬇ Download CSV", df.to_csv(index=False), "student_course_gpa.csv")

with tabs[3]:
    st.subheader("Semester GPA")
    df = run_query("SELECT * FROM semester_gpa ORDER BY year, semester, regno LIMIT 150;")
    st.dataframe(df, use_container_width=True)
    st.download_button("⬇ Download CSV", df.to_csv(index=False), "semester_gpa.csv")

with tabs[4]:
    st.subheader("Cumulative GPA (CGPA)")
    df = run_query("SELECT * FROM cgpa ORDER BY cgpa DESC LIMIT 150;")
    st.dataframe(df, use_container_width=True)
    top_chart = px.bar(df.head(10), x="regno", y="cgpa", title="Top 10 Students by CGPA")
    st.plotly_chart(top_chart, use_container_width=True)
    st.download_button("⬇ Download CSV", df.to_csv(index=False), "cgpa.csv")

with tabs[5]:
    st.subheader("Batch GPA")
    df = run_query("SELECT * FROM batch_gpa ORDER BY class, year, semester LIMIT 100;")
    st.dataframe(df, use_container_width=True)
    st.download_button("⬇ Download CSV", df.to_csv(index=False), "batch_gpa.csv")

with tabs[6]:
    st.subheader("Batch CGPA")
    df = run_query("SELECT * FROM batch_cgpa ORDER BY class LIMIT 100;")
    st.dataframe(df, use_container_width=True)
    st.download_button("⬇ Download CSV", df.to_csv(index=False), "batch_cgpa.csv")

with tabs[7]:
    st.subheader("Batch GPA Trend")
    df = run_query("SELECT * FROM batch_gpa_trend ORDER BY class, year, semester LIMIT 100;")
    st.dataframe(df, use_container_width=True)
    trend_chart = px.line(df, x="semester", y="avg_batch_gpa", color="class", markers=True, title="Batch GPA Trend")
    st.plotly_chart(trend_chart, use_container_width=True)
    st.download_button("⬇ Download CSV", df.to_csv(index=False), "batch_gpa_trend.csv")

with tabs[8]:
    st.subheader("Full Dashboard")
    df = run_query("SELECT * FROM dashboard ORDER BY class, year, semester, regno LIMIT 100;")
    st.dataframe(df, use_container_width=True)
    comparison_chart = px.scatter(df, x="semester_gpa", y="batch_gpa", color="class", hover_name="student_name", title="Student GPA vs Batch Average")
    st.plotly_chart(comparison_chart, use_container_width=True)
    st.download_button("⬇ Download CSV", df.to_csv(index=False), "dashboard.csv")

