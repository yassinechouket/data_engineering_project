import streamlit as st
import psycopg2
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'port': 5339,
    'database': 'smart_city',
    'user': 'chouket',
    'password': '2003'
}

# Page configuration
st.set_page_config(
    page_title="Neo-Sousse 2030",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
    <style>
    .main {
        background-color: #f5f7fa;
    }
    .stMetric {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        margin: 10px 0;
    }
    .section-header {
        background: linear-gradient(90deg, #2C3E50 0%, #3498DB 100%);
        color: white;
        padding: 15px;
        border-radius: 8px;
        margin: 20px 0 10px 0;
        font-size: 1.5em;
        font-weight: bold;
    }
    div[data-testid="stDataFrame"] {
        background-color: white;
        padding: 10px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

# Database connection function
@st.cache_resource
def get_connection():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        st.error(f"Erreur de connexion à la base de données: {e}")
        return None

# Data loading functions
@st.cache_data(ttl=300)
def load_pollution_data():
    conn = get_connection()
    if conn:
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
          AND c.type_capteur = 'qualité de l''air'
        GROUP BY a.nom_arrondissement
        ORDER BY pollution_moyenne DESC;
        """
        return pd.read_sql(query, conn)
    return pd.DataFrame()

@st.cache_data(ttl=300)
def load_disponibilite_data():
    conn = get_connection()
    if conn:
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
        return pd.read_sql(query, conn)
    return pd.DataFrame()

@st.cache_data(ttl=300)
def load_citoyens_engages():
    conn = get_connection()
    if conn:
        query = """
        SELECT 
            c.id_citoyen,
            c.nom_citoyen,
            c.prenom_citoyen,
            c.email,
            c.score_engagement_ecologique,
            COUNT(p.id_consultation) AS nombre_participations,
            SUM(CASE WHEN p.vote = 'pour' THEN 1 ELSE 0 END) AS votes_pour,
            c.preferences_mobilite
        FROM citoyen c
        LEFT JOIN participation_citoyenne p ON c.id_citoyen = p.id_citoyen
        GROUP BY c.id_citoyen, c.nom_citoyen, c.prenom_citoyen, c.email, 
                 c.score_engagement_ecologique, c.preferences_mobilite
        ORDER BY c.score_engagement_ecologique DESC, nombre_participations DESC
        LIMIT 20;
        """
        return pd.read_sql(query, conn)
    return pd.DataFrame()

@st.cache_data(ttl=300)
def load_interventions_predictives():
    conn = get_connection()
    if conn:
        query = """
        SELECT 
            COUNT(DISTINCT i.id_intervention) AS nombre_interventions_predictives,
            COALESCE(SUM(i.impact_environnemental_co2_kg), 0) AS economie_co2_totale_kg,
            COALESCE(SUM(i.cout_euros), 0) AS cout_total_euros,
            COALESCE(AVG(i.duree_minutes), 0) AS duree_moyenne_minutes
        FROM intervention i
        WHERE i.nature_intervention = 'prédictive'
          AND i.date_heure_intervention >= DATE_TRUNC('month', CURRENT_DATE)
          AND i.date_heure_intervention < DATE_TRUNC('month', CURRENT_DATE) + INTERVAL '1 month';
        """
        return pd.read_sql(query, conn)
    return pd.DataFrame()

@st.cache_data(ttl=300)
def load_trajets_vehicules():
    conn = get_connection()
    if conn:
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
        ORDER BY t.economie_co2_kg DESC
        LIMIT 50;
        """
        return pd.read_sql(query, conn)
    return pd.DataFrame()

@st.cache_data(ttl=300)
def load_capteur_types():
    conn = get_connection()
    if conn:
        query = """
        SELECT 
            type_capteur,
            COUNT(*) as nombre,
            ROUND(AVG(CASE WHEN statut = 'actif' THEN 1 ELSE 0 END) * 100, 2) as taux_actif
        FROM capteur
        GROUP BY type_capteur
        ORDER BY nombre DESC;
        """
        return pd.read_sql(query, conn)
    return pd.DataFrame()

@st.cache_data(ttl=300)
def load_interventions_by_nature():
    conn = get_connection()
    if conn:
        query = """
        SELECT 
            nature_intervention,
            COUNT(*) as nombre,
            COALESCE(AVG(duree_minutes), 0) as duree_moyenne,
            COALESCE(SUM(cout_euros), 0) as cout_total,
            COALESCE(SUM(impact_environnemental_co2_kg), 0) as co2_economise
        FROM intervention
        WHERE date_heure_intervention >= NOW() - INTERVAL '30 DAYS'
        GROUP BY nature_intervention
        ORDER BY nombre DESC;
        """
        return pd.read_sql(query, conn)
    return pd.DataFrame()

@st.cache_data(ttl=300)
def load_mesures_timeline():
    conn = get_connection()
    if conn:
        query = """
        SELECT 
            DATE(date_heure_mesure) as date,
            c.type_capteur,
            AVG(valeur_mesuree) as valeur_moyenne,
            COUNT(*) as nombre_mesures
        FROM mesure m
        JOIN capteur c ON m.id_capteur = c.id_capteur
        WHERE date_heure_mesure >= NOW() - INTERVAL '7 DAYS'
        GROUP BY DATE(date_heure_mesure), c.type_capteur
        ORDER BY date, type_capteur;
        """
        return pd.read_sql(query, conn)
    return pd.DataFrame()

@st.cache_data(ttl=300)
def load_consultations():
    conn = get_connection()
    if conn:
        query = """
        SELECT 
            cc.titre_consultation,
            cc.theme,
            cc.date_debut,
            cc.date_fin,
            COUNT(pc.id_citoyen) as nombre_participants,
            SUM(CASE WHEN pc.vote = 'pour' THEN 1 ELSE 0 END) as votes_pour,
            SUM(CASE WHEN pc.vote = 'contre' THEN 1 ELSE 0 END) as votes_contre
        FROM consultation_citoyenne cc
        LEFT JOIN participation_citoyenne pc ON cc.id_consultation = pc.id_consultation
        GROUP BY cc.id_consultation, cc.titre_consultation, cc.theme, cc.date_debut, cc.date_fin
        ORDER BY cc.date_debut DESC
        LIMIT 10;
        """
        return pd.read_sql(query, conn)
    return pd.DataFrame()

@st.cache_data(ttl=300)
def load_techniciens_stats():
    conn = get_connection()
    if conn:
        query = """
        SELECT 
            t.nom_technicien,
            t.prenom_technicien,
            t.certification,
            COUNT(DISTINCT it.id_intervention) as nombre_interventions,
            STRING_AGG(DISTINCT it.role_technicien, ', ') as roles
        FROM technicien t
        LEFT JOIN intervention_technicien it ON t.id_technicien = it.id_technicien
        GROUP BY t.id_technicien, t.nom_technicien, t.prenom_technicien, t.certification
        ORDER BY nombre_interventions DESC
        LIMIT 15;
        """
        return pd.read_sql(query, conn)
    return pd.DataFrame()

# Sidebar navigation
st.sidebar.markdown("## 🌍 Neo-Sousse 2030")
st.sidebar.markdown("### Tableau de Bord Smart City")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigation",
    ["Vue d'ensemble", "Qualité de l'Air", "Capteurs", "Citoyens Engagés", 
     "Interventions", "Véhicules Autonomes", "Analyses Avancées", "Consultations", "Techniciens"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("**Dernière mise à jour**")
st.sidebar.info(datetime.now().strftime("%d/%m/%Y %H:%M"))

# Main content based on selected page
if page == "Vue d'ensemble":
    st.title("🌍 Neo-Sousse 2030 - Vue d'Ensemble")
    st.markdown("Plateforme de gestion intelligente de la ville")
    
    # KPIs row
    col1, col2, col3, col4 = st.columns(4)
    
    # Load summary data
    pollution_data = load_pollution_data()
    disponibilite_data = load_disponibilite_data()
    interventions_data = load_interventions_predictives()
    trajets_data = load_trajets_vehicules()
    
    with col1:
        if not pollution_data.empty:
            avg_pollution = pollution_data['pollution_moyenne'].mean()
            st.metric("Pollution Moyenne (24h)", f"{avg_pollution:.2f}", 
                     delta=None, delta_color="inverse")
        else:
            st.metric("Pollution Moyenne (24h)", "N/A")
    
    with col2:
        if not disponibilite_data.empty:
            avg_dispo = disponibilite_data['taux_disponibilite_pourcentage'].mean()
            st.metric("Disponibilité Capteurs", f"{avg_dispo:.1f}%")
        else:
            st.metric("Disponibilité Capteurs", "N/A")
    
    with col3:
        if not interventions_data.empty and interventions_data['nombre_interventions_predictives'].iloc[0]:
            nb_inter = int(interventions_data['nombre_interventions_predictives'].iloc[0])
            st.metric("Interventions ce mois", f"{nb_inter}")
        else:
            st.metric("Interventions ce mois", "0")
    
    with col4:
        if not trajets_data.empty:
            total_eco = trajets_data['economie_co2_kg'].sum()
            st.metric("Économie CO2 (kg)", f"{total_eco:.1f}")
        else:
            st.metric("Économie CO2 (kg)", "N/A")
    
    st.markdown("---")
    
    # Two-column layout for charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="section-header">Distribution de la Pollution</div>', 
                   unsafe_allow_html=True)
        if not pollution_data.empty:
            fig = px.bar(pollution_data, 
                        x='nom_arrondissement', 
                        y='pollution_moyenne',
                        color='pollution_moyenne',
                        color_continuous_scale='Reds',
                        labels={'pollution_moyenne': 'Pollution Moyenne', 
                               'nom_arrondissement': 'Arrondissement'})
            fig.update_layout(showlegend=False, height=350)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Aucune donnée disponible")
    
    with col2:
        st.markdown('<div class="section-header">Disponibilité des Capteurs</div>', 
                   unsafe_allow_html=True)
        if not disponibilite_data.empty:
            fig = px.pie(disponibilite_data, 
                        values='capteurs_actifs', 
                        names='nom_arrondissement',
                        color_discrete_sequence=px.colors.sequential.Blues_r)
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Aucune donnée disponible")

elif page == "Qualité de l'Air":
    st.title("🌫️ Qualité de l'Air - Dernières 24 Heures")
    
    pollution_data = load_pollution_data()
    
    if not pollution_data.empty:
        # Statistics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Zone la plus polluée", 
                     pollution_data.iloc[0]['nom_arrondissement'])
        with col2:
            st.metric("Pollution maximale", 
                     f"{pollution_data['pollution_max'].max():.2f}")
        with col3:
            st.metric("Nombre de mesures", 
                     f"{pollution_data['nombre_mesures'].sum():.0f}")
        
        st.markdown("---")
        
        # Detailed chart
        st.markdown('<div class="section-header">Niveaux de Pollution par Arrondissement</div>', 
                   unsafe_allow_html=True)
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=pollution_data['nom_arrondissement'],
            y=pollution_data['pollution_moyenne'],
            name='Moyenne',
            marker_color='#3498DB'
        ))
        fig.add_trace(go.Scatter(
            x=pollution_data['nom_arrondissement'],
            y=pollution_data['pollution_max'],
            name='Maximum',
            mode='lines+markers',
            marker_color='#E74C3C',
            line=dict(width=3)
        ))
        fig.update_layout(height=400, barmode='group')
        st.plotly_chart(fig, use_container_width=True)
        
        # Data table
        st.markdown('<div class="section-header">Données Détaillées</div>', 
                   unsafe_allow_html=True)
        st.dataframe(pollution_data, use_container_width=True, hide_index=True)
    else:
        st.warning("Aucune donnée de pollution disponible pour les dernières 24 heures")

