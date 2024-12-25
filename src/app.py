import streamlit as st
import pandas as pd
import google.generativeai as genai
from dotenv import load_dotenv
import os
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import psycopg2
from psycopg2.extras import Json
import json

# Load environment variables
load_dotenv()

# Color theme mapping
COLOR_THEMES = {
    "Viridis": px.colors.sequential.Viridis,
    "Plasma": px.colors.sequential.Plasma,
    "Inferno": px.colors.sequential.Inferno,
    "Magma": px.colors.sequential.Magma,
    "Cividis": px.colors.sequential.Cividis
}

# Database connection configuration
DB_CONFIG = {
    "host": "localhost",
    "database": "csv_analysis_db",
    "user": "osmanorka",
    "password": "Allah248012"
}

# Database helper functions
def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

def save_analysis(file_name, question, response, analysis_type="general"):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # First, get or create user
        cur.execute(
            "INSERT INTO users (username, email) VALUES (%s, %s) ON CONFLICT (username) DO UPDATE SET last_login = CURRENT_TIMESTAMP RETURNING user_id",
            ("default_user", "default@example.com")
        )
        user_id = cur.fetchone()[0]
        
        # Then, get or create file record
        cur.execute(
            """
            INSERT INTO uploaded_files (user_id, file_name, file_size, upload_date)
            VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
            ON CONFLICT (file_name) DO UPDATE SET upload_date = CURRENT_TIMESTAMP
            RETURNING file_id
            """,
            (user_id, file_name, 0)
        )
        file_id = cur.fetchone()[0]
        
        # Save the analysis
        cur.execute(
            """
            INSERT INTO ai_analyses (file_id, user_id, question, response, model_version, analysis_type)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING analysis_id
            """,
            (file_id, user_id, question, response, "gemini-pro", analysis_type)
        )
        
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Database error: {str(e)}")
        return False
    finally:
        if conn:
            conn.close()

def save_visualization(file_name, chart_type, chart_config):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Get or create user
        cur.execute(
            "INSERT INTO users (username, email) VALUES (%s, %s) ON CONFLICT (username) DO UPDATE SET last_login = CURRENT_TIMESTAMP RETURNING user_id",
            ("default_user", "default@example.com")
        )
        user_id = cur.fetchone()[0]
        
        # Get or create file record
        cur.execute(
            """
            INSERT INTO uploaded_files (user_id, file_name, file_size, upload_date)
            VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
            ON CONFLICT (file_name) DO UPDATE SET upload_date = CURRENT_TIMESTAMP
            RETURNING file_id
            """,
            (user_id, file_name, 0)
        )
        file_id = cur.fetchone()[0]
        
        # Save visualization
        cur.execute(
            """
            INSERT INTO visualizations (file_id, user_id, chart_type, chart_config)
            VALUES (%s, %s, %s, %s)
            RETURNING viz_id
            """,
            (file_id, user_id, chart_type, Json(chart_config))
        )
        
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Database error: {str(e)}")
        return False
    finally:
        if conn:
            conn.close()

def get_analysis_history():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute(
            """
            SELECT file_name, question, response, aa.created_at
            FROM ai_analyses aa
            JOIN uploaded_files uf ON aa.file_id = uf.file_id
            ORDER BY aa.created_at DESC
            LIMIT 50
            """
        )
        
        return cur.fetchall()
    except Exception as e:
        st.error(f"Database error: {str(e)}")
        return []
    finally:
        if conn:
            conn.close()

def get_visualization_history():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute(
            """
            SELECT file_name, chart_type, chart_config, v.created_at
            FROM visualizations v
            JOIN uploaded_files uf ON v.file_id = uf.file_id
            ORDER BY v.created_at DESC
            LIMIT 50
            """
        )
        
        return cur.fetchall()
    except Exception as e:
        st.error(f"Database error: {str(e)}")
        return []
    finally:
        if conn:
            conn.close()

