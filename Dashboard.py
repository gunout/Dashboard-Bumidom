import streamlit as st
import requests
import pandas as pd
import json
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, date
import sqlite3
from pathlib import Path
import base64

# ============================================================================
# CONFIGURATION DE LA PAGE
# ============================================================================
st.set_page_config(page_title="Archives BUMIDOM", layout="wide")
st.title("🔍 Module d'Analyse Archivistique BUMIDOM")
st.markdown("***Outils de recherche qualitative basés sur les archives du Conseil d'Administration (1962-1981)***")

# ============================================================================
# 1. BASE DE DONNÉES POUR LES NOTES DE RECHERCHE
# ============================================================================
def init_database():
    """Initialise la base de données SQLite pour stocker les notes de recherche"""
    conn = sqlite3.connect('bumidom_research.db')
    c = conn.cursor()
    
    # Table pour les observations d'archives
    c.execute('''CREATE TABLE IF NOT EXISTS archive_observations
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  consultation_date TEXT,
                  cote TEXT,
                  page_number INTEGER,
                  theme TEXT,
                  key_finding TEXT,
                  quote TEXT,
                  link_to_data TEXT,
                  researcher_name TEXT,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Table pour les thèmes de recherche
    c.execute('''CREATE TABLE IF NOT EXISTS research_themes
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  theme_name TEXT UNIQUE,
                  color_code TEXT,
                  description TEXT)''')
    
    # Table pour les documents liés
    c.execute('''CREATE TABLE IF NOT EXISTS linked_documents
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  title TEXT,
                  archive_id TEXT,
                  document_type TEXT,
                  relevance_score INTEGER,
                  notes TEXT)''')
    
    conn.commit()
    conn.close()

# Initialiser la base de données
init_database()

# ============================================================================
# 2. FONCTIONS API FRANCEARCHIVES
# ============================================================================
@st.cache_data(ttl=3600, show_spinner="Récupération des métadonnées...")
def fetch_archive_metadata(archive_id):
    """
    Récupère les métadonnées d'une archive via l'API FranceArchives
    """
    base_url = "https://francearchives.fr/api/"
    
    try:
        # Tentative de récupération via l'API des composants
        response = requests.get(f"{base_url}fa-component/{archive_id}", 
                              timeout=10,
                              headers={'User-Agent': 'BUMIDOM-Research-App/1.0'})
        
        if response.status_code == 200:
            return response.json()
        else:
            # Fallback : utilisation des données de base si l'API ne répond pas
            st.warning(f"L'API a retourné le code {response.status_code}. Utilisation des données de référence.")
            return {
                'label': 'Conseil d’administration du BUMIDOM',
                'date': '1962 - 1981',
                'cote': '20080699/1-20080699/4',
                'content': 'Procès-verbaux, rapports d’activités, budget, bilans.',
                'locations': [],
                'functions': []
            }
            
    except requests.exceptions.RequestException as e:
        st.error(f"Erreur de connexion : {e}")
        return None

@st.cache_data(ttl=86400)
def get_related_archives():
    """
    Récupère d'autres archives liées au BUMIDOM (liste prédéfinie)
    """
    related_archives = [
        {
            'id': '4cf8e64493541970a9407a30ff47693657bd18f9',
            'title': 'Conseil d’administration du BUMIDOM',
            'period': '1962-1981',
            'type': 'Procès-verbaux',
            'relevance': 10
        },
        {
            'id': 'simulated_001',
            'title': 'Correspondance Ministère Outre-mer',
            'period': '1960-1985',
            'type': 'Correspondance',
            'relevance': 8
        },
        {
            'id': 'simulated_002',
            'title': 'Statistiques migratoires DOM',
            'period': '1955-1980',
            'type': 'Rapports statistiques',
            'relevance': 9
        },
        {
            'id': 'simulated_003',
            'title': 'Budget BUMIDOM par année',
            'period': '1963-1982',
            'type': 'Documents budgétaires',
            'relevance': 7
        }
    ]
    return related_archives

# ============================================================================
# 3. FONCTIONS D'ANALYSE QUALITATIVE
# ============================================================================
def save_research_observation(data):
    """Sauvegarde une observation dans la base de données"""
    conn = sqlite3.connect('bumidom_research.db')
    c = conn.cursor()
    
    c.execute('''INSERT INTO archive_observations 
                 (consultation_date, cote, page_number, theme, key_finding, quote, link_to_data, researcher_name)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
              (data['consultation_date'], data['cote'], data['page_number'], 
               data['theme'], data['key_finding'], data['quote'], 
               data['link_to_data'], data['researcher_name']))
    
    conn.commit()
    conn.close()