elif page == "Capteurs":
    st.title("État des Capteurs par Arrondissement")
    
    disponibilite_data = load_disponibilite_data()
    
    if not disponibilite_data.empty:
        # Summary metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            total = disponibilite_data['total_capteurs'].sum()
            st.metric("Total Capteurs", f"{total:.0f}")
        with col2:
            actifs = disponibilite_data['capteurs_actifs'].sum()
            st.metric("Capteurs Actifs", f"{actifs:.0f}")
        with col3:
            taux_global = (actifs / total * 100) if total > 0 else 0
            st.metric("Taux Global", f"{taux_global:.1f}%")
        
        st.markdown("---")
        
        # Horizontal bar chart
        st.markdown('<div class="section-header">Taux de Disponibilité par Arrondissement</div>', 
                   unsafe_allow_html=True)
        fig = px.bar(disponibilite_data, 
                    y='nom_arrondissement', 
                    x='taux_disponibilite_pourcentage',
                    orientation='h',
                    color='taux_disponibilite_pourcentage',
                    color_continuous_scale='Greens',
                    labels={'taux_disponibilite_pourcentage': 'Taux (%)', 
                           'nom_arrondissement': 'Arrondissement'})
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        # Comparison chart
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div class="section-header">Total vs Actifs</div>', 
                       unsafe_allow_html=True)
            fig = go.Figure()
            fig.add_trace(go.Bar(
                name='Total',
                x=disponibilite_data['nom_arrondissement'],
                y=disponibilite_data['total_capteurs'],
                marker_color='#95A5A6'
            ))
            fig.add_trace(go.Bar(
                name='Actifs',
                x=disponibilite_data['nom_arrondissement'],
                y=disponibilite_data['capteurs_actifs'],
                marker_color='#27AE60'
            ))
            fig.update_layout(barmode='group', height=350)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown('<div class="section-header">Données Détaillées</div>', 
                       unsafe_allow_html=True)
            st.dataframe(disponibilite_data, use_container_width=True, hide_index=True)
    else:
        st.warning("Aucune donnée de capteurs disponible")

