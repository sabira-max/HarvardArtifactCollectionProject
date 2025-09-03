                  #PROJECT NO :1 
         ###HARVARD'S ARTIFACTS COLLECTION
            #MINI PROJECT FROM PYTHON SQL

        #SKILLS DEMONSTRATE

#API Integration & Pagination Handling  line :81

#JSON Parsing & ETL Pipeline Development line :91

#SQL Database Schema Design (3 linked tables) line : 115

#Data Transformation & Cleaning      line: 161

#Streamlit App Development (UI + Query execution) line: 220

 

        #PROJECT DELIVERABLES

#ETL Pipeline:

    #Collect ≥2500 artifacts per classification.  line:95

    #Save into 3 SQL tables (artifact_metadata, artifact_media, artifact_colors). line: 118,135,147

#Database:

    #Sqlite3 with the 3-table schema. 

    #Proper foreign key relationships.

#Streamlit App:

    #Dropdown to select classification. line :225

    #Buttons for:

        #Fetch Data from API  line: 235 (col1)

        #Display Data  (show) line : 242 (col 2)

        #Insert into SQL DB line: 161 using cursor line: 250 (col3)

    #Query Section with:

        #Predefined SQL queries (20)  line: 266

        #Self-framed SQL queries (5) line: 400

        #Result display as tables/charts line: 465


    #✅ Expected Outcomes ✅

#1.Database of 12,500+ artifacts (5 classifications × 2500 records). display all the 14 classification we can choose any 5.

#2.SQL tables automatically populated from API.

#3.20 SQL queries available inside the app.

#4.A working Streamlit dashboard for exploration & visualization.


import streamlit as st     #library used
import pandas as pd
import requests
import sqlite3

# ---------- REFERENCES ----------
API_KEY = "a7f03993-8a52-4cd3-b67c-4d564a493927"     ###Application programming interface key
CLASS_URL = "https://api.harvardartmuseums.org/classification"     #line:91
OBJECT_URL = "https://api.harvardartmuseums.org/object"   #line:100
DB_NAME = "harvard_artifacts.db"      #line:115

# ---------- API Functions ----------

def fetch_classifications(pages=7):
    records = []
    for i in range(1, pages + 1):
        res = requests.get(CLASS_URL, params={"apikey": API_KEY, "page": i}).json()
        records.extend(res.get("records", [])) 
    return pd.DataFrame(records)                    ### Json much easier to filter loop and insert data into SQL Database(most common format)


def fetch_objects_by_classification(classification, size=2500):
    records = []
    page = 1
    while len(records) < size:
        res = requests.get(OBJECT_URL, params={
            "apikey": API_KEY,
            "classification": classification,
            "size": 100,
            "page": page
        }).json()
        records.extend(res.get("records", []))
        if "next" not in res.get("info", {}):
            break
        page += 1
    return records[:size]