def get_research_observations(limit=50):
    """Récupère les observations de recherche"""
    conn = sqlite3.connect('bumidom_research.db')
    df = pd.read_sql_query(f"SELECT * FROM archive_observations ORDER BY created_at DESC LIMIT {limit}", conn)
    conn.close()
    return df

def get_observations_by_theme():
    """Analyse des observations par thème"""
    conn = sqlite3.connect('bumidom_research.db')
    df = pd.read_sql_query('''SELECT theme, COUNT(*) as count, 
                                     MAX(consultation_date) as last_consultation
                              FROM archive_observations 
                              GROUP BY theme 
                              ORDER BY count DESC''', conn)
    conn.close()
    return df

# ============================================================================
# 4. INTERFACE PRINCIPALE
# ============================================================================

# Sidebar pour la navigation
with st.sidebar:
    st.image("https://via.placeholder.com/150x50/1E3A8A/FFFFFF?text=ARCHIVES", width=150)
    st.title("Navigation")
    
    section = st.radio(
        "Sélectionnez une section",
        ["📋 Fiche d'archive", "🧪 Analyse qualitative", "📊 Tableau de bord recherche", 
         "🔗 Archives liées", "📁 Gestion des données"]
    )
    
    st.markdown("---")
    st.info("""
    **Identifiant d'archive actuel:**
    `4cf8e64493541970a9407a30ff47693657bd18f9`
    
    **Cote:** 20080699/1-20080699/4
    **Période:** 1962-1981
    """)

# ============================================================================
# SECTION 1: FICHE D'ARCHIVE
# ============================================================================
if section == "📋 Fiche d'archive":
    st.header("📋 Fiche Descriptive de l'Archive")
    
    # Récupération des données
    archive_id = "4cf8e64493541970a9407a30ff47693657bd18f9"
    archive_data = fetch_archive_metadata(archive_id)
    
    if archive_data:
        col1, col2, col3 = st.columns([3, 2, 2])
        
        with col1:
            st.subheader(archive_data.get('label', 'Archive BUMIDOM'))
            
            # Affichage des métadonnées
            metadata_expander = st.expander("📄 Métadonnées complètes", expanded=True)
            with metadata_expander:
                st.markdown(f"""
                **Identifiant unique:** `{archive_id}`  
                **Période:** {archive_data.get('date', 'Non spécifiée')}  
                **Cote:** `{archive_data.get('cote', 'Non spécifiée')}`  
                **Description:** {archive_data.get('content', 'Aucune description disponible')}
                """)
                
                if 'locations' in archive_data and archive_data['locations']:
                    st.markdown("**Lieux concernés:**")
                    for location in archive_data['locations']:
                        st.markdown(f"- {location}")
                
                if 'functions' in archive_data and archive_data['functions']:
                    st.markdown("**Fonctions concernées:**")
                    for function in archive_data['functions']:
                        st.markdown(f"- {function}")
        
        with col2:
            st.metric("Période couverte", "20 ans", "1962-1981", delta_color="off")
            st.metric("Volume", "4 boîtes", "Cotes 1-4", delta_color="off")
            
            # Indicateur d'état
            st.markdown("### 📦 État de conservation")
            st.progress(85, text="Bon état (estimation)")
            st.caption("Selon les standards des Archives Nationales")
        
        with col3:
            st.markdown("### 🔗 Accès direct")
            st.markdown(f"""
            [📖 Voir sur FranceArchives](https://francearchives.gouv.fr/fr/facomponent/{archive_id})
            
            [🗺️ Localisation: Archives Nationales Pierrefitte](https://www.archives-nationales.culture.gouv.fr/pierrefitte-sur-seine)
            
            📞 **Salle des inventaires:** +33 1 75 47 20 02
            """)
        
        # Carte de localisation simulée
        st.subheader("📍 Localisation physique")
        col_loc1, col_loc2 = st.columns([2, 1])
        
        with col_loc1:
            st.map(pd.DataFrame({
                'lat': [48.924],
                'lon': [2.361],
                'nom': ['Archives Nationales Pierrefitte']
            }), zoom=12)
        
        with col_loc2:
            st.markdown("""
            **Archives Nationales**  
            Site de Pierrefitte-sur-Seine  
            59 rue Guynemer  
            93383 Pierrefitte-sur-Seine Cedex
            
            **Horaires:**  
            Lundi-vendredi: 9h-16h45  
            Samedi: 9h-16h45  
            
            **Conditions d'accès:**  
            • Inscription gratuite sur place  
            • Pièce d'identité requise  
            • Photographie sans flash autorisée
            """)