elif page == "Citoyens Engagés":
    st.title("👥 Citoyens les Plus Engagés")
    
    citoyens_data = load_citoyens_engages()
    
    if not citoyens_data.empty:
        # Top 3 citizens
        st.markdown('<div class="section-header">🏆 Top 3 Citoyens</div>', 
                   unsafe_allow_html=True)
        cols = st.columns(3)
        for idx, col in enumerate(cols):
            if idx < len(citoyens_data):
                with col:
                    citoyen = citoyens_data.iloc[idx]
                    st.markdown(f"""
                    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                padding: 20px; border-radius: 10px; color: white; text-align: center;'>
                        <h2>#{idx + 1}</h2>
                        <h3>{citoyen['prenom_citoyen']} {citoyen['nom_citoyen']}</h3>
                        <p style='font-size: 24px; font-weight: bold;'>
                            Score: {citoyen['score_engagement_ecologique']}
                        </p>
                        <p>Participations: {citoyen['nombre_participations']}</p>
                    </div>
                    """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="section-header">Distribution des Scores</div>', 
                       unsafe_allow_html=True)
            fig = px.histogram(citoyens_data, 
                             x='score_engagement_ecologique',
                             nbins=20,
                             color_discrete_sequence=['#3498DB'])
            fig.update_layout(height=350, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown('<div class="section-header">Préférences de Mobilité</div>', 
                       unsafe_allow_html=True)
            mobilite_counts = citoyens_data['preferences_mobilite'].value_counts()
            fig = px.pie(values=mobilite_counts.values, 
                        names=mobilite_counts.index,
                        color_discrete_sequence=px.colors.sequential.Teal)
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)
        
        # Full table
        st.markdown('<div class="section-header">Liste Complète</div>', 
                   unsafe_allow_html=True)
        display_data = citoyens_data[['prenom_citoyen', 'nom_citoyen', 
                                      'score_engagement_ecologique', 
                                      'nombre_participations', 'votes_pour', 
                                      'preferences_mobilite']]
        st.dataframe(display_data, use_container_width=True, hide_index=True)
    else:
        st.warning("Aucune donnée de citoyens disponible")