# Add new database functions
def save_chat_history(file_name, role, content):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Get or create user and file records (similar to existing functions)
        cur.execute(
            "INSERT INTO users (username, email) VALUES (%s, %s) ON CONFLICT (username) DO UPDATE SET last_login = CURRENT_TIMESTAMP RETURNING user_id",
            ("default_user", "default@example.com")
        )
        user_id = cur.fetchone()[0]
        
        cur.execute(
            """
            INSERT INTO uploaded_files (user_id, file_name, file_size, upload_date)
            VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
            ON CONFLICT (file_name) DO UPDATE SET upload_date = CURRENT_TIMESTAMP
            RETURNING file_id
            """,
            (user_id, file_name, 0)
        )
        file_id = cur.fetchone()[0]
        
        # Save chat message
        cur.execute(
            """
            INSERT INTO chat_history (user_id, file_id, role, content)
            VALUES (%s, %s, %s, %s)
            RETURNING chat_id
            """,
            (user_id, file_id, role, content)
        )
        
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Database error: {str(e)}")
        return False
    finally:
        if conn:
            conn.close()

def save_statistical_summary(file_name, column_stats):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Get or create user and file records
        cur.execute(
            "INSERT INTO users (username, email) VALUES (%s, %s) ON CONFLICT (username) DO UPDATE SET last_login = CURRENT_TIMESTAMP RETURNING user_id",
            ("default_user", "default@example.com")
        )
        user_id = cur.fetchone()[0]
        
        cur.execute(
            """
            INSERT INTO uploaded_files (user_id, file_name, file_size, upload_date)
            VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
            ON CONFLICT (file_name) DO UPDATE SET upload_date = CURRENT_TIMESTAMP
            RETURNING file_id
            """,
            (user_id, file_name, 0)
        )
        file_id = cur.fetchone()[0]
        
        # Save statistical summaries
        for col_name, stats in column_stats.items():
            cur.execute(
                """
                INSERT INTO statistical_summaries 
                (file_id, column_name, data_type, null_count, unique_count, 
                mean, median, std_dev, min_value, max_value, summary_json)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (file_id, col_name, stats['data_type'], stats['null_count'],
                 stats['unique_count'], stats.get('mean'), stats.get('median'),
                 stats.get('std_dev'), str(stats.get('min')), str(stats.get('max')),
                 Json(stats))
            )
        
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Database error: {str(e)}")
        return False
    finally:
        if conn:
            conn.close()

def get_file_history():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute(
            """
            SELECT DISTINCT ON (uf.file_id)
                uf.file_id,
                uf.file_name,
                uf.upload_date,
                (SELECT COUNT(*) FROM visualizations v WHERE v.file_id = uf.file_id) as viz_count,
                (SELECT COUNT(*) FROM ai_analyses aa WHERE aa.file_id = uf.file_id) as analysis_count,
                (SELECT COUNT(*) FROM chat_history ch WHERE ch.file_id = uf.file_id) as chat_count,
                (SELECT COUNT(*) FROM statistical_summaries ss WHERE ss.file_id = uf.file_id) as stats_count
            FROM uploaded_files uf
            ORDER BY uf.file_id, uf.upload_date DESC
            """
        )
        
        return cur.fetchall()
    except Exception as e:
        st.error(f"Database error: {str(e)}")
        return []
    finally:
        if conn:
            conn.close()

def get_file_details(file_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Get visualizations
        cur.execute(
            """
            SELECT chart_type, chart_config, created_at
            FROM visualizations
            WHERE file_id = %s
            ORDER BY created_at DESC
            """,
            (file_id,)
        )
        visualizations = cur.fetchall()
        
        # Get analyses
        cur.execute(
            """
            SELECT question, response, created_at
            FROM ai_analyses
            WHERE file_id = %s
            ORDER BY created_at DESC
            """,
            (file_id,)
        )
        analyses = cur.fetchall()
        
        # Get chat history
        cur.execute(
            """
            SELECT role, content, created_at
            FROM chat_history
            WHERE file_id = %s
            ORDER BY created_at
            """,
            (file_id,)
        )
        chat_history = cur.fetchall()
        
        # Get statistical summaries
        cur.execute(
            """
            SELECT column_name, summary_json, created_at
            FROM statistical_summaries
            WHERE file_id = %s
            ORDER BY created_at DESC
            """,
            (file_id,)
        )
        stats = cur.fetchall()
        
        return {
            'visualizations': visualizations,
            'analyses': analyses,
            'chat_history': chat_history,
            'statistics': stats
        }
    except Exception as e:
        st.error(f"Database error: {str(e)}")
        return None
    finally:
        if conn:
            conn.close()

# Configure Google Gemini API
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))

# Set page config with dark theme
st.set_page_config(
    page_title="CSV Data Analysis Assistant",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for dark theme and modern design with better contrast
st.markdown("""
    <style>
        /* Main app background and text */
        .stApp {
            background-color: #1a1a1a;
            color: #ffffff;
        }
        
        /* Sidebar styling */
        .css-1d391kg {
            background-color: #2d2d2d;
        }
        
        /* Buttons */
        .stButton>button {
            background-color: #FF6B6B;
            color: white;
            border-radius: 8px;
            border: none;
            padding: 10px 24px;
            transition: all 0.3s ease;
            font-weight: bold;
        }
        .stButton>button:hover {
            background-color: #FF8787;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(255, 107, 107, 0.3);
        }
        
        /* Input fields */
        .stTextInput>div>div>input, .stSelectbox>div>div>input {
            background-color: #3d3d3d;
            color: #ffffff;
            border: 1px solid #FF6B6B;
        }
        
        /* Dataframe styling */
        .dataframe {
            background-color: #2d2d2d !important;
            color: #ffffff !important;
        }
        
        /* Metric cards */
        .css-1xarl3l {
            background-color: #2d2d2d;
            border: 1px solid #FF6B6B;
            padding: 20px;
            border-radius: 10px;
        }
        
        /* Tabs styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
        .stTabs [data-baseweb="tab"] {
            background-color: #2d2d2d;
            color: #ffffff;
            border-radius: 4px 4px 0 0;
            padding: 10px 20px;
            border: 1px solid #FF6B6B;
        }
        .stTabs [aria-selected="true"] {
            background-color: #FF6B6B;
        }
        
        /* Chat messages */
        .stChatMessage {
            background-color: #2d2d2d;
            border-radius: 15px;
            padding: 15px;
            margin: 10px 0;
        }
        
        /* Headers */
        h1, h2, h3 {
            color: #FF6B6B !important;
        }
        
        /* Custom card container */
        .custom-card {
            background-color: #2d2d2d;
            border: 1px solid #FF6B6B;
            border-radius: 10px;
            padding: 20px;
            margin: 10px 0;
        }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'analysis_history' not in st.session_state:
    st.session_state.analysis_history = []
if 'favorite_visualizations' not in st.session_state:
    st.session_state.favorite_visualizations = []

# Sidebar
with st.sidebar:
    st.image("https://raw.githubusercontent.com/streamlit/streamlit/develop/lib/streamlit/static/favicon.png", width=100)
    st.title("Data Analysis Tools")
    
    # Create tabs in sidebar with professional icons
    sidebar_tab1, sidebar_tab2 = st.tabs([
        "⬆️ Upload",  # upload icon
        "📁 Files"    # folder icon
    ])
    
    with sidebar_tab1:
        uploaded_file = st.file_uploader("Select CSV File", type=['csv'])
        
        if uploaded_file is not None:
            st.success("File uploaded successfully")
            
            st.subheader("Visualization Settings")
            chart_type = st.selectbox(
                "Chart Type",
                ["Histogram", "Box Plot", "Scatter Plot", "Bar Chart", "Line Chart", "Violin Plot"]
            )
            
            color_theme = st.selectbox(
                "Color Theme",
                ["Viridis", "Plasma", "Inferno", "Magma", "Cividis"]
            )
            
            with st.expander("Settings"):
                show_grid = st.checkbox("Show Grid", value=True)
                enable_animations = st.checkbox("Enable Animations", value=True)
    
    with sidebar_tab2:
        st.subheader("Analysis History")
        
        # Get and display file history with better styling
        file_history = get_file_history()
        for file in file_history:
            st.markdown(f"""
                <div style='background-color: #2D2D2D; padding: 12px; border-radius: 4px; margin: 8px 0;'>
                    <h4 style='color: #FF6B6B; margin: 0;'>{file[1]}</h4>
                    <p style='color: #CCCCCC; font-size: 12px; margin: 4px 0;'>{file[2].strftime('%Y-%m-%d %H:%M')}</p>
                    <div style='display: flex; justify-content: space-between; color: #FFFFFF; margin-top: 8px;'>
                        <span title="Visualizations"><i class="fa-regular fa-chart-bar"></i> {file[3]}</span>
                        <span title="Analyses"><i class="fa-solid fa-chart-column"></i> {file[4]}</span>
                        <span title="Chat History"><i class="fa-regular fa-comments"></i> {file[5]}</span>
                        <span title="Statistics"><i class="fa-solid fa-chart-line"></i> {file[6]}</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"View Details", key=f"view_{file[0]}"):
                details = get_file_details(file[0])
                if details:
                    # Create tabs for different types of history with updated icons
                    hist_tab1, hist_tab2, hist_tab3, hist_tab4 = st.tabs([
                        '<i class="fa-regular fa-chart-bar"></i> Visualizations',
                        '<i class="fa-solid fa-chart-column"></i> Analyses',
                        '<i class="fa-regular fa-comments"></i> Chat',
                        '<i class="fa-solid fa-chart-line"></i> Statistics'
                    ])
                    
                    with hist_tab1:
                        for viz in details['visualizations']:
                            st.markdown(f"""
                                <div style='background-color: #2D2D2D; padding: 16px; border-radius: 4px; margin: 8px 0;'>
                                    <h4 style='color: #FF6B6B; margin: 0;'>Chart - {viz[2]}</h4>
                                    <p style='color: #FFFFFF; margin: 8px 0;'>Type: {viz[0]}</p>
                                    <pre style='background-color: #1E1E1E; padding: 12px; border-radius: 4px; color: #CCCCCC;'>{json.dumps(viz[1], indent=2)}</pre>
                                </div>
                            """, unsafe_allow_html=True)
                    
                    with hist_tab2:
                        for analysis in details['analyses']:
                            st.markdown(f"""
                                <div style='background-color: #2D2D2D; padding: 16px; border-radius: 4px; margin: 8px 0;'>
                                    <h4 style='color: #FF6B6B; margin: 0;'>Analysis - {analysis[2]}</h4>
                                    <p style='color: #FFFFFF; margin: 8px 0;'><strong>Question:</strong> {analysis[0]}</p>
                                    <p style='color: #CCCCCC;'>{analysis[1]}</p>
                                </div>
                            """, unsafe_allow_html=True)
                    
                    with hist_tab3:
                        for chat in details['chat_history']:
                            with st.chat_message(chat[0]):
                                st.markdown(f"""
                                    <div style='color: #FFFFFF;'>
                                        <p style='margin: 0;'>{chat[1]}</p>
                                        <small style='color: #CCCCCC;'>{chat[2]}</small>
                                    </div>
                                """, unsafe_allow_html=True)
                    
                    with hist_tab4:
                        for stat in details['statistics']:
                            st.markdown(f"""
                                <div style='background-color: #2D2D2D; padding: 16px; border-radius: 4px; margin: 8px 0;'>
                                    <h4 style='color: #FF6B6B; margin: 0;'>{stat[0]} - {stat[2]}</h4>
                                    <pre style='background-color: #1E1E1E; padding: 12px; border-radius: 4px; color: #CCCCCC;'>{json.dumps(stat[1], indent=2)}</pre>
                                </div>
                            """, unsafe_allow_html=True)

# Add Font Awesome to the page
st.markdown("""
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
    <style>
        .fa-solid, .fa-regular, .fa-light, .fa-brands {
            margin-right: 5px;
            font-size: 14px;
        }
        /* Main app styling */
        .stApp {
            background-color: #1a1a1a;
            color: #ffffff;
        }
        /* Sidebar styling */
        .css-1d391kg {
            background-color: #2d2d2d;
        }
        /* Buttons */
        .stButton>button {
            background-color: #FF6B6B;
            color: white;
            border-radius: 4px;
            border: none;
            padding: 8px 16px;
            transition: all 0.2s ease;
        }
        .stButton>button:hover {
            background-color: #FF8787;
            transform: translateY(-1px);
        }
        /* Input fields */
        .stTextInput>div>div>input {
            background-color: #3d3d3d;
            color: #ffffff;
            border: 1px solid #4d4d4d;
        }
        /* Tabs styling */
        .stTabs [data-baseweb="tab"] {
            background-color: #2d2d2d;
            color: #ffffff;
            border-radius: 4px;
            padding: 8px 16px;
        }
        .stTabs [data-baseweb="tab"][aria-selected="true"] {
            background-color: #FF6B6B;
        }
    </style>
""", unsafe_allow_html=True)

# Main content area with fixed tabs
st.markdown("""
    <style>
        /* Tab container */
        .main-nav {
            background-color: #2D2D2D;
            padding: 10px;
            border-radius: 8px;
            margin-bottom: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        /* Individual tab buttons */
        .nav-button {
            background-color: transparent;
            color: #CCCCCC;
            border: none;
            padding: 10px 20px;
            border-radius: 4px;
            cursor: pointer;
            transition: all 0.3s ease;
            font-size: 14px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .nav-button:hover {
            background-color: #3D3D3D;
            color: #FFFFFF;
        }
        
        .nav-button.active {
            background-color: #FF6B6B;
            color: #FFFFFF;
        }
        
        /* Icon styling */
        .nav-button i {
            font-size: 16px;
        }
    </style>
""", unsafe_allow_html=True)

# Create navigation container
if 'current_tab' not in st.session_state:
    st.session_state.current_tab = 'data_preview'

# Navigation buttons
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    if st.button('📊 Data Preview', key='btn_preview', use_container_width=True):
        st.session_state.current_tab = 'data_preview'
with col2:
    if st.button('📈 Statistics', key='btn_stats', use_container_width=True):
        st.session_state.current_tab = 'statistics'
with col3:
    if st.button('📊 Visualization', key='btn_viz', use_container_width=True):
        st.session_state.current_tab = 'visualization'
with col4:
    if st.button('💬 AI Chat', key='btn_chat', use_container_width=True):
        st.session_state.current_tab = 'chat'
with col5:
    if st.button('📋 History', key='btn_history', use_container_width=True):
        st.session_state.current_tab = 'history'

# Add separator
st.markdown("<hr style='margin: 20px 0; border-color: #3D3D3D;'>", unsafe_allow_html=True)

# Content based on selected tab
if uploaded_file is not None:
    try:
        # Load data
        try:
            df = pd.read_csv(uploaded_file, encoding='utf-8')
        except UnicodeDecodeError:
            try:
                df = pd.read_csv(uploaded_file, encoding='latin1')
            except:
                df = pd.read_csv(uploaded_file, encoding='cp1252')
        
        # Display content based on selected tab
        if st.session_state.current_tab == 'data_preview':
            st.header("📊 Data Preview")
            st.dataframe(df.head(10), use_container_width=True)
            
            st.subheader("📑 Column Information")
            col_info = pd.DataFrame({
                'Data Type': df.dtypes.astype(str),
                'Non-Null Count': df.count(),
                'Null Count': df.isnull().sum(),
                'Unique Values': df.nunique()
            })
            st.dataframe(col_info, use_container_width=True)
            
        elif st.session_state.current_tab == 'statistics':
            st.header("📈 Statistical Analysis")
            
            # Numeric statistics
            numeric_df = df.select_dtypes(include=[np.number])
            if not numeric_df.empty:
                st.subheader("Numeric Data Statistics")
                stats_df = numeric_df.describe()
                stats_df.loc['skew'] = numeric_df.skew()
                stats_df.loc['kurtosis'] = numeric_df.kurtosis()
                st.dataframe(stats_df, use_container_width=True)
                
                # Correlation matrix
                st.subheader("Correlation Matrix")
                corr = numeric_df.corr()
                fig = px.imshow(
                    corr,
                    color_continuous_scale=COLOR_THEMES[color_theme],
                    aspect='auto'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Categorical statistics
            categorical_df = df.select_dtypes(exclude=[np.number])
            if not categorical_df.empty:
                st.subheader("Categorical Data Summary")
                for col in categorical_df.columns:
                    with st.expander(f"{col} Distribution"):
                        value_counts = categorical_df[col].value_counts()
                        fig = px.bar(
                            x=value_counts.index,
                            y=value_counts.values,
                            title=f"{col} Distribution",
                            color_discrete_sequence=COLOR_THEMES[color_theme]
                        )
                        st.plotly_chart(fig, use_container_width=True)
            
            # Save statistics
            if st.button("Save Statistical Analysis"):
                column_stats = {}
                for col in df.columns:
                    stats = {
                        'data_type': str(df[col].dtype),
                        'null_count': int(df[col].isnull().sum()),
                        'unique_count': int(df[col].nunique())
                    }
                    if np.issubdtype(df[col].dtype, np.number):
                        stats.update({
                            'mean': float(df[col].mean()) if not pd.isna(df[col].mean()) else None,
                            'median': float(df[col].median()) if not pd.isna(df[col].median()) else None,
                            'std_dev': float(df[col].std()) if not pd.isna(df[col].std()) else None,
                            'min': float(df[col].min()) if not pd.isna(df[col].min()) else None,
                            'max': float(df[col].max()) if not pd.isna(df[col].max()) else None
                        })
                    column_stats[col] = stats
                
                if save_statistical_summary(uploaded_file.name, column_stats):
                    st.success("Statistical analysis saved successfully!")
            
        elif st.session_state.current_tab == 'visualization':
            st.header("📊 Data Visualization")
            
            # Column selection
            col1, col2 = st.columns(2)
            with col1:
                x_col = st.selectbox("Select X-axis column", df.columns)
            with col2:
                y_col = st.selectbox("Select Y-axis column (optional)", ["None"] + list(df.columns))
            
            # Create visualization
            try:
                fig = None
                if chart_type == "Histogram":
                    fig = px.histogram(df, x=x_col, color_discrete_sequence=COLOR_THEMES[color_theme])
                elif chart_type == "Box Plot":
                    fig = px.box(df, y=x_col, color_discrete_sequence=COLOR_THEMES[color_theme])
                elif chart_type == "Scatter Plot" and y_col != "None":
                    fig = px.scatter(df, x=x_col, y=y_col, color_discrete_sequence=COLOR_THEMES[color_theme])
                elif chart_type == "Bar Chart":
                    if df[x_col].dtype == 'object':
                        value_counts = df[x_col].value_counts()
                        fig = px.bar(x=value_counts.index, y=value_counts.values,
                                   color_discrete_sequence=COLOR_THEMES[color_theme])
                    else:
                        fig = px.bar(df, x=x_col, color_discrete_sequence=COLOR_THEMES[color_theme])
                elif chart_type == "Line Chart" and y_col != "None":
                    fig = px.line(df, x=x_col, y=y_col, color_discrete_sequence=COLOR_THEMES[color_theme])
                elif chart_type == "Violin Plot":
                    fig = px.violin(df, y=x_col, color_discrete_sequence=COLOR_THEMES[color_theme])
                
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Save visualization
                    if st.button("Save Visualization"):
                        chart_config = {
                            'type': chart_type,
                            'x_col': x_col,
                            'y_col': y_col if y_col != "None" else None,
                            'color_theme': color_theme
                        }
                        if save_visualization(uploaded_file.name, chart_type, chart_config):
                            st.success("Visualization saved successfully!")
            
            except Exception as e:
                st.error(f"Error creating visualization: {str(e)}")
            
        elif st.session_state.current_tab == 'chat':
            st.header("💬 AI Chat")
            
            # Display chat history
            for message in st.session_state.chat_history:
                with st.chat_message(message["role"]):
                    st.write(message["content"])
            
            # Chat input
            user_question = st.chat_input("Ask a question about your data...")
            
            if user_question:
                # Add user message to chat
                st.session_state.chat_history.append({"role": "user", "content": user_question})
                
                # Generate AI response
                try:
                    model = genai.GenerativeModel('gemini-pro')
                    prompt = f"""Analyze this dataset and answer: {user_question}
                    
                    Dataset info:
                    - Columns: {', '.join(df.columns)}
                    - Shape: {df.shape}
                    - Data types: {df.dtypes.to_string()}
                    """
                    
                    response = model.generate_content(prompt)
                    
                    # Save chat history
                    save_chat_history(uploaded_file.name, "user", user_question)
                    save_chat_history(uploaded_file.name, "assistant", response.text)
                    
                    # Display response
                    st.session_state.chat_history.append({"role": "assistant", "content": response.text})
                    with st.chat_message("assistant"):
                        st.write(response.text)
                
                except Exception as e:
                    st.error(f"Error generating response: {str(e)}")
            
        elif st.session_state.current_tab == 'history':
            st.header("📋 Analysis History")
            
            # Get history data
            viz_history = get_visualization_history()
            analysis_history = get_analysis_history()
            file_history = get_file_history()
            
            # Display history in tabs
            hist_tab1, hist_tab2, hist_tab3 = st.tabs(["Visualizations", "Analyses", "Files"])
            
            with hist_tab1:
                if viz_history:
                    for viz in viz_history:
                        with st.expander(f"{viz[0]} - {viz[3].strftime('%Y-%m-%d %H:%M')}"):
                            st.write(f"Chart Type: {viz[1]}")
                            st.json(viz[2])
                else:
                    st.info("No visualization history found")
            
            with hist_tab2:
                if analysis_history:
                    for analysis in analysis_history:
                        with st.expander(f"{analysis[0]} - {analysis[3].strftime('%Y-%m-%d %H:%M')}"):
                            st.write("Question:", analysis[1])
                            st.write("Response:", analysis[2])
                else:
                    st.info("No analysis history found")
            
            with hist_tab3:
                if file_history:
                    for file in file_history:
                        with st.expander(f"{file[1]} - {file[2].strftime('%Y-%m-%d %H:%M')}"):
                            st.write(f"Visualizations: {file[3]}")
                            st.write(f"Analyses: {file[4]}")
                            st.write(f"Chat Messages: {file[5]}")
                            st.write(f"Statistics: {file[6]}")
                else:
                    st.info("No file history found")

    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
else:
    # Welcome screen
    st.markdown("""
        <div style='text-align: center; padding: 50px;'>
            <h1 style='color: #FF6B6B;'>Welcome to CSV Data Analysis Assistant</h1>
            <p style='font-size: 20px; color: #ffffff;'>Upload a CSV file to begin your data analysis journey!</p>
            <div style='background-color: #2d2d2d; padding: 30px; border-radius: 15px; margin: 20px 0;'>
                <h3 style='color: #FF6B6B;'>Features:</h3>
                <ul style='list-style-type: none; color: #ffffff;'>
                    <li><i class="fa-regular fa-chart-bar"></i> Interactive data visualizations</li>
                    <li><i class="fa-solid fa-chart-column"></i> Comprehensive statistical analysis</li>
                    <li><i class="fa-solid fa-robot"></i> AI-powered insights</li>
                    <li><i class="fa-regular fa-comments"></i> Chat with an AI analyst</li>
                    <li><i class="fa-solid fa-clock-rotate-left"></i> Save and track your analysis history</li>
                </ul>
            </div>
        </div>
    """, unsafe_allow_html=True)

# Update button styles
st.markdown("""
    <style>
        /* Button styling */
        .stButton > button {
            width: 100%;
            background-color: #2D2D2D;
            color: #CCCCCC;
            border: 1px solid #3D3D3D;
            padding: 10px 20px;
            border-radius: 4px;
            font-weight: normal;
            transition: all 0.3s ease;
        }
        
        .stButton > button:hover {
            background-color: #3D3D3D;
            color: #FFFFFF;
            border-color: #FF6B6B;
        }
        
        .stButton > button:active {
            background-color: #FF6B6B;
            color: #FFFFFF;
            border-color: #FF6B6B;
        }
        
        /* Active tab styling */
        .stButton > button[data-active="true"] {
            background-color: #FF6B6B;
            color: #FFFFFF;
            border-color: #FF6B6B;
        }
    </style>
""", unsafe_allow_html=True) 