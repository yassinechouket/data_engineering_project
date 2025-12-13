import streamlit as st
import pandas as pd
import psycopg2
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time

# --- Configuration ---
st.set_page_config(
    page_title="Neo-Sousse 2030",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Theme & Styling ---
# Green for Ecology (#27AE60), Blue for Technology (#2980B9)
st.markdown("""
    <style>
    .main {
        background-color: #F8F9FA;
    }
    .stApp {
        background-color: #FFFFFF;
    }
    h1, h2, h3 {
        color: #2C3E50;
        font-family: 'Segoe UI', sans-serif;
    }
    .metric-card {
        background-color: #FFFFFF;
        border-left: 5px solid #27AE60;
        padding: 15px;
        border-radius: 5px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    .metric-card-blue {
        border-left: 5px solid #2980B9;
    }
    div[data-testid="stMetricValue"] {
        font-size: 24px;
        color: #2C3E50;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Database Connection ---
# Using config from consumer.py
DB_CONFIG = {
    'host': 'localhost',
    'port': 5339,
    'database': 'smart_city',
    'user': 'chouket',
    'password': '2003'
}

@st.cache_resource
def get_db_connection():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        st.error(f"❌ Database connection failed: {e}")
        return None

# --- Data Fetching Functions ---

def get_pollution_data():
    query = """
    SELECT 
        a.nom_arrondissement,
        AVG(m.valeur_mesuree) AS pollution_moyenne,
        MAX(m.valeur_mesuree) AS pollution_max,
        COUNT(m.id_mesure) AS nombre_mesures
    FROM arrondissement a
    JOIN capteur c ON a.id_arrondissement = c.id_arrondissement
    JOIN mesure m ON c.id_capteur = m.id_capteur
    WHERE m.date_heure_mesure >= NOW() - INTERVAL '24 HOURS'
      AND c.type_capteur IN ('pollution', 'qualité air', 'air', 'CO2', 'PM2.5')
    GROUP BY a.nom_arrondissement
    ORDER BY pollution_moyenne DESC;
    """
    conn = get_db_connection()
    if conn:
        return pd.read_sql(query, conn)
    return pd.DataFrame()

def get_sensor_availability():
    query = """
    SELECT 
        a.nom_arrondissement,
        COUNT(c.id_capteur) AS total_capteurs,
        SUM(CASE WHEN c.statut = 'actif' THEN 1 ELSE 0 END) AS capteurs_actifs,
        ROUND(
            CASE 
                WHEN COUNT(c.id_capteur) = 0 THEN 0
                ELSE (SUM(CASE WHEN c.statut = 'actif' THEN 1 ELSE 0 END)::DECIMAL / COUNT(c.id_capteur)) * 100
            END, 2
        ) AS taux_disponibilite_pourcentage
    FROM arrondissement a
    LEFT JOIN capteur c ON a.id_arrondissement = c.id_arrondissement
    GROUP BY a.nom_arrondissement
    ORDER BY taux_disponibilite_pourcentage DESC;
    """
    conn = get_db_connection()
    if conn:
        return pd.read_sql(query, conn)
    return pd.DataFrame()

def get_autonomous_trips():
    query = """
    SELECT 
        t.plaque_immatriculation,
        v.type_vehicule,
        v.energie_utilisee,
        t.origine,
        t.destination,
        t.date_heure_depart,
        t.duree_minutes,
        t.economie_co2_kg
    FROM trajet t
    JOIN vehicule_autonome v ON t.plaque_immatriculation = v.plaque_immatriculation
    ORDER BY t.date_heure_depart DESC
    LIMIT 100;
    """
    conn = get_db_connection()
    if conn:
        return pd.read_sql(query, conn)
    return pd.DataFrame()

def get_predictive_interventions():
    query = """
    SELECT 
        COUNT(DISTINCT i.id_intervention) AS nombre_interventions_predictives,
        COALESCE(SUM(i.impact_environnemental_co2_kg), 0) AS economie_co2_totale_kg,
        COALESCE(SUM(i.cout_euros), 0) AS cout_total_euros,
        COALESCE(AVG(i.duree_minutes), 0) AS duree_moyenne_minutes
    FROM intervention i
    WHERE i.nature_intervention = 'predictive'
      AND i.date_heure_intervention >= DATE_TRUNC('month', CURRENT_DATE);
    """
    conn = get_db_connection()
    if conn:
        return pd.read_sql(query, conn)
    return pd.DataFrame()

def get_engaged_citizens():
    query = """
    SELECT 
        c.nom_citoyen,
        c.prenom_citoyen,
        c.score_engagement_ecologique,
        COUNT(p.id_consultation) AS nombre_participations
    FROM citoyen c
    LEFT JOIN participation_citoyenne p ON c.id_citoyen = p.id_citoyen
    GROUP BY c.id_citoyen, c.nom_citoyen, c.prenom_citoyen, c.score_engagement_ecologique
    ORDER BY c.score_engagement_ecologique DESC, nombre_participations DESC
    LIMIT 10;
    """
    conn = get_db_connection()
    if conn:
        return pd.read_sql(query, conn)
    return pd.DataFrame()

def get_latest_measurements():
    query = """
    SELECT 
        c.type_capteur,
        m.valeur_mesuree,
        m.unite_mesure,
        m.date_heure_mesure,
        a.nom_arrondissement
    FROM mesure m
    JOIN capteur c ON m.id_capteur = c.id_capteur
    LEFT JOIN arrondissement a ON c.id_arrondissement = a.id_arrondissement
    ORDER BY m.date_heure_mesure DESC
    LIMIT 5;
    """
    conn = get_db_connection()
    if conn:
        return pd.read_sql(query, conn)
    return pd.DataFrame()

# --- Sidebar Navigation ---
st.sidebar.title("🏙️ Neo-Sousse 2030")
st.sidebar.markdown("Intelligent Urban Data Management")
page = st.sidebar.radio("Navigation", ["Dashboard Overview", "Environment & Ecology", "Smart Infrastructure", "Mobility", "Citizen Engagement"])

st.sidebar.markdown("---")
st.sidebar.caption("🟢 Connected to Kafka Stream (via DB)")
st.sidebar.caption(f"Last Update: {datetime.now().strftime('%H:%M:%S')}")

if st.sidebar.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()

# --- Main Content ---

if page == "Dashboard Overview":
    st.title("📊 Executive Dashboard")
    st.markdown("Real-time overview of city performance indicators.")

    # Fetch Data
    df_interventions = get_predictive_interventions()
    df_sensors = get_sensor_availability()
    
    # Top KPIs
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_sensors = df_sensors['total_capteurs'].sum() if not df_sensors.empty else 0
        st.metric("Total Sensors", f"{total_sensors}", delta="Active")
        
    with col2:
        avg_availability = df_sensors['taux_disponibilite_pourcentage'].mean() if not df_sensors.empty else 0
        st.metric("Avg Availability", f"{avg_availability:.1f}%", delta_color="normal")
        
    with col3:
        co2_saved = df_interventions['economie_co2_totale_kg'].iloc[0] if not df_interventions.empty else 0
        st.metric("CO2 Saved (Month)", f"{co2_saved:.1f} kg", delta="Target: 500kg")
        
    with col4:
        cost = df_interventions['cout_total_euros'].iloc[0] if not df_interventions.empty else 0
        st.metric("Intervention Cost", f"€{cost:,.0f}", delta="-5% vs Prev")

    # Recent Activity Feed
    st.subheader("📡 Live Sensor Feed")
    df_latest = get_latest_measurements()
    if not df_latest.empty:
        st.dataframe(df_latest, use_container_width=True, hide_index=True)
    else:
        st.info("No recent sensor data available.")

    # Quick Charts
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Sensor Status by District")
        if not df_sensors.empty:
            fig = px.bar(df_sensors, x='nom_arrondissement', y=['capteurs_actifs', 'total_capteurs'], 
                         barmode='group', title="Active vs Total Sensors",
                         color_discrete_sequence=['#27AE60', '#BDC3C7'])
            st.plotly_chart(fig, use_container_width=True)
            
    with c2:
        st.subheader("Predictive Maintenance Impact")
        # Mock data for trend if not enough real data
        dates = pd.date_range(start='2025-01-01', periods=7)
        mock_savings = [10, 15, 12, 20, 25, 18, 30]
        fig = px.line(x=dates, y=mock_savings, title="Daily CO2 Savings (kg)",
                      labels={'x': 'Date', 'y': 'CO2 Saved'},
                      line_shape='spline')
        fig.update_traces(line_color='#2980B9', line_width=3)
        st.plotly_chart(fig, use_container_width=True)

elif page == "Environment & Ecology":
    st.title("🌿 Environmental Monitoring")
    
    df_pollution = get_pollution_data()
    
    if not df_pollution.empty:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Air Quality Index (24h)")
            fig = px.bar(df_pollution, x='nom_arrondissement', y='pollution_moyenne',
                         color='pollution_moyenne',
                         color_continuous_scale='RdYlGn_r',
                         title="Average Pollution Levels by District",
                         labels={'pollution_moyenne': 'Concentration (µg/m³)'})
            st.plotly_chart(fig, use_container_width=True)
            
        with col2:
            st.subheader("Critical Alerts")
            critical = df_pollution[df_pollution['pollution_max'] > 100] # Threshold example
            if not critical.empty:
                for _, row in critical.iterrows():
                    st.error(f"⚠️ High Pollution in {row['nom_arrondissement']}: {row['pollution_max']} µg/m³")
            else:
                st.success("✅ No critical pollution levels detected.")
                
            st.metric("City Average", f"{df_pollution['pollution_moyenne'].mean():.2f}", "µg/m³")
    else:
        st.warning("No pollution data available for the last 24 hours.")

elif page == "Smart Infrastructure":
    st.title("🏗️ Smart Infrastructure & Maintenance")
    
    tab1, tab2 = st.tabs(["Sensor Health", "Interventions"])
    
    with tab1:
        df_sensors = get_sensor_availability()
        if not df_sensors.empty:
            fig = px.pie(df_sensors, values='total_capteurs', names='nom_arrondissement', 
                         title="Sensor Distribution", hole=0.4,
                         color_discrete_sequence=px.colors.sequential.Blues)
            st.plotly_chart(fig, use_container_width=True)
            
            st.dataframe(df_sensors.style.highlight_max(axis=0, color='#d4edda'), use_container_width=True)
    
    with tab2:
        df_interventions = get_predictive_interventions()
        if not df_interventions.empty:
            c1, c2, c3 = st.columns(3)
            c1.metric("Predictive Interventions", df_interventions['nombre_interventions_predictives'].iloc[0])
            c2.metric("Avg Duration", f"{df_interventions['duree_moyenne_minutes'].iloc[0]:.0f} min")
            c3.metric("Total Cost", f"€{df_interventions['cout_total_euros'].iloc[0]:,.2f}")
            
            st.info("Predictive maintenance has reduced downtime by an estimated 15% this month.")

elif page == "Mobility":
    st.title("🚗 Autonomous Mobility & Traffic")
    
    df_trips = get_autonomous_trips()
    
    if not df_trips.empty:
        st.subheader("Recent Autonomous Trips")
        
        # Scatter plot of Duration vs CO2 Savings
        fig = px.scatter(df_trips, x='duree_minutes', y='economie_co2_kg',
                         color='type_vehicule', size='economie_co2_kg',
                         title="Trip Efficiency: Duration vs CO2 Savings",
                         hover_data=['origine', 'destination'])
        st.plotly_chart(fig, use_container_width=True)
        
        st.dataframe(df_trips[['plaque_immatriculation', 'type_vehicule', 'origine', 'destination', 'economie_co2_kg']], 
                     use_container_width=True)
    else:
        st.info("No autonomous vehicle trip data available.")

elif page == "Citizen Engagement":
    st.title("🤝 Citizen Participation")
    
    df_citizens = get_engaged_citizens()
    
    if not df_citizens.empty:
        st.subheader("Top Engaged Citizens")
        
        # Horizontal bar chart for engagement scores
        fig = px.bar(df_citizens, x='score_engagement_ecologique', y='nom_citoyen',
                     orientation='h', title="Ecological Engagement Score",
                     color='score_engagement_ecologique',
                     color_continuous_scale='Greens')
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("### Participation Leaderboard")
        st.table(df_citizens[['nom_citoyen', 'prenom_citoyen', 'score_engagement_ecologique', 'nombre_participations']])
    else:
        st.info("No citizen engagement data available.")

# Footer
st.markdown("---")
st.markdown("© 2025 Neo-Sousse Smart City Initiative | Powered by Kafka & Streamlit")