# ---------- Database Setup ----------
def init_db():              ### Initialize the database and create tables
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS artifact_metadata (
            id INTEGER PRIMARY KEY,
            title TEXT,
            culture TEXT,
            period TEXT,
            century TEXT,
            medium TEXT,
            dimensions TEXT,
            description TEXT,
            department TEXT,
            classification TEXT,
            accessionyear TEXT,
            accessionmethod TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS artifact_media (
            objectid INTEGER,
            imagecount INTEGER,
            mediacount INTEGER,
            colorcount INTEGER,
            rank INTEGER,
            datebegin INTEGER,
            dateend INTEGER
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS artifact_colors (
            objectid INTEGER,
            color TEXT,
            spectrum TEXT,
            hue TEXT,
            percent REAL,
            css3 TEXT
        )
    """)
    conn.commit()            ### to save changes permanently
    conn.close()             ### close the database connection and free up resources


def insert_records(records):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    for rec in records:         # ? is a placeholder and later be replaced with actual values
        cur.execute("""
            INSERT OR IGNORE INTO artifact_metadata
            (id, title, culture, period, century, medium, dimensions, description,
             department, classification, accessionyear, accessionmethod)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)  
        """, (
            rec.get("objectid"),
            rec.get("title"),
            rec.get("culture"),
            rec.get("period"),
            rec.get("century"),
            rec.get("medium"),
            rec.get("dimensions"),
            rec.get("description"),
            rec.get("department"),
            rec.get("classification"),
            rec.get("accessionyear"),
            rec.get("accessionmethod")
        ))

        cur.execute("""
            INSERT INTO artifact_media
            (objectid, imagecount, mediacount, colorcount, rank, datebegin, dateend)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            rec.get("objectid"),
            rec.get("imagecount", 0),
            rec.get("mediacount", 0),
            rec.get("colorcount", 0),
            rec.get("rank", 0),
            rec.get("datebegin"),
            rec.get("dateend")
        ))

        if rec.get("colors"):
            for color in rec["colors"]:
                cur.execute("""
                    INSERT INTO artifact_colors
                    (objectid, color, spectrum, hue, percent, css3)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    rec.get("objectid"),
                    color.get("color"),
                    color.get("spectrum"),
                    color.get("hue"),
                    color.get("percent"),
                    color.get("css3")
                ))

    conn.commit()
    conn.close()


# ---------- Streamlit App ----------
st.set_page_config(page_title="HARVARD ARTIFACTS PROJECT", layout="wide")
st.title("🏛️ HARVARD ARTIFACTS PROJECT")

init_db()

# Sidebar classification selection
st.sidebar.header("🎨 Select from Classifications")
df_classifications = fetch_classifications()
df_filtered = df_classifications[df_classifications['objectcount'] > 2500]
classification_list = sorted(df_filtered["name"].dropna().unique())      #dropna used for removing none values
selected_classification = st.sidebar.selectbox("Select a Classification", classification_list)

# Fetch and Show Data Buttons
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📥 Fetch Artifacts", key="fetch_btn"):
        with st.spinner("Fetching data from API..."):
            artifacts = fetch_objects_by_classification(selected_classification)
            st.session_state["fetched_data"] = artifacts
        st.success(f"Fetched {len(artifacts)} artifacts.")

with col2:
    if st.button("📊 Show Artifacts", key="show_btn"):
        if "fetched_data" in st.session_state:     #line 229
            df = pd.DataFrame(st.session_state["fetched_data"])
            st.dataframe(df[["objectid", "title", "culture", "period", "classification"]])
        else:
            st.warning("No data fetched yet. Please fetch artifacts first.")

with col3:
    if st.button("💾 Insert into Database", key="insert_btn"):
        if "fetched_data" in st.session_state:
            insert_records(st.session_state["fetched_data"])
            st.success("Data inserted into SQLite database.")
        else:
            st.warning("No data to insert. Fetch first.")


# ---------- SQL Query Section ----------
st.markdown("---")
st.header("🔎 SQL QUERIES")

# Main queries

queries = {
    # 🏺 artifact_metadata Table
    "1. Byzantine 11th century artifacts": """
        SELECT title, culture, century
        FROM artifact_metadata
        WHERE century = '11th century' AND culture = 'Byzantine';
    """,

    "2. Unique Cultures": """
        SELECT DISTINCT culture
        FROM artifact_metadata;
    """,

    "3. Artifacts from Archaic Period": """
        SELECT *
        FROM artifact_metadata
        WHERE period = 'Archaic';
    """,

    "4. Titles ordered by accession year (desc)": """
        SELECT title, accessionyear
        FROM artifact_metadata
        ORDER BY accessionyear DESC;
    """,

    "5. Artifacts per Department": """
        SELECT department, COUNT(*) as total
        FROM artifact_metadata
        GROUP BY department;
    """,

    # 🖼️ artifact_media Table
    "6. Artifacts with >1 image": """
        SELECT objectid, imagecount
        FROM artifact_media
        WHERE imagecount > 1;
    """,

    "7. Average rank of all artifacts": """
        SELECT AVG(rank) as avg_rank
        FROM artifact_media;
    """,

    "8. Artifacts with colorcount > mediacount": """
        SELECT objectid, colorcount, mediacount
        FROM artifact_media
        WHERE colorcount > mediacount;
    """,

    "9. Artifacts created between 1500 and 1600": """
        SELECT objectid, datebegin, dateend
        FROM artifact_media
        WHERE datebegin >= 1500 AND dateend <= 1600;
    """,

    "10. Artifacts with no media files": """
        SELECT COUNT(*) as no_media
        FROM artifact_media
        WHERE mediacount = 0;
    """,

    # 🎨 artifact_colors Table
    "11. Distinct hues": """
        SELECT DISTINCT hue
        FROM artifact_colors;
    """,

    "12. Top 5 most used colors": """
        SELECT color, COUNT(*) as freq
        FROM artifact_colors
        GROUP BY color
        ORDER BY freq DESC
        LIMIT 5;
    """,

    "13. Average coverage % per hue": """
        SELECT hue, AVG(percent) as avg_percent
        FROM artifact_colors
        GROUP BY hue;
    """,

    "14. Colors for a given artifact ID (e.g. 123456)": """
        SELECT *
        FROM artifact_colors
        WHERE objectid = 123456;
    """,

    "15. Total number of color entries": """
        SELECT COUNT(*) as total_colors
        FROM artifact_colors;
    """,

    # 🔗 Join-Based Queries
    "16. Byzantine artifacts with hues": """
        SELECT m.title, c.hue
        FROM artifact_metadata m
        JOIN artifact_colors c ON m.id = c.objectid
        WHERE m.culture = 'Byzantine';
    """,

    "17. Artifact titles with hues": """
        SELECT m.title, c.hue
        FROM artifact_metadata m
        JOIN artifact_colors c ON m.id = c.objectid;
    """,

    "18. Titles, cultures, media ranks where period not null": """
        SELECT m.title, m.culture, media.rank
        FROM artifact_metadata m
        JOIN artifact_media media ON m.id = media.objectid
        WHERE m.period IS NOT NULL;
    """,

    "19. Top 10 ranked artifacts that include Grey": """
        SELECT m.title, media.rank
        FROM artifact_metadata m
        JOIN artifact_media media ON m.id = media.objectid
        JOIN artifact_colors c ON m.id = c.objectid
        WHERE c.hue = 'Grey'
        ORDER BY media.rank ASC
        LIMIT 10;
    """,

    "20. Artifacts per classification and avg mediacount": """
        SELECT m.classification,
               COUNT(*) as total,
               AVG(media.mediacount) as avg_media
        FROM artifact_metadata m
        JOIN artifact_media media ON m.id = media.objectid
        GROUP BY m.classification;
    """
}


# Additional queries 
additional_queries = {
    "1.Most Common Culture per Period": """
        SELECT period, culture, COUNT(*) as freq
        FROM artifact_metadata
        WHERE culture IS NOT NULL AND period IS NOT NULL
        GROUP BY period, culture
        ORDER BY freq DESC;
    """,

    "2.Average Accession Year by Department": """
        SELECT department, ROUND(AVG(CAST(accessionyear AS INTEGER)), 0) as avg_accession_year
        FROM artifact_metadata
        WHERE accessionyear IS NOT NULL
        GROUP BY department;
    """,

    "3.Departments with the Largest Number of Artifacts": """
        SELECT department, COUNT(*) as artifact_count
        FROM artifact_metadata
        WHERE department IS NOT NULL
        GROUP BY department
        ORDER BY artifact_count DESC
        LIMIT 10;
    """,

    "4.Rare Mediums Used in Artifacts": """
        SELECT medium, COUNT(*) as usage_count
        FROM artifact_metadata
        WHERE medium IS NOT NULL AND medium != ''
        GROUP BY medium
        HAVING COUNT(*) = 1;
    """,

    "5.Culture with Longest Time Span of Artifacts": """
        SELECT m.culture,
               MIN(media.datebegin) as earliest,
               MAX(media.dateend) as latest,
               (MAX(media.dateend) - MIN(media.datebegin)) as time_span
        FROM artifact_metadata m
        JOIN artifact_media media ON m.id = media.objectid
        WHERE m.culture IS NOT NULL AND media.datebegin IS NOT NULL AND media.dateend IS NOT NULL
        GROUP BY m.culture
        ORDER BY time_span DESC
        LIMIT 1;
    """
}

# Run main queries
selected_query = st.selectbox("📌 Choose a Main Query", list(queries.keys()))
if st.button("▶️ Run Query", key="run_query_btn"):
    conn = sqlite3.connect(DB_NAME)
    df_query = pd.read_sql_query(queries[selected_query], conn)
    conn.close()
    st.dataframe(df_query)

# Run additional queries
st.title("🎯 Additional Queries")
selected_additional = st.selectbox("🔍 Choose an Additional Query", list(additional_queries.keys()))
if st.button("▶️ Run Additional Query", key="run_additional_query_btn"):
    conn = sqlite3.connect(DB_NAME)
    df_query = pd.read_sql_query(additional_queries[selected_additional], conn)
    conn.close()
    st.dataframe(df_query)

# View raw tables
st.markdown("---")
st.header("📂 View Database Tables")
tables = ["artifact_metadata", "artifact_media", "artifact_colors"]
selected_table = st.selectbox("Select a table to view", tables)

if st.button("📖 Show Table Data", key="show_table_btn"):
    conn = sqlite3.connect(DB_NAME)
    df_table = pd.read_sql_query(f"SELECT * FROM {selected_table} LIMIT 100;", conn)
    conn.close()
    st.write(f"Showing first {len(df_table)} rows from `{selected_table}`")
    st.dataframe(df_table)

# Footer
st.markdown("---")
st.info("This app uses the Harvard Art Museums API to explore artifact metadata and allows querying via SQL.")

st.info("The goal of this project is to analyze Harvard Artifacts data to extract cultural, historical, and visual insights using Python, SQLite, and Streamlit.")


### Conclusion : The Harvard Art Museums API provides a rich dataset for exploring and analyzing art artifacts. Through this Streamlit app, users can query and visualize various aspects of the data, gaining insights into cultural, historical, and artistic trends.
### Thank You!!!
### Sabira - (DS-S-WD-T-B79)