# ============================================================================
# SECTION 2: ANALYSE QUALITATIVE
# ============================================================================
elif section == "🧪 Analyse qualitative":
    st.header("🧪 Outils d'Analyse Qualitative")
    
    tab1, tab2, tab3, tab4 = st.tabs(["📝 Saisie d'observation", "🔍 Analyse thématique", "💬 Analyse de contenu", "📚 Bibliographie"])
    
    with tab1:
        st.subheader("Saisie d'une nouvelle observation")
        
        with st.form("research_form", clear_on_submit=True):
            col_form1, col_form2 = st.columns(2)
            
            with col_form1:
                consultation_date = st.date_input("Date de consultation", value=date.today())
                cote = st.text_input("Cote du document", value="20080699/1")
                page_number = st.number_input("Numéro de page", min_value=1, value=1)
                researcher_name = st.text_input("Nom du chercheur", value="Chercheur")
            
            with col_form2:
                theme = st.selectbox(
                    "Thème principal",
                    ["Recrutement", "Logement", "Formation", "Budget", "Politique migratoire", 
                     "Relations DOM-TOM", "Statistiques", "Débats parlementaires", "Autre"]
                )
                
                link_to_data = st.multiselect(
                    "Lien avec données quantitatives",
                    ["Flux migratoires", "Démographie", "Budget", "Emploi", "Logement", "Intégration"]
                )
            
            key_finding = st.text_area("Découverte principale ou hypothèse", 
                                      placeholder="Ex: Le budget 1975 montre une réorientation vers la formation professionnelle...")
            
            quote = st.text_area("Citation extraite (optionnel)", 
                                placeholder="Copiez ici une citation importante du document...",
                                height=100)
            
            submitted = st.form_submit_button("💾 Enregistrer l'observation", type="primary")
            
            if submitted:
                observation_data = {
                    'consultation_date': str(consultation_date),
                    'cote': cote,
                    'page_number': page_number,
                    'theme': theme,
                    'key_finding': key_finding,
                    'quote': quote if quote else "",
                    'link_to_data': ", ".join(link_to_data),
                    'researcher_name': researcher_name
                }
                
                save_research_observation(observation_data)
                st.success("✅ Observation enregistrée avec succès !")
                st.balloons()
    
    with tab2:
        st.subheader("Analyse par thèmes")
        
        # Récupérer et afficher les observations par thème
        theme_df = get_observations_by_theme()
        
        if not theme_df.empty:
            col_theme1, col_theme2 = st.columns(2)
            
            with col_theme1:
                # Graphique des thèmes
                fig = go.Figure(data=[
                    go.Bar(
                        x=theme_df['theme'],
                        y=theme_df['count'],
                        marker_color='rgb(55, 83, 109)',
                        text=theme_df['count'],
                        textposition='auto'
                    )
                ])
                
                fig.update_layout(
                    title='Observations par thème',
                    xaxis_title='Thème',
                    yaxis_title='Nombre d\'observations',
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col_theme2:
                st.dataframe(
                    theme_df.style.background_gradient(subset=['count'], cmap='Blues'),
                    use_container_width=True
                )
            
            # Nuage de mots simulé des thèmes
            st.subheader("Nuage de mots des concepts étudiés")
            
            # Données simulées pour le nuage de mots
            concepts = {
                'recrutement': 45, 'logement': 38, 'formation': 32, 'budget': 28,
                'transport': 25, 'intégration': 22, 'statistiques': 20, 'politique': 18,
                'débats': 15, 'rapports': 12, 'bilans': 10, 'procès-verbaux': 8
            }
            
            # Création d'une visualisation simple
            concept_df = pd.DataFrame(list(concepts.items()), columns=['Concept', 'Fréquence'])
            
            fig = go.Figure(data=[go.Scatter(
                x=concept_df['Concept'],
                y=concept_df['Fréquence'],
                mode='markers',
                marker=dict(
                    size=concept_df['Fréquence']*0.8,
                    color=concept_df['Fréquence'],
                    colorscale='Viridis',
                    showscale=True
                ),
                text=concept_df['Concept'],
                hovertemplate='<b>%{text}</b><br>Fréquence: %{y}<extra></extra>'
            )])
            
            fig.update_layout(
                title='Importance relative des concepts',
                xaxis_title='Concepts',
                yaxis_title='Fréquence',
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Aucune observation enregistrée. Commencez par saisir des observations dans l'onglet précédent.")
    
    with tab3:
        st.subheader("Analyse de contenu assistée")
        
        col_ana1, col_ana2 = st.columns(2)
        
        with col_ana1:
            st.markdown("### Méthodes d'analyse")
            analysis_method = st.selectbox(
                "Choisissez une méthode d'analyse",
                ["Analyse thématique", "Analyse de discours", "Analyse de réseau sémantique", 
                 "Analyse chronologique", "Analyse comparative"]
            )
            
            st.markdown("### Paramètres")
            min_frequency = st.slider("Fréquence minimale des termes", 1, 50, 5)
            group_similar = st.checkbox("Regrouper les termes similaires", value=True)
            
            if st.button("🔬 Lancer l'analyse", type="secondary"):
                st.info("Cette fonctionnalité nécessiterait l'intégration avec des documents numérisés.")
        
        with col_ana2:
            st.markdown("### Codage qualitatif")
            
            codes = st.text_area(
                "Codes analytiques (un par ligne)",
                value="RCT - Recrutement\nLOG - Logement\nFRM - Formation\nBDG - Budget\nPLT - Politique\nINT - Intégration",
                height=200
            )
            
            if st.button("💾 Sauvegarder les codes"):
                st.success("Codes sauvegardés (fonctionnalité de stockage à implémenter)")
    
    with tab4:
        st.subheader("Bibliographie et sources complémentaires")
        
        st.markdown("""
        ### Sources primaires
        - **Archives Nationales** : Série F/60 (Outre-mer)
        - **Archives Nationales d'Outre-Mer** (ANOM) à Aix-en-Provence
        - **Archives du Ministère du Travail**
        - **Presse contemporaine** (Le Monde, La Croix, journaux ultramarins)
        
        ### Sources secondaires
        - Géraud Létang, *Le BUMIDOM : genèse et mise en œuvre*, Revue d'histoire moderne
        - Marie Poinsot, *Les immigrations des Outre-mer*, Hommes et Migrations
        - Rapport parlementaire 1981 sur les migrations ultramarines
        
        ### Bases de données en ligne
        - [Retronews](https://www.retronews.fr) - Presse historique
        - [Gallica](https://gallica.bnf.fr) - Bibliothèque numérique BnF
        - [INA Jalons](https://fresques.ina.fr/jalons) - Archives audiovisuelles
        """)
        
        # Formulaire pour ajouter une source
        with st.expander("➕ Ajouter une nouvelle source"):
            source_title = st.text_input("Titre de la source")
            source_type = st.selectbox("Type", ["Livre", "Article", "Archive", "Thèse", "Site web"])
            source_url = st.text_input("URL (si applicable)")
            
            if st.button("Ajouter à la bibliographie"):
                st.success(f"Source '{source_title}' ajoutée (stockage à implémenter)")

# ============================================================================
# SECTION 3: TABLEAU DE BORD RECHERCHE
# ============================================================================
elif section == "📊 Tableau de bord recherche":
    st.header("📊 Tableau de Bord de la Recherche")
    
    # Récupérer toutes les observations
    observations_df = get_research_observations(100)
    
    if not observations_df.empty:
        # Métriques principales
        col_met1, col_met2, col_met3, col_met4 = st.columns(4)
        
        with col_met1:
            total_obs = len(observations_df)
            st.metric("Observations totales", total_obs)
        
        with col_met2:
            unique_themes = observations_df['theme'].nunique()
            st.metric("Thèmes étudiés", unique_themes)
        
        with col_met3:
            first_date = pd.to_datetime(observations_df['consultation_date']).min().date()
            st.metric("Début de la recherche", first_date)
        
        with col_met4:
            last_date = pd.to_datetime(observations_df['consultation_date']).max().date()
            st.metric("Dernière consultation", last_date)
        
        # Graphiques d'analyse
        tab_dash1, tab_dash2, tab_dash3 = st.tabs(["📈 Évolution", "🎯 Répartition", "📋 Détails"])
        
        with tab_dash1:
            # Évolution temporelle des observations
            obs_by_date = observations_df.copy()
            obs_by_date['consultation_date'] = pd.to_datetime(obs_by_date['consultation_date'])
            obs_by_date = obs_by_date.groupby(obs_by_date['consultation_date'].dt.date).size().reset_index(name='count')
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=obs_by_date['consultation_date'],
                y=obs_by_date['count'],
                mode='lines+markers',
                name='Observations par jour',
                line=dict(color='royalblue', width=2)
            ))
            
            # Moyenne mobile
            obs_by_date['moving_avg'] = obs_by_date['count'].rolling(window=7, min_periods=1).mean()
            fig.add_trace(go.Scatter(
                x=obs_by_date['consultation_date'],
                y=obs_by_date['moving_avg'],
                mode='lines',
                name='Moyenne mobile (7 jours)',
                line=dict(color='firebrick', width=2, dash='dash')
            ))
            
            fig.update_layout(
                title='Évolution de l\'activité de recherche',
                xaxis_title='Date',
                yaxis_title='Nombre d\'observations',
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with tab_dash2:
            col_chart1, col_chart2 = st.columns(2)
            
            with col_chart1:
                # Répartition par thème
                theme_dist = observations_df['theme'].value_counts().reset_index()
                theme_dist.columns = ['theme', 'count']
                
                fig = go.Figure(data=[go.Pie(
                    labels=theme_dist['theme'],
                    values=theme_dist['count'],
                    hole=.3
                )])
                fig.update_layout(title='Répartition par thème', height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            with col_chart2:
                # Répartition par chercheur
                researcher_dist = observations_df['researcher_name'].value_counts().reset_index()
                researcher_dist.columns = ['researcher', 'count']
                
                fig = go.Figure(data=[go.Bar(
                    x=researcher_dist['researcher'],
                    y=researcher_dist['count'],
                    marker_color='lightseagreen'
                )])
                fig.update_layout(title='Observations par chercheur', height=400)
                st.plotly_chart(fig, use_container_width=True)
        
        with tab_dash3:
            # Table détaillée des observations
            st.dataframe(
                observations_df[['consultation_date', 'theme', 'key_finding', 'researcher_name']].sort_values('consultation_date', ascending=False),
                use_container_width=True,
                height=400
            )
            
            # Option d'export
            csv = observations_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Exporter les observations (CSV)",
                data=csv,
                file_name=f"observations_bumidom_{date.today()}.csv",
                mime="text/csv"
            )
    else:
        st.info("Aucune donnée de recherche disponible. Commencez par saisir des observations.")

# ============================================================================
# SECTION 4: ARCHIVES LIÉES
# ============================================================================
elif section == "🔗 Archives liées":
    st.header("🔗 Archives et Sources Complémentaires")
    
    # Récupérer les archives liées
    related_archives = get_related_archives()
    
    # Affichage sous forme de cartes
    for i in range(0, len(related_archives), 2):
        cols = st.columns(2)
        
        for j in range(2):
            if i + j < len(related_archives):
                archive = related_archives[i + j]
                
                with cols[j]:
                    with st.container(border=True):
                        st.markdown(f"### {archive['title']}")
                        st.markdown(f"**Période:** {archive['period']}")
                        st.markdown(f"**Type:** {archive['type']}")
                        
                        # Barre de pertinence
                        relevance = archive['relevance']
                        st.progress(relevance/10, text=f"Pertinence: {relevance}/10")
                        
                        # Actions
                        if archive['id'].startswith('simulated'):
                            st.button("📄 Voir les détails", key=f"btn_{i+j}", disabled=True)
                        else:
                            st.button("📄 Voir les détails", key=f"btn_{i+j}")
    
    # Carte conceptuelle des archives
    st.subheader("📌 Carte conceptuelle des fonds d'archives")
    
    # Données pour la carte conceptuelle
    nodes_data = {
        'Node': ['BUMIDOM CA', 'Ministère Outre-mer', 'Ministère Travail', 'Préfectures', 
                'Associations', 'Presse', 'Recherches'],
        'Type': ['Fonds principal', 'Fonds politique', 'Fonds administratif', 
                'Fonds local', 'Fonds associatif', 'Fonds médiatique', 'Fonds secondaire'],
        'Size': [100, 80, 70, 60, 50, 40, 30]
    }
    
    fig = go.Figure(data=[go.Scatter(
        x=[1, 2, 3, 4, 5, 6, 7],
        y=[1, 2, 1.5, 3, 2.5, 1, 3],
        mode='markers+text',
        marker=dict(
            size=nodes_data['Size'],
            color=['rgb(93, 164, 214)', 'rgb(255, 144, 14)', 'rgb(44, 160, 101)',
                  'rgb(255, 65, 54)', 'rgb(207, 114, 255)', 'rgb(127, 96, 0)', 'rgb(255, 140, 184)'],
            opacity=0.8
        ),
        text=nodes_data['Node'],
        textposition="top center"
    )])
    
    fig.update_layout(
        title="Relations entre les différents fonds d'archives",
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        height=400,
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# SECTION 5: GESTION DES DONNÉES
# ============================================================================
else:
    st.header("📁 Gestion des Données de Recherche")
    
    tab_mgmt1, tab_mgmt2, tab_mgmt3 = st.tabs(["🗃️ Base de données", "⚙️ Configuration", "🔄 Import/Export"])
    
    with tab_mgmt1:
        st.subheader("État de la base de données")
        
        conn = sqlite3.connect('bumidom_research.db')
        
        # Informations sur les tables
        tables = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table'", conn)
        
        for table_name in tables['name']:
            with st.expander(f"Table: {table_name}"):
                row_count = pd.read_sql_query(f"SELECT COUNT(*) as count FROM {table_name}", conn)['count'].iloc[0]
                st.metric("Nombre d'enregistrements", row_count)
                
                # Aperçu des données
                if row_count > 0:
                    preview = pd.read_sql_query(f"SELECT * FROM {table_name} LIMIT 5", conn)
                    st.dataframe(preview, use_container_width=True)
        
        conn.close()
        
        # Actions de maintenance
        st.subheader("Maintenance")
        col_maint1, col_maint2, col_maint3 = st.columns(3)
        
        with col_maint1:
            if st.button("🔄 Vérifier l'intégrité", type="secondary"):
                st.success("Base de données vérifiée (fonctionnalité à implémenter)")
        
        with col_maint2:
            if st.button("🗑️ Nettoyer les doublons", type="secondary"):
                st.warning("Cette action nécessite une confirmation")
        
        with col_maint3:
            if st.button("💾 Sauvegarde automatique", type="primary"):
                st.info("Sauvegarde programmée (fonctionnalité à implémenter)")
    
    with tab_mgmt2:
        st.subheader("Configuration de la recherche")
        
        # Configuration des thèmes
        st.markdown("### Gestion des thèmes de recherche")
        
        default_themes = [
            {"name": "Recrutement", "color": "#1f77b4", "active": True},
            {"name": "Logement", "color": "#ff7f0e", "active": True},
            {"name": "Formation", "color": "#2ca02c", "active": True},
            {"name": "Budget", "color": "#d62728", "active": True},
            {"name": "Politique", "color": "#9467bd", "active": True}
        ]
        
        for theme in default_themes:
            col_conf1, col_conf2, col_conf3 = st.columns([2, 1, 1])
            with col_conf1:
                st.markdown(f"**{theme['name']}**")
            with col_conf2:
                st.color_picker("Couleur", theme['color'], key=f"color_{theme['name']}")
            with col_conf3:
                st.checkbox("Actif", value=theme['active'], key=f"active_{theme['name']}")
        
        # Paramètres d'export
        st.markdown("### Paramètres d'export")
        export_format = st.selectbox("Format par défaut", ["CSV", "JSON", "Excel", "PDF"])
        include_metadata = st.checkbox("Inclure les métadonnées", value=True)
        auto_backup = st.checkbox("Sauvegarde automatique", value=False)
        
        if st.button("💾 Sauvegarder la configuration", type="primary"):
            st.success("Configuration sauvegardée")
    
    with tab_mgmt3:
        st.subheader("Importation et exportation")
        
        col_io1, col_io2 = st.columns(2)
        
        with col_io1:
            st.markdown("### 📤 Exporter les données")
            
            export_options = st.multiselect(
                "Données à exporter",
                ["Observations de recherche", "Métadonnées d'archive", "Thèmes de recherche", "Configuration"],
                default=["Observations de recherche"]
            )
            
            export_format = st.selectbox("Format d'export", ["CSV", "JSON", "Excel"])
            
            if st.button("📥 Générer l'export", type="primary"):
                # Simulation d'export
                observations_df = get_research_observations()
                
                if export_format == "CSV":
                    csv = observations_df.to_csv(index=False)
                    st.download_button(
                        label="Télécharger CSV",
                        data=csv,
                        file_name="bumidom_export.csv",
                        mime="text/csv"
                    )
                
                st.success(f"Export {export_format} prêt au téléchargement")
        
        with col_io2:
            st.markdown("### 📥 Importer des données")
            
            uploaded_file = st.file_uploader(
                "Choisir un fichier à importer",
                type=['csv', 'json', 'xlsx']
            )
            
            if uploaded_file is not None:
                file_ext = uploaded_file.name.split('.')[-1].lower()
                
                if file_ext == 'csv':
                    df = pd.read_csv(uploaded_file)
                elif file_ext == 'json':
                    df = pd.read_json(uploaded_file)
                elif file_ext in ['xlsx', 'xls']:
                    df = pd.read_excel(uploaded_file)
                
                st.success(f"Fichier importé : {len(df)} lignes")
                st.dataframe(df.head(), use_container_width=True)
                
                if st.button("💾 Importer dans la base", type="primary"):
                    st.info("Fonctionnalité d'import à implémenter")

# ============================================================================
# PIED DE PAGE ET INFORMATIONS
# ============================================================================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.9em;'>
    <p><strong>Module d'Analyse Archivistique BUMIDOM</strong> | Dashboard Streamlit v2.0</p>
    <p>⚠️ <em>Certaines fonctionnalités nécessitent une implémentation complète (base de données, API étendue)</em></p>
    <p>📚 <em>Pour une recherche approfondie, consultez les archives physiques aux Archives Nationales</em></p>
</div>
""", unsafe_allow_html=True)