elif page == "Interventions":
    st.title("🔧 Interventions Prédictives du Mois")
    
    interventions_data = load_interventions_predictives()
    
    if not interventions_data.empty and interventions_data['nombre_interventions_predictives'].iloc[0]:
        row = interventions_data.iloc[0]
        
        # Metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Nombre d'Interventions", 
                     f"{int(row['nombre_interventions_predictives'])}")
        with col2:
            st.metric("Économie CO2 (kg)", 
                     f"{row['economie_co2_totale_kg']:.2f}")
        with col3:
            st.metric("Coût Total (€)", 
                     f"{row['cout_total_euros']:.2f}")
        with col4:
            st.metric("Durée Moyenne (min)", 
                     f"{row['duree_moyenne_minutes']:.1f}")
        
        st.markdown("---")
        
        # Visual representation
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="section-header">Impact Environnemental</div>', 
                       unsafe_allow_html=True)
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=row['economie_co2_totale_kg'],
                title={'text': "Économie CO2 (kg)"},
                gauge={'axis': {'range': [None, row['economie_co2_totale_kg'] * 1.5]},
                       'bar': {'color': "#27AE60"},
                       'steps': [
                           {'range': [0, row['economie_co2_totale_kg'] * 0.5], 
                            'color': "#D5F4E6"},
                           {'range': [row['economie_co2_totale_kg'] * 0.5, 
                                     row['economie_co2_totale_kg']], 
                            'color': "#A9DFBF"}],
                       'threshold': {
                           'line': {'color': "red", 'width': 4},
                           'thickness': 0.75,
                           'value': row['economie_co2_totale_kg']}}))
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown('<div class="section-header">Analyse des Coûts</div>', 
                       unsafe_allow_html=True)
            cout_moyen = row['cout_total_euros'] / row['nombre_interventions_predictives']
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=['Coût Total', 'Coût Moyen'],
                y=[row['cout_total_euros'], cout_moyen],
                marker_color=['#3498DB', '#E74C3C']
            ))
            fig.update_layout(height=350, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        st.markdown('<div class="section-header">Récapitulatif</div>', 
                   unsafe_allow_html=True)
        st.dataframe(interventions_data, use_container_width=True, hide_index=True)
    else:
        st.info("Aucune intervention prédictive ce mois-ci")

elif page == "Véhicules Autonomes":
    st.title("Trajets des Véhicules Autonomes")
    
    trajets_data = load_trajets_vehicules()
    
    if not trajets_data.empty:
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Nombre de Trajets", f"{len(trajets_data)}")
        with col2:
            total_co2 = trajets_data['economie_co2_kg'].sum()
            st.metric("Économie CO2 Total (kg)", f"{total_co2:.2f}")
        with col3:
            duree_totale = trajets_data['duree_minutes'].sum()
            st.metric("Durée Totale (heures)", f"{duree_totale / 60:.1f}")
        with col4:
            nb_vehicules = trajets_data['plaque_immatriculation'].nunique()
            st.metric("Véhicules Actifs", f"{nb_vehicules}")
        
        st.markdown("---")
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="section-header">Top 10 Économies CO2</div>', 
                       unsafe_allow_html=True)
            top_10 = trajets_data.nlargest(10, 'economie_co2_kg')
            fig = px.bar(top_10, 
                        x='economie_co2_kg', 
                        y='plaque_immatriculation',
                        orientation='h',
                        color='economie_co2_kg',
                        color_continuous_scale='Greens',
                        labels={'economie_co2_kg': 'Économie CO2 (kg)', 
                               'plaque_immatriculation': 'Véhicule'})
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown('<div class="section-header">Distribution par Type d\'Énergie</div>', 
                       unsafe_allow_html=True)
            energie_counts = trajets_data['energie_utilisee'].value_counts()
            fig = px.pie(values=energie_counts.values, 
                        names=energie_counts.index,
                        color_discrete_sequence=px.colors.sequential.Teal)
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        # Type de véhicule
        st.markdown('<div class="section-header">Économie CO2 par Type de Véhicule</div>', 
                   unsafe_allow_html=True)
        eco_by_type = trajets_data.groupby('type_vehicule')['economie_co2_kg'].sum().sort_values(ascending=False)
        fig = px.bar(x=eco_by_type.index, 
                    y=eco_by_type.values,
                    color=eco_by_type.values,
                    color_continuous_scale='Blues',
                    labels={'x': 'Type de Véhicule', 'y': 'Économie CO2 (kg)'})
        fig.update_layout(height=350, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        
        # Full table
        st.markdown('<div class="section-header">Liste des Trajets</div>', 
                   unsafe_allow_html=True)
        display_data = trajets_data[['plaque_immatriculation', 'type_vehicule', 
                                     'energie_utilisee', 'origine', 'destination',
                                     'duree_minutes', 'economie_co2_kg']]
        st.dataframe(display_data, use_container_width=True, hide_index=True)
    else:
        st.warning("Aucune donnée de trajets disponible")

elif page == "Analyses Avancées":
    st.title("📊 Analyses Avancées")
    
    # Load data for advanced analytics
    capteur_types = load_capteur_types()
    interventions_nature = load_interventions_by_nature()
    mesures_timeline = load_mesures_timeline()
    
    # Types de capteurs analysis
    if not capteur_types.empty:
        st.markdown('<div class="section-header">Analyse des Types de Capteurs</div>', 
                   unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.treemap(capteur_types, 
                           path=['type_capteur'], 
                           values='nombre',
                           color='taux_actif',
                           color_continuous_scale='RdYlGn',
                           labels={'nombre': 'Nombre de Capteurs', 
                                  'taux_actif': 'Taux Actif (%)'})
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = go.Figure()
            fig.add_trace(go.Bar(
                name='Nombre de Capteurs',
                x=capteur_types['type_capteur'],
                y=capteur_types['nombre'],
                marker_color='#3498DB',
                yaxis='y'
            ))
            fig.add_trace(go.Scatter(
                name='Taux Actif (%)',
                x=capteur_types['type_capteur'],
                y=capteur_types['taux_actif'],
                marker_color='#27AE60',
                yaxis='y2',
                mode='lines+markers',
                line=dict(width=3)
            ))
            fig.update_layout(
                yaxis=dict(title='Nombre'),
                yaxis2=dict(title='Taux Actif (%)', overlaying='y', side='right'),
                height=400,
                hovermode='x unified'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Interventions analysis
    if not interventions_nature.empty:
        st.markdown('<div class="section-header">Analyse des Interventions (30 derniers jours)</div>', 
                   unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_interventions = interventions_nature['nombre'].sum()
            st.metric("Total Interventions", f"{int(total_interventions)}")
        
        with col2:
            total_cout = interventions_nature['cout_total'].sum()
            st.metric("Coût Total (€)", f"{total_cout:,.2f}")
        
        with col3:
            total_co2 = interventions_nature['co2_economise'].sum()
            st.metric("CO2 Économisé (kg)", f"{total_co2:.2f}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.bar(interventions_nature, 
                        x='nature_intervention', 
                        y='nombre',
                        color='nature_intervention',
                        labels={'nombre': 'Nombre', 'nature_intervention': 'Type'},
                        color_discrete_sequence=px.colors.qualitative.Set3)
            fig.update_layout(height=350, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=interventions_nature['nature_intervention'],
                y=interventions_nature['duree_moyenne'],
                mode='lines+markers',
                name='Durée Moyenne',
                marker=dict(size=12, color='#E74C3C'),
                line=dict(width=3)
            ))
            fig.update_layout(
                title='Durée Moyenne par Type (minutes)',
                height=350,
                yaxis_title='Minutes'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        st.dataframe(interventions_nature, use_container_width=True, hide_index=True)
    
    # Timeline analysis
    if not mesures_timeline.empty:
        st.markdown("---")
        st.markdown('<div class="section-header">Évolution des Mesures (7 derniers jours)</div>', 
                   unsafe_allow_html=True)
        
        fig = px.line(mesures_timeline, 
                     x='date', 
                     y='valeur_moyenne',
                     color='type_capteur',
                     markers=True,
                     labels={'valeur_moyenne': 'Valeur Moyenne', 
                            'date': 'Date',
                            'type_capteur': 'Type de Capteur'})
        fig.update_layout(height=400, hovermode='x unified')
        st.plotly_chart(fig, use_container_width=True)
        
        # Heat map of measurements
        pivot_data = mesures_timeline.pivot(index='type_capteur', 
                                           columns='date', 
                                           values='valeur_moyenne')
        
        fig = px.imshow(pivot_data,
                       labels=dict(x="Date", y="Type de Capteur", color="Valeur"),
                       aspect="auto",
                       color_continuous_scale='RdYlGn_r')
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)

elif page == "Consultations":
    st.title("Consultations Citoyennes")
    
    consultations_data = load_consultations()
    
    if not consultations_data.empty:
        # Summary metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_consultations = len(consultations_data)
            st.metric("Consultations Totales", f"{total_consultations}")
        
        with col2:
            total_participants = consultations_data['nombre_participants'].sum()
            st.metric("Participants Totaux", f"{int(total_participants)}")
        
        with col3:
            avg_participation = consultations_data['nombre_participants'].mean()
            st.metric("Participation Moyenne", f"{avg_participation:.1f}")
        
        st.markdown("---")
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="section-header">Participation par Consultation</div>', 
                       unsafe_allow_html=True)
            fig = px.bar(consultations_data, 
                        y='titre_consultation', 
                        x='nombre_participants',
                        orientation='h',
                        color='nombre_participants',
                        color_continuous_scale='Blues',
                        labels={'nombre_participants': 'Participants', 
                               'titre_consultation': 'Consultation'})
            fig.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown('<div class="section-header">Distribution par Thème</div>', 
                       unsafe_allow_html=True)
            theme_counts = consultations_data.groupby('theme')['nombre_participants'].sum()
            fig = px.pie(values=theme_counts.values, 
                        names=theme_counts.index,
                        color_discrete_sequence=px.colors.sequential.Purples_r)
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        # Voting analysis
        st.markdown('<div class="section-header">Analyse des Votes</div>', 
                   unsafe_allow_html=True)
        
        consultations_with_votes = consultations_data[
            (consultations_data['votes_pour'] > 0) | (consultations_data['votes_contre'] > 0)
        ].copy()
        
        if not consultations_with_votes.empty:
            consultations_with_votes['taux_approbation'] = (
                consultations_with_votes['votes_pour'] / 
                (consultations_with_votes['votes_pour'] + consultations_with_votes['votes_contre']) * 100
            )
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                name='Pour',
                y=consultations_with_votes['titre_consultation'],
                x=consultations_with_votes['votes_pour'],
                orientation='h',
                marker_color='#27AE60'
            ))
            fig.add_trace(go.Bar(
                name='Contre',
                y=consultations_with_votes['titre_consultation'],
                x=consultations_with_votes['votes_contre'],
                orientation='h',
                marker_color='#E74C3C'
            ))
            fig.update_layout(barmode='stack', height=350)
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        st.markdown('<div class="section-header">Liste Détaillée</div>', 
                   unsafe_allow_html=True)
        st.dataframe(consultations_data, use_container_width=True, hide_index=True)
    else:
        st.warning("Aucune consultation disponible")

