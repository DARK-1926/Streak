import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
from datetime import datetime, timezone
from tagger import generate_tags

# ----------------------------------------------------------------------
# Helper Functions
# ----------------------------------------------------------------------
def get_db_connection():
    """Return a cached SQLite connection."""
    if "db_conn" not in st.session_state:
        conn = sqlite3.connect("incidents.db", check_same_thread=False)
        conn.row_factory = sqlite3.Row
        st.session_state.db_conn = conn
        _initialize_db(conn)
    return st.session_state.db_conn

def _initialize_db(conn):
    """Create the issues table if it does not exist."""
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS issues (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                tags TEXT,
                created_at TIMESTAMP NOT NULL
            )
            """
        )
        conn.commit()
    except Exception as e:
        st.error(f"Database initialization failed: {e}")

def insert_issue(title: str, description: str, tags: str):
    """Insert a new issue record."""
    conn = get_db_connection()
    try:
        created_at = datetime.now(timezone.utc)
        conn.execute(
            """
            INSERT INTO issues (title, description, tags, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (title, description, tags, created_at),
        )
        conn.commit()
        st.success("Issue logged successfully!")
    except Exception as e:
        st.error(f"Failed to insert issue: {e}")

def fetch_issues():
    """Retrieve all issues as a DataFrame."""
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT * FROM issues", conn, parse_dates=["created_at"])
    return df

def export_csv(df: pd.DataFrame):
    """Provide a CSV download button."""
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download CSV",
        data=csv,
        file_name="issues_log.csv",
        mime="text/csv",
    )

def get_top_tags(df: pd.DataFrame, top_n: int = 10):
    """Return a DataFrame with top N tags."""
    if df.empty:
        return pd.DataFrame(columns=["tag", "count"])
    tags_series = df["tags"].dropna().str.split(",", expand=True).stack().str.strip()
    tag_counts = tags_series.value_counts().reset_index()
    tag_counts.columns = ["tag", "count"]
    return tag_counts.head(top_n)

def incidents_per_week(df: pd.DataFrame):
    """Return a DataFrame with incident counts per week."""
    if df.empty:
        return pd.DataFrame(columns=["week", "count"])
    df["week"] = df["created_at"].dt.to_period("W").apply(lambda r: r.start_time)
    weekly = df.groupby("week").size().reset_index(name="count")
    weekly = weekly.sort_values("week")
    return weekly

# ----------------------------------------------------------------------
# Streamlit App Layout
# ----------------------------------------------------------------------
st.set_page_config(page_title="InsightPulse – IT Issue Tracker", layout="wide")

st.title("🔎 InsightPulse – Local AI‑Powered IT Issue Tracker")

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Log Issue", "View Log", "Analytics"])

# ----------------------------------------------------------------------
# Page: Log Issue
# ----------------------------------------------------------------------
if page == "Log Issue":
    st.header("📝 Log a New Issue")
    with st.form(key="log_issue_form"):
        title = st.text_input("Issue Title", max_chars=100)
        description = st.text_area("Issue Description", height=200)
        submit = st.form_submit_button("Submit")

    if submit:
        if not title.strip() or not description.strip():
            st.error("Both title and description are required.")
        else:
            with st.spinner("Generating tags..."):
                try:
                    tags = generate_tags(f"{title}\n\n{description}")
                    tags = tags.strip()
                except Exception as e:
                    st.error(f"Tag generation failed: {e}")
                    tags = ""
            insert_issue(title.strip(), description.strip(), tags)
            st.info(f"Generated Tags: {tags}")

    st.info(
        "All issues are stored locally. No data leaves your environment."
    )

# ----------------------------------------------------------------------
# Page: View Log
# ----------------------------------------------------------------------
elif page == "View Log":
    st.header("📋 View Issue Log")
    df = fetch_issues()

    if df.empty:
        st.info("No issues logged yet.")
    else:
        # Search box
        search_term = st.text_input("Search", placeholder="Enter keyword...")
        if search_term:
            mask = (
                df["title"].str.contains(search_term, case=False, na=False)
                | df["description"].str.contains(search_term, case=False, na=False)
                | df["tags"].str.contains(search_term, case=False, na=False)
            )
            df_display = df[mask]
        else:
            df_display = df

        # Sorting
        sort_by = st.selectbox(
            "Sort by",
            options=["created_at", "title", "id"],
            index=0,
        )
        ascending = st.checkbox("Ascending", value=False)
        df_display = df_display.sort_values(sort_by, ascending=ascending)

        st.dataframe(df_display, use_container_width=True)

        export_csv(df_display)

# ----------------------------------------------------------------------
# Page: Analytics
# ----------------------------------------------------------------------
elif page == "Analytics":
    st.header("📊 Analytics Dashboard")
    df = fetch_issues()

    if df.empty:
        st.info("No data to analyze yet.")
    else:
        # Top Tags Bar Chart
        top_tags_df = get_top_tags(df)
        if not top_tags_df.empty:
            fig_tags = px.bar(
                top_tags_df,
                x="count",
                y="tag",
                orientation="h",
                title="Top 10 Tags",
                labels={"count": "Occurrences", "tag": "Tag"},
            )
            fig_tags.update_layout(yaxis=dict(autorange="reversed"))
            st.plotly_chart(fig_tags, use_container_width=True)
        else:
            st.info("No tags available for charting.")

        # Incidents per Week Line Chart
        weekly_df = incidents_per_week(df)
        if not weekly_df.empty:
            fig_time = px.line(
                weekly_df,
                x="week",
                y="count",
                title="Incidents per Week",
                markers=True,
                labels={"week": "Week Starting", "count": "Number of Incidents"},
            )
            st.plotly_chart(fig_time, use_container_width=True)
        else:
            st.info("Insufficient temporal data for time‑series chart.")

# ----------------------------------------------------------------------
# Collapsible Raw Prompt Section
# ----------------------------------------------------------------------
with st.expander("🔍 Show raw model generation prompt"):
    st.code(
        """You are an AI assistant tasked with generating concise, comma‑separated tags that describe the core IT issue based on the provided title and description. Return only the tags without any additional text.\n\nTitle: {title}\n\nDescription: {description}\n\nTags:""",
        language="text",
    )