elif page == "Techniciens":
    st.title("👷 Performance des Techniciens")
    
    techniciens_data = load_techniciens_stats()
    
    if not techniciens_data.empty:
        # Summary metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_techniciens = len(techniciens_data)
            st.metric("Nombre de Techniciens", f"{total_techniciens}")
        
        with col2:
            total_interventions = techniciens_data['nombre_interventions'].sum()
            st.metric("Interventions Totales", f"{int(total_interventions)}")
        
        with col3:
            avg_interventions = techniciens_data['nombre_interventions'].mean()
            st.metric("Moyenne par Technicien", f"{avg_interventions:.1f}")
        
        st.markdown("---")
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="section-header">Top 10 Techniciens Actifs</div>', 
                       unsafe_allow_html=True)
            top_10 = techniciens_data.nlargest(10, 'nombre_interventions')
            top_10['nom_complet'] = top_10['prenom_technicien'] + ' ' + top_10['nom_technicien']
            
            fig = px.bar(top_10, 
                        y='nom_complet', 
                        x='nombre_interventions',
                        orientation='h',
                        color='nombre_interventions',
                        color_continuous_scale='Viridis',
                        labels={'nombre_interventions': 'Interventions', 
                               'nom_complet': 'Technicien'})
            fig.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown('<div class="section-header">Distribution par Certification</div>', 
                       unsafe_allow_html=True)
            cert_counts = techniciens_data['certification'].value_counts()
            fig = px.pie(values=cert_counts.values, 
                        names=cert_counts.index,
                        color_discrete_sequence=px.colors.sequential.Oranges_r)
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        # Performance distribution
        st.markdown('<div class="section-header">Distribution des Performances</div>', 
                   unsafe_allow_html=True)
        
        fig = px.histogram(techniciens_data, 
                         x='nombre_interventions',
                         nbins=15,
                         color_discrete_sequence=['#9B59B6'],
                         labels={'nombre_interventions': 'Nombre d\'Interventions'})
        fig.update_layout(height=300, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        st.markdown('<div class="section-header">Liste Complète des Techniciens</div>', 
                   unsafe_allow_html=True)
        display_data = techniciens_data[['prenom_technicien', 'nom_technicien', 
                                        'certification', 'nombre_interventions', 'roles']]
        st.dataframe(display_data, use_container_width=True, hide_index=True)
    else:
        st.warning("Aucune donnée de techniciens disponible")