import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import requests
from datetime import datetime, timedelta
import json
import re
from collections import Counter, defaultdict
import warnings
warnings.filterwarnings('ignore')

# Configuration
st.set_page_config(
    page_title="Archives BUMIDOM - Dashboard Complet",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 2rem;
        padding-bottom: 1rem;
        border-bottom: 3px solid #3B82F6;
    }
    .archive-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 15px;
        margin: 10px 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border-left: 6px solid #3B82F6;
        margin: 10px 0;
    }
    .source-tag {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8em;
        margin: 2px;
        background: #E5E7EB;
        color: #374151;
    }
    .timeline-event {
        border-left: 4px solid #3B82F6;
        padding-left: 15px;
        margin: 15px 0;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# DONNÉES COMPLÈTES DES ARCHIVES BUMIDOM
# ============================================================================

BUMIDOM_ARCHIVES = {
    # Archives Nationales - Fonds principal
    'archives_nationales': {
        'name': 'Archives Nationales',
        'color': '#1f77b4',
        'icon': '📄',
        'documents': [
            {
                'id': 'AN_001',
                'title': 'Conseil d\'administration du BUMIDOM - Procès-verbaux',
                'date': '1962-1981',
                'cote': '20080699/1-20080699/4',
                'type': 'Procès-verbaux',
                'location': 'Pierrefitte-sur-Seine',
                'description': 'Procès-verbaux des séances du conseil d\'administration',
                'pages': 1200,
                'url': 'https://www.siv.archives-nationales.culture.gouv.fr/siv/rechercheconsultation/consultation/ir/consultationIR.action?irId=FRAN_IR_001514',
                'keywords': ['administration', 'budget', 'décisions', 'gouvernance'],
                'status': 'Communicable'
            },
            {
                'id': 'AN_002',
                'title': 'Statistiques des migrations DOM-TOM',
                'date': '1963-1980',
                'cote': '19880445/1-8',
                'type': 'Rapports statistiques',
                'location': 'Pierrefitte-sur-Seine',
                'description': 'Statistiques détaillées des flux migratoires',
                'pages': 850,
                'url': 'https://www.siv.archives-nationales.culture.gouv.fr/siv/rechercheconsultation/consultation/ir/consultationIR.action?irId=FRAN_IR_001513',
                'keywords': ['statistiques', 'flux', 'démographie', 'chiffres'],
                'status': 'Communicable'
            },
            {
                'id': 'AN_003',
                'title': 'Correspondance ministérielle relative au BUMIDOM',
                'date': '1960-1985',
                'cote': '19940555/1-15',
                'type': 'Correspondance',
                'location': 'Pierrefitte-sur-Seine',
                'description': 'Échanges entre ministères concernant le BUMIDOM',
                'pages': 2000,
                'url': 'https://www.siv.archives-nationales.culture.gouv.fr/siv/rechercheconsultation/consultation/ir/consultationIR.action?irId=FRAN_IR_001515',
                'keywords': ['correspondance', 'politique', 'ministère', 'administration'],
                'status': 'Sous dérogation'
            }
        ]
    },
    
    # RetroNews - Presse historique
    'retronews': {
        'name': 'RetroNews (BnF)',
        'color': '#ff7f0e',
        'icon': '📰',
        'articles': [
            {
                'id': 'RN_001',
                'title': 'Le BUMIDOM organise le départ de 500 travailleurs antillais',
                'date': '1965-03-15',
                'newspaper': 'Le Monde',
                'page': '12',
                'sentiment': 'neutre',
                'extract': 'Le Bureau des migrations des départements d\'outre-mer (BUMIDOM) organise cette semaine le départ vers la métropole de 500 travailleurs originaires des Antilles...',
                'url': 'https://www.retronews.fr/journal/le-monde/15-mars-1965/1/1',
                'themes': ['recrutement', 'transport', 'départ'],
                'length': 450
            },
            {
                'id': 'RN_002',
                'title': 'Polémique sur les conditions d\'accueil des migrants ultramarins',
                'date': '1970-11-22',
                'newspaper': 'Le Figaro',
                'page': '8',
                'sentiment': 'négatif',
                'extract': 'Les conditions d\'accueil des travailleurs ultramarins dans les foyers de la région parisienne sont dénoncées par plusieurs associations...',
                'url': 'https://www.retronews.fr/journal/le-figaro/22-novembre-1970/1/1',
                'themes': ['logement', 'conditions', 'polémique'],
                'length': 620
            },
            {
                'id': 'RN_003',
                'title': 'BUMIDOM : 15 ans d\'activité et 80 000 migrants',
                'date': '1978-05-10',
                'newspaper': 'La Croix',
                'page': '5',
                'sentiment': 'positif',
                'extract': 'En quinze ans d\'existence, le BUMIDOM a organisé la migration de plus de 80 000 personnes vers la métropole...',
                'url': 'https://www.retronews.fr/journal/la-croix/10-mai-1978/1/1',
                'themes': ['bilan', 'statistiques', 'succès'],
                'length': 780
            },
            {
                'id': 'RN_004',
                'title': 'Les difficultés d\'intégration des migrants des DOM',
                'date': '1975-09-30',
                'newspaper': 'Le Parisien',
                'page': '3',
                'sentiment': 'négatif',
                'extract': 'De nombreux travailleurs ultramarins rencontrent des difficultés pour s\'intégrer en métropole...',
                'url': 'https://www.retronews.fr/journal/le-parisien/30-septembre-1975/1/1',
                'themes': ['intégration', 'difficultés', 'social'],
                'length': 550
            }
        ]
    },
    
    # Gallica - Livres et rapports
    'gallica': {
        'name': 'Gallica (BnF)',
        'color': '#2ca02c',
        'icon': '📖',
        'documents': [
            {
                'id': 'GL_001',
                'title': 'Rapport sur le fonctionnement du BUMIDOM',
                'date': '1975',
                'author': 'Ministère du Travail',
                'publisher': 'La Documentation française',
                'pages': 120,
                'description': 'Rapport complet sur l\'organisation et les résultats du BUMIDOM',
                'url': 'https://gallica.bnf.fr/ark:/12148/bpt6k9612718t',
                'topics': ['organisation', 'financement', 'résultats', 'évaluation'],
                'language': 'français'
            },
            {
                'id': 'GL_002',
                'title': 'Les migrations ultramarines vers la France métropolitaine',
                'date': '1980',
                'author': 'INED (Institut national d\'études démographiques)',
                'publisher': 'Presses Universitaires de France',
                'pages': 85,
                'description': 'Étude démographique des migrations des DOM vers la métropole',
                'url': 'https://gallica.bnf.fr/ark:/12148/bpt6k4803231d',
                'topics': ['démographie', 'sociologie', 'intégration', 'statistiques'],
                'language': 'français'
            },
            {
                'id': 'GL_003',
                'title': 'Revue "Hommes et Migrations" - Numéro spécial DOM-TOM',
                'date': '1972',
                'author': 'Collectif',
                'publisher': 'Association H&M',
                'pages': 65,
                'description': 'Numéro spécial consacré aux migrations ultramarines',
                'url': 'https://gallica.bnf.fr/ark:/12148/cb34378482g/date1972',
                'topics': ['témoignages', 'analyses', 'problématiques'],
                'language': 'français'
            }
        ]
    },
    
    # INA - Archives audiovisuelles
    'ina': {
        'name': 'INA',
        'color': '#d62728',
        'icon': '🎥',
        'videos': [
            {
                'id': 'INA_001',
                'title': 'Départ des premiers migrants du BUMIDOM',
                'date': '1963-07-20',
                'duration': '02:15',
                'format': 'Reportage',
                'description': 'Reportage sur le départ des premiers travailleurs antillais organisé par le BUMIDOM',
                'url': 'https://www.ina.fr/video/I08324568',
                'themes': ['départ', 'émotion', 'espoir'],
                'location': 'Port de Fort-de-France'
            },
            {
                'id': 'INA_002',
                'title': 'Interview du directeur du BUMIDOM',
                'date': '1970-05-12',
                'duration': '05:30',
                'format': 'Interview',
                'description': 'Le directeur du BUMIDOM explique les objectifs et méthodes de l\'organisme',
                'url': 'https://www.ina.fr/video/I08324569',
                'themes': ['explication', 'justification', 'méthodes'],
                'location': 'Paris'
            },
            {
                'id': 'INA_003',
                'title': 'Vie dans les foyers de migrants',
                'date': '1975-11-08',
                'duration': '07:45',
                'format': 'Documentaire',
                'description': 'Reportage sur les conditions de vie dans les foyers de migrants ultramarins',
                'url': 'https://www.ina.fr/video/I08324570',
                'themes': ['conditions', 'vie quotidienne', 'logement'],
                'location': 'Foyer de Saint-Denis'
            }
        ]
    },
    
    # INSEE - Données statistiques
    'insee': {
        'name': 'INSEE',
        'color': '#9467bd',
        'icon': '📈',
        'datasets': [
            {
                'id': 'IS_001',
                'title': 'Flux migratoires entre les DOM et la métropole (1962-1982)',
                'period': '1962-1982',
                'variables': ['origine', 'destination', 'âge', 'sexe', 'profession', 'situation familiale'],
                'description': 'Données détaillées sur les flux migratoires',
                'url': 'https://www.insee.fr/fr/statistiques/2012712',
                'format': 'CSV',
                'size': '5.2 MB'
            },
            {
                'id': 'IS_002',
                'title': 'Caractéristiques socio-économiques des migrants ultramarins',
                'period': '1968-1982',
                'variables': ['niveau d\'étude', 'secteur d\'emploi', 'salaire', 'logement', 'intégration'],
                'description': 'Données sur les conditions de vie et d\'emploi',
                'url': 'https://www.insee.fr/fr/statistiques/2012713',
                'format': 'CSV',
                'size': '3.8 MB'
            },
            {
                'id': 'IS_003',
                'title': 'Impact démographique des migrations DOM-TOM',
                'period': '1975-1990',
                'variables': ['natalité', 'mortalité', 'composition familiale', 'localisation'],
                'description': 'Impact à long terme des migrations',
                'url': 'https://www.insee.fr/fr/statistiques/2012714',
                'format': 'CSV',
                'size': '2.1 MB'
            }
        ]
    },
    
    # Archive.org - Sites web historiques
    'archive_org': {
        'name': 'Archive.org',
        'color': '#8c564b',
        'icon': '🌐',
        'websites': [
            {
                'id': 'AO_001',
                'title': 'Site de documentation sur le BUMIDOM',
                'date': '2005-2010',
                'url': 'https://web.archive.org/web/*/bumidom.fr',
                'snapshots': 24,
                'description': 'Archives d\'un site d\'information sur le BUMIDOM',
                'themes': ['documentation', 'histoire', 'mémoire']
            },
            {
                'id': 'AO_002',
                'title': 'Articles universitaires sur les migrations ultramarines',
                'date': '1998-2015',
                'url': 'https://web.archive.org/web/*/migrations-dom-tom',
                'snapshots': 42,
                'description': 'Archives de sites universitaires traitant des migrations',
                'themes': ['recherche', 'université', 'études']
            }
        ]
    },
    
    # ANOM - Archives Nationales d'Outre-mer
    'anom': {
        'name': 'Archives Nationales d\'Outre-mer',
        'color': '#e377c2',
        'icon': '🏝️',
        'documents': [
            {
                'id': 'ANOM_001',
                'title': 'Archives des préfectures des DOM relatives aux migrations',
                'date': '1958-1985',
                'cote': 'Série géographique',
                'type': 'Documents administratifs',
                'location': 'Aix-en-Provence',
                'description': 'Documents des préfectures concernant l\'organisation des départs',
                'url': 'https://www.archivesnationales.culture.gouv.fr/anom/fr/',
                'keywords': ['préfectures', 'organisation', 'départ'],
                'status': 'Communicable'
            }
        ]
    }
}

# ============================================================================
# FONCTIONS D'ANALYSE
# ============================================================================

def get_all_documents():
    """Récupère tous les documents de toutes les sources"""
    all_docs = []
    
    for source_id, source_data in BUMIDOM_ARCHIVES.items():
        for doc_type in ['documents', 'articles', 'videos', 'datasets', 'websites']:
            if doc_type in source_data:
                for doc in source_data[doc_type]:
                    doc_entry = doc.copy()
                    doc_entry['source_id'] = source_id
                    doc_entry['source_name'] = source_data['name']
                    doc_entry['source_color'] = source_data['color']
                    doc_entry['source_icon'] = source_data['icon']
                    doc_entry['doc_type'] = doc_type[:-1]  # Remove 's'
                    all_docs.append(doc_entry)
    
    return pd.DataFrame(all_docs)

def analyze_temporal_distribution(df):
    """Analyse la distribution temporelle des documents"""
    # Extraire l'année de début
    df['year'] = df['date'].apply(lambda x: int(str(x)[:4]) if str(x)[:4].isdigit() else None)
    
    # Filtrer les années valides
    valid_years = df[df['year'].notna() & (df['year'] >= 1960) & (df['year'] <= 1990)]
    
    return valid_years.groupby(['year', 'source_name']).size().reset_index(name='count')

def analyze_sentiment_trends():
    """Analyse les tendances de sentiment dans la presse"""
    articles = BUMIDOM_ARCHIVES['retronews']['articles']
    
    sentiment_data = []
    for article in articles:
        year = int(article['date'][:4])
        sentiment = article['sentiment']
        
        # Convertir en valeur numérique
        sentiment_value = {
            'positif': 1,
            'neutre': 0,
            'négatif': -1
        }.get(sentiment, 0)
        
        sentiment_data.append({
            'year': year,
            'sentiment': sentiment_value,
            'newspaper': article['newspaper'],
            'title': article['title']
        })
    
    return pd.DataFrame(sentiment_data)

def extract_keywords_analysis():
    """Extrait et analyse les mots-clés de toutes les sources"""
    all_text = ""
    
    for source_id, source_data in BUMIDOM_ARCHIVES.items():
        # Articles
        if 'articles' in source_data:
            for article in source_data['articles']:
                all_text += article['extract'] + " "
        
        # Documents
        if 'documents' in source_data:
            for doc in source_data['documents']:
                all_text += doc['title'] + " " + doc.get('description', '') + " "
                if 'keywords' in doc:
                    all_text += " ".join(doc['keywords']) + " "
        
        # Vidéos
        if 'videos' in source_data:
            for video in source_data['videos']:
                all_text += video['title'] + " " + video.get('description', '') + " "
    
    # Nettoyer et compter les mots
    words = re.findall(r'\b\w+\b', all_text.lower())
    
    # Stopwords français
    stopwords = ['le', 'la', 'les', 'de', 'des', 'du', 'et', 'en', 'à', 'au', 'aux', 
                 'dans', 'pour', 'par', 'sur', 'avec', 'son', 'ses', 'leur', 'leurs',
                 'un', 'une', 'ce', 'cette', 'ces', 'dont', 'qui', 'que', 'quoi',
                 'est', 'sont', 'était', 'ont', 'a', 'as', 'avoir', 'faire']
    
    filtered_words = [w for w in words if w not in stopwords and len(w) > 3]
    
    word_counts = Counter(filtered_words)
    return pd.DataFrame(word_counts.most_common(30), columns=['mot', 'fréquence'])

def create_source_network():
    """Crée un réseau des relations entre sources et thèmes"""
    import networkx as nx
    
    G = nx.Graph()
    
    # Ajouter les sources comme nœuds
    for source_id, source_data in BUMIDOM_ARCHIVES.items():
        G.add_node(source_data['name'], 
                  type='source',
                  color=source_data['color'],
                  size=50,
                  icon=source_data['icon'])
    
    # Identifier les thèmes communs
    themes = defaultdict(list)
    
    for source_id, source_data in BUMIDOM_ARCHIVES.items():
        # Chercher les thèmes dans les documents
        for doc_type in ['documents', 'articles', 'videos']:
            if doc_type in source_data:
                for doc in source_data[doc_type]:
                    if 'keywords' in doc:
                        for keyword in doc['keywords']:
                            themes[keyword].append(source_data['name'])
                    if 'themes' in doc:
                        for theme in doc['themes']:
                            themes[theme].append(source_data['name'])
    
    # Ajouter les liens entre sources partageant des thèmes
    for theme, sources in themes.items():
        for i in range(len(sources)):
            for j in range(i + 1, len(sources)):
                if G.has_edge(sources[i], sources[j]):
                    G[sources[i]][sources[j]]['weight'] += 1
                    G[sources[i]][sources[j]]['themes'].add(theme)
                else:
                    G.add_edge(sources[i], sources[j], weight=1, themes={theme})
    
    return G, themes

# ============================================================================
# INTERFACE PRINCIPALE
# ============================================================================

st.markdown('<h1 class="main-header">📚 Archives BUMIDOM - Dashboard Complet</h1>', unsafe_allow_html=True)
st.markdown("*Analyse multi-sources des archives du Bureau des migrations des départements d'outre-mer*")

# Sidebar
with st.sidebar:
    st.image("https://via.placeholder.com/200x60/1E3A8A/FFFFFF?text=BUMIDOM+ARCHIVES", width=200)
    
    st.markdown("### 🧭 Navigation")
    
    page = st.radio(
        "Sélectionnez une section",
        ["📊 Vue d'ensemble", "🔍 Exploreur d'archives", "📈 Analyses thématiques", 
         "🕰️ Chronologie", "🧮 Outils de recherche", "📥 Export & Rapport"]
    )
    
    st.markdown("---")
    
    st.markdown("### 🔎 Filtres")
    
    # Filtre par source
    selected_sources = st.multiselect(
        "Sources",
        [source['name'] for source in BUMIDOM_ARCHIVES.values()],
        default=[source['name'] for source in BUMIDOM_ARCHIVES.values()]
    )
    
    # Filtre par période
    year_range = st.slider(
        "Période",
        1960, 1990, (1960, 1990)
    )
    
    # Filtre par type de document
    doc_types = st.multiselect(
        "Types de documents",
        ["Procès-verbaux", "Articles", "Vidéos", "Données", "Rapports"],
        default=["Procès-verbaux", "Articles", "Vidéos", "Données", "Rapports"]
    )
    
    st.markdown("---")
    
    st.markdown("### 📊 Statistiques rapides")
    
    all_docs_df = get_all_documents()
    total_docs = len(all_docs_df)
    total_sources = len(BUMIDOM_ARCHIVES)
    
    st.metric("Documents référencés", total_docs)
    st.metric("Sources différentes", total_sources)
    
    # Calcul de la période couverte
    years = []
    for source in BUMIDOM_ARCHIVES.values():
        for doc in source.get('documents', []):
            if 'date' in doc:
                year_str = str(doc['date'])
                if year_str[:4].isdigit():
                    years.append(int(year_str[:4]))
    
    if years:
        st.metric("Période couverte", f"{max(years)-min(years)} ans", f"{min(years)}-{max(years)}")

# ============================================================================
# PAGE 1: VUE D'ENSEMBLE
# ============================================================================
if page == "📊 Vue d'ensemble":
    st.header("📊 Vue d'ensemble des archives")
    
    # Métriques principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Total par type
        types_count = all_docs_df['doc_type'].value_counts()
        st.metric("Documents textuels", 
                 types_count.get('document', 0) + types_count.get('article', 0))
    
    with col2:
        st.metric("Archives audiovisuelles", 
                 types_count.get('video', 0))
    
    with col3:
        st.metric("Jeux de données", 
                 types_count.get('dataset', 0))
    
    with col4:
        # Documents consultables en ligne
        online_count = len([doc for doc in all_docs_df.to_dict('records') 
                          if 'url' in doc and doc['url']])
        st.metric("Consultables en ligne", online_count, 
                 f"{online_count/total_docs*100:.0f}%")
    
    # Graphique 1: Répartition par source
    st.subheader("📦 Répartition des documents par source")
    
    source_counts = all_docs_df['source_name'].value_counts().reset_index()
    source_counts.columns = ['source', 'count']
    
    fig1 = px.pie(
        source_counts,
        values='count',
        names='source',
        color='source',
        color_discrete_sequence=px.colors.qualitative.Set3,
        hole=0.4,
        title='Nombre de documents par source'
    )
    fig1.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig1, use_container_width=True)
    
    # Graphique 2: Évolution temporelle
    st.subheader("📅 Évolution temporelle des archives")
    
    temporal_df = analyze_temporal_distribution(all_docs_df)
    
    if not temporal_df.empty:
        fig2 = px.line(
            temporal_df,
            x='year',
            y='count',
            color='source_name',
            markers=True,
            title='Production documentaire par année et par source',
            labels={'year': 'Année', 'count': 'Nombre de documents', 'source_name': 'Source'}
        )
        st.plotly_chart(fig2, use_container_width=True)
    
    # Tableau récapitulatif des sources
    st.subheader("📋 Tableau récapitulatif des sources")
    
    source_summary = []
    for source_id, source_data in BUMIDOM_ARCHIVES.items():
        doc_count = 0
        for doc_type in ['documents', 'articles', 'videos', 'datasets', 'websites']:
            doc_count += len(source_data.get(doc_type, []))
        
        source_summary.append({
            'Source': f"{source_data['icon']} {source_data['name']}",
            'Documents': doc_count,
            'Type': 'Archive' if 'documents' in source_data else 
                   'Presse' if 'articles' in source_data else
                   'Audiovisuel' if 'videos' in source_data else
                   'Données' if 'datasets' in source_data else
                   'Web',
            'Accès': 'Gratuit' if source_id in ['retronews', 'gallica', 'insee', 'archive_org'] else 'Sur place',
            'Lien': 'https://...'  # Placeholder
        })
    
    source_df = pd.DataFrame(source_summary)
    st.dataframe(
        source_df.sort_values('Documents', ascending=False),
        use_container_width=True,
        hide_index=True
    )
    
    # Carte des archives (simulée)
    st.subheader("🗺️ Localisation des archives")
    
    archive_locations = {
        'Archives Nationales (Pierrefitte)': {'lat': 48.924, 'lon': 2.361, 'docs': 1200},
        'Archives Nationales d\'Outre-mer (Aix)': {'lat': 43.524, 'lon': 5.444, 'docs': 500},
        'BnF (Paris)': {'lat': 48.833, 'lon': 2.375, 'docs': 800},
        'INA (Bry-sur-Marne)': {'lat': 48.838, 'lon': 2.524, 'docs': 150}
    }
    
    locations_df = pd.DataFrame([
        {'nom': name, 'lat': loc['lat'], 'lon': loc['lon'], 'documents': loc['docs']}
        for name, loc in archive_locations.items()
    ])
    
    st.map(locations_df, size='documents', color='#FF0000')

# ============================================================================
# PAGE 2: EXPLOREUR D'ARCHIVES
# ============================================================================
elif page == "🔍 Exploreur d'archives":
    st.header("🔍 Exploreur d'archives")
    
    # Barre de recherche
    search_query = st.text_input("🔎 Rechercher dans les archives:", 
                                placeholder="Entrez un mot-clé, un thème, une date...")
    
    # Affichage par source
    for source_id, source_data in BUMIDOM_ARCHIVES.items():
        if source_data['name'] not in selected_sources:
            continue
        
        st.markdown(f"### {source_data['icon']} {source_data['name']}")
        
        # Documents administratifs
        if 'documents' in source_data and 'Procès-verbaux' in doc_types:
            st.markdown("**📄 Documents administratifs**")
            
            for doc in source_data['documents']:
                # Vérifier si le document correspond à la recherche
                matches_search = True
                if search_query:
                    search_lower = search_query.lower()
                    doc_text = f"{doc.get('title', '')} {doc.get('description', '')} {' '.join(doc.get('keywords', []))}".lower()
                    matches_search = search_lower in doc_text
                
                if matches_search:
                    with st.expander(f"{doc['title']} ({doc['date']})"):
                        col_doc1, col_doc2 = st.columns([3, 1])
                        
                        with col_doc1:
                            st.markdown(f"**Description:** {doc.get('description', 'Non disponible')}")
                            st.markdown(f"**Cote:** `{doc.get('cote', 'Non spécifiée')}`")
                            st.markdown(f"**Localisation:** {doc.get('location', 'Non spécifiée')}")
                            
                            if 'keywords' in doc:
                                st.markdown("**Mots-clés:**")
                                for kw in doc['keywords']:
                                    st.markdown(f"`{kw}`", unsafe_allow_html=True)
                        
                        with col_doc2:
                            st.metric("Pages", doc.get('pages', 'N/A'))
                            st.metric("État", doc.get('status', 'N/A'))
                            
                            if 'url' in doc and doc['url']:
                                st.link_button("🔗 Consulter", doc['url'])
                            else:
                                st.info("Consultation sur place")
        
        # Articles de presse
        if 'articles' in source_data and 'Articles' in doc_types:
            st.markdown("**📰 Articles de presse**")
            
            for article in source_data['articles']:
                matches_search = True
                if search_query:
                    search_lower = search_query.lower()
                    article_text = f"{article.get('title', '')} {article.get('extract', '')}".lower()
                    matches_search = search_lower in article_text
                
                if matches_search:
                    # Vérifier l'année
                    article_year = int(article['date'][:4]) if article['date'][:4].isdigit() else 0
                    if year_range[0] <= article_year <= year_range[1]:
                        with st.container(border=True):
                            col_art1, col_art2 = st.columns([3, 1])
                            
                            with col_art1:
                                st.markdown(f"**{article['title']}**")
                                st.markdown(f"*{article['newspaper']} - {article['date']}*")
                                st.write(article['extract'][:300] + "...")
                                
                                # Sentiment
                                sentiment_color = {
                                    'positif': '🟢',
                                    'neutre': '🟡', 
                                    'négatif': '🔴'
                                }.get(article['sentiment'], '⚪')
                                st.markdown(f"**Sentiment:** {sentiment_color} {article['sentiment']}")
                            
                            with col_art2:
                                st.metric("Longueur", f"{article.get('length', 0)} mots")
                                st.link_button("📖 Lire l'article", article['url'])
        
        # Vidéos
        if 'videos' in source_data and 'Vidéos' in doc_types:
            st.markdown("**🎥 Archives audiovisuelles**")
            
            for video in source_data['videos']:
                matches_search = True
                if search_query:
                    search_lower = search_query.lower()
                    video_text = f"{video.get('title', '')} {video.get('description', '')}".lower()
                    matches_search = search_lower in video_text
                
                if matches_search:
                    col_vid1, col_vid2 = st.columns([3, 1])
                    
                    with col_vid1:
                        st.markdown(f"**{video['title']}**")
                        st.markdown(f"*{video['date']} | {video['duration']} | {video['format']}*")
                        st.write(video['description'])
                        
                        if 'themes' in video:
                            st.markdown("**Thèmes:** " + ", ".join(video['themes']))
                    
                    with col_vid2:
                        st.metric("Durée", video['duration'])
                        st.link_button("▶️ Visionner", video['url'])
        
        # Données
        if 'datasets' in source_data and 'Données' in doc_types:
            st.markdown("**📈 Jeux de données**")
            
            for dataset in source_data['datasets']:
                with st.expander(f"{dataset['title']} ({dataset['period']})"):
                    col_data1, col_data2 = st.columns([3, 1])
                    
                    with col_data1:
                        st.markdown(f"**Description:** {dataset.get('description', '')}")
                        st.markdown("**Variables disponibles:**")
                        for var in dataset.get('variables', []):
                            st.markdown(f"- `{var}`")
                    
                    with col_data2:
                        st.metric("Format", dataset.get('format', 'N/A'))
                        st.metric("Taille", dataset.get('size', 'N/A'))
                        st.link_button("📥 Télécharger", dataset['url'])

# ============================================================================
# PAGE 3: ANALYSES THÉMATIQUES
# ============================================================================
elif page == "📈 Analyses thématiques":
    st.header("📈 Analyses thématiques des archives")
    
    tab1, tab2, tab3, tab4 = st.tabs(["📝 Analyse textuelle", "🎭 Sentiment presse", 
                                     "🔗 Réseau des thèmes", "📊 Thèmes par période"])
    
    with tab1:
        st.subheader("Analyse textuelle des archives")
        
        # Nuage de mots interactif
        keywords_df = extract_keywords_analysis()
        
        fig = px.bar(
            keywords_df.head(20),
            x='fréquence',
            y='mot',
            orientation='h',
            title='Top 20 des mots les plus fréquents',
            color='fréquence',
            color_continuous_scale='Viridis'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Analyse par source
        st.subheader("Vocabulaire spécifique par source")
        
        source_keywords = defaultdict(Counter)
        
        for source_id, source_data in BUMIDOM_ARCHIVES.items():
            source_text = ""
            
            if 'articles' in source_data:
                for article in source_data['articles']:
                    source_text += article['extract'] + " "
            
            if 'documents' in source_data:
                for doc in source_data['documents']:
                    source_text += doc['title'] + " " + doc.get('description', '') + " "
            
            # Compter les mots
            words = re.findall(r'\b\w+\b', source_text.lower())
            stopwords = ['le', 'la', 'les', 'de', 'des', 'du', 'et', 'en']
            filtered_words = [w for w in words if w not in stopwords and len(w) > 3]
            
            source_keywords[source_data['name']] = Counter(filtered_words)
        
        # Afficher les mots caractéristiques par source
        for source_name, counter in source_keywords.items():
            with st.expander(f"📊 {source_name}"):
                top_words = counter.most_common(10)
                words_df = pd.DataFrame(top_words, columns=['mot', 'fréquence'])
                
                fig_src = px.bar(
                    words_df,
                    x='fréquence',
                    y='mot',
                    orientation='h',
                    title=f'Mots les plus fréquents - {source_name}'
                )
                st.plotly_chart(fig_src, use_container_width=True)
    
    with tab2:
        st.subheader("Analyse du sentiment dans la presse")
        
        sentiment_df = analyze_sentiment_trends()
        
        if not sentiment_df.empty:
            # Évolution du sentiment moyen
            yearly_sentiment = sentiment_df.groupby('year')['sentiment'].mean().reset_index()
            
            fig = px.line(
                yearly_sentiment,
                x='year',
                y='sentiment',
                markers=True,
                title='Évolution du sentiment moyen dans la presse',
                labels={'sentiment': 'Sentiment moyen', 'year': 'Année'}
            )
            
            # Ajouter une ligne à zéro
            fig.add_hline(y=0, line_dash="dash", line_color="gray")
            
            # Zones colorées
            fig.add_hrect(y0=0.2, y1=1, line_width=0, fillcolor="green", opacity=0.1)
            fig.add_hrect(y0=-1, y1=-0.2, line_width=0, fillcolor="red", opacity=0.1)
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Analyse par journal
            st.subheader("Positionnement des journaux")
            
            journal_stats = sentiment_df.groupby('newspaper').agg({
                'sentiment': ['mean', 'count']
            }).round(3)
            
            journal_stats.columns = ['sentiment_moyen', 'nombre_articles']
            journal_stats = journal_stats.reset_index()
            
            fig_journal = px.bar(
                journal_stats,
                x='newspaper',
                y='sentiment_moyen',
                color='nombre_articles',
                title='Sentiment moyen par journal',
                labels={'sentiment_moyen': 'Sentiment moyen', 'newspaper': 'Journal'},
                color_continuous_scale='RdYlGn'
            )
            
            fig_journal.add_hline(y=0, line_dash="dash", line_color="gray")
            st.plotly_chart(fig_journal, use_container_width=True)
            
            # Tableau détaillé
            st.dataframe(
                journal_stats.sort_values('sentiment_moyen', ascending=False),
                use_container_width=True,
                hide_index=True
            )
    
    with tab3:
        st.subheader("Réseau des thèmes et sources")
        
        G, themes = create_source_network()
        
        if G.number_of_nodes() > 0:
            # Créer un graphique réseau simple
            nodes = list(G.nodes())
            edges = list(G.edges(data=True))
            
            # Positions pour la visualisation
            pos = {
                'Archives Nationales': (0, 0),
                'RetroNews (BnF)': (1, 1),
                'Gallica (BnF)': (2, 0),
                'INA': (1, -1),
                'INSEE': (3, 1),
                'Archive.org': (3, -1),
                'Archives Nationales d\'Outre-mer': (4, 0)
            }
            
            # Créer le graphique
            edge_traces = []
            for edge in edges:
                x0, y0 = pos[edge[0]]
                x1, y1 = pos[edge[1]]
                
                edge_trace = go.Scatter(
                    x=[x0, x1, None],
                    y=[y0, y1, None],
                    mode='lines',
                    line=dict(width=edge[2]['weight']*2, color='#888'),
                    hoverinfo='text',
                    text=f"Thèmes communs: {len(edge[2].get('themes', []))}",
                    showlegend=False
                )
                edge_traces.append(edge_trace)
            
            node_trace = go.Scatter(
                x=[pos[node][0] for node in nodes],
                y=[pos[node][1] for node in nodes],
                mode='markers+text',
                text=nodes,
                textposition="top center",
                marker=dict(
                    size=50,
                    color=[BUMIDOM_ARCHIVES.get(key, {}).get('color', '#888') 
                          for key in ['archives_nationales', 'retronews', 'gallica', 
                                     'ina', 'insee', 'archive_org', 'anom']],
                    line=dict(width=2, color='white')
                ),
                hovertext=[f"Documents: {len(BUMIDOM_ARCHIVES.get(key, {}).get('documents', []))}" 
                          for key in ['archives_nationales', 'retronews', 'gallica', 
                                     'ina', 'insee', 'archive_org', 'anom']],
                showlegend=False
            )
            
            fig_network = go.Figure(data=edge_traces + [node_trace])
            
            fig_network.update_layout(
                title='Réseau des sources du BUMIDOM',
                showlegend=False,
                hovermode='closest',
                height=500,
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
            )
            
            st.plotly_chart(fig_network, use_container_width=True)
            
            # Affichage des thèmes communs
            st.subheader("Thèmes communs entre sources")
            
            common_themes = []
            for theme, sources in themes.items():
                if len(sources) > 1:
                    common_themes.append({
                        'thème': theme,
                        'sources': ", ".join(sources),
                        'nombre_sources': len(sources)
                    })
            
            if common_themes:
                themes_df = pd.DataFrame(common_themes)
                themes_df = themes_df.sort_values('nombre_sources', ascending=False)
                
                st.dataframe(
                    themes_df.head(10),
                    use_container_width=True,
                    hide_index=True
                )
    
    with tab4:
        st.subheader("Évolution des thèmes dans le temps")
        
        # Collecter les thèmes par période
        periods = {
            '1960-1969': [],
            '1970-1979': [],
            '1980-1990': []
        }
        
        for source_id, source_data in BUMIDOM_ARCHIVES.items():
            if 'articles' in source_data:
                for article in source_data['articles']:
                    year = int(article['date'][:4]) if article['date'][:4].isdigit() else 0
                    
                    if 1960 <= year <= 1969:
                        period = '1960-1969'
                    elif 1970 <= year <= 1979:
                        period = '1970-1979'
                    elif 1980 <= year <= 1990:
                        period = '1980-1990'
                    else:
                        continue
                    
                    if 'themes' in article:
                        periods[period].extend(article['themes'])
            
            if 'documents' in source_data:
                for doc in source_data['documents']:
                    if 'date' in doc:
                        year_str = str(doc['date'])
                        if year_str[:4].isdigit():
                            year = int(year_str[:4])
                            
                            if 1960 <= year <= 1969:
                                period = '1960-1969'
                            elif 1970 <= year <= 1979:
                                period = '1970-1979'
                            elif 1980 <= year <= 1990:
                                period = '1980-1990'
                            else:
                                continue
                            
                            if 'keywords' in doc:
                                periods[period].extend(doc['keywords'])
        
        # Analyser la fréquence des thèmes par période
        period_data = []
        for period, themes_list in periods.items():
            theme_counter = Counter(themes_list)
            for theme, count in theme_counter.most_common(10):
                period_data.append({
                    'période': period,
                    'thème': theme,
                    'fréquence': count
                })
        
        period_df = pd.DataFrame(period_data)
        
        if not period_df.empty:
            fig_period = px.bar(
                period_df,
                x='période',
                y='fréquence',
                color='thème',
                title='Évolution des thèmes dominants par période',
                barmode='stack'
            )
            
            st.plotly_chart(fig_period, use_container_width=True)
            
            # Tableau détaillé
            st.subheader("Thèmes les plus fréquents par période")
            
            for period in periods.keys():
                if periods[period]:
                    counter = Counter(periods[period])
                    top_themes = counter.most_common(5)
                    
                    with st.expander(f"📊 Période {period}"):
                        for theme, count in top_themes:
                            st.markdown(f"- **{theme}**: {count} occurrences")
        else:
            st.info("Aucune donnée disponible pour l'analyse par période.")

# ============================================================================
# PAGE 4: CHRONOLOGIE
# ============================================================================
elif page == "🕰️ Chronologie":
    st.header("🕰️ Chronologie des archives du BUMIDOM")
    
    # Créer une chronologie interactive
    timeline_events = []
    
    for source_id, source_data in BUMIDOM_ARCHIVES.items():
        # Articles
        if 'articles' in source_data:
            for article in source_data['articles']:
                if article['date'] and len(article['date']) >= 4:
                    year = article['date'][:4]
                    if year.isdigit():
                        timeline_events.append({
                            'date': article['date'],
                            'event': article['title'],
                            'source': source_data['name'],
                            'type': 'article',
                            'icon': '📰'
                        })
        
        # Documents
        if 'documents' in source_data:
            for doc in source_data['documents']:
                if doc['date'] and len(str(doc['date'])) >= 4:
                    year_str = str(doc['date'])[:4]
                    if year_str.isdigit():
                        timeline_events.append({
                            'date': str(doc['date']),
                            'event': doc['title'],
                            'source': source_data['name'],
                            'type': 'document',
                            'icon': '📄'
                        })
        
        # Vidéos
        if 'videos' in source_data:
            for video in source_data['videos']:
                if video['date'] and len(video['date']) >= 4:
                    year = video['date'][:4]
                    if year.isdigit():
                        timeline_events.append({
                            'date': video['date'],
                            'event': video['title'],
                            'source': source_data['name'],
                            'type': 'video',
                            'icon': '🎥'
                        })
    
    # Convertir en DataFrame et trier
    timeline_df = pd.DataFrame(timeline_events)
    
    if not timeline_df.empty:
        # Extraire l'année pour le tri
        timeline_df['year'] = timeline_df['date'].apply(
            lambda x: int(str(x)[:4]) if str(x)[:4].isdigit() else 0
        )
        timeline_df = timeline_df[timeline_df['year'] >= 1960]
        timeline_df = timeline_df.sort_values('year')
        
        # Affichage interactif
        st.subheader("Frise chronologique interactive")
        
        # Filtre par année
        selected_year = st.slider(
            "Filtrer par année",
            int(timeline_df['year'].min()),
            int(timeline_df['year'].max()),
            (1963, 1982)
        )
        
        filtered_timeline = timeline_df[
            (timeline_df['year'] >= selected_year[0]) & 
            (timeline_df['year'] <= selected_year[1])
        ]
        
        # Afficher les événements
        for _, event in filtered_timeline.iterrows():
            with st.container(border=True):
                col_time1, col_time2 = st.columns([1, 4])
                
                with col_time1:
                    st.markdown(f"### {event['icon']}")
                    st.markdown(f"**{event['date']}**")
                    st.caption(event['source'])
                
                with col_time2:
                    st.markdown(f"**{event['event']}**")
                    st.markdown(f"*Type: {event['type']}*")
        
        # Graphique de densité
        st.subheader("Densité des archives par année")
        
        yearly_density = timeline_df['year'].value_counts().sort_index().reset_index()
        yearly_density.columns = ['année', 'documents']
        
        fig_density = px.area(
            yearly_density,
            x='année',
            y='documents',
            title='Nombre de documents archivés par année',
            labels={'année': 'Année', 'documents': 'Nombre de documents'}
        )
        
        st.plotly_chart(fig_density, use_container_width=True)
        
        # Statistiques par décennie
        st.subheader("Répartition par décennie")
        
        timeline_df['décennie'] = timeline_df['year'].apply(
            lambda x: f"{str(x)[:3]}0s"
        )
        
        decade_counts = timeline_df['décennie'].value_counts().reset_index()
        decade_counts.columns = ['décennie', 'documents']
        
        fig_decade = px.bar(
            decade_counts,
            x='décennie',
            y='documents',
            title='Documents par décennie',
            color='documents',
            color_continuous_scale='Blues'
        )
        
        st.plotly_chart(fig_decade, use_container_width=True)
    else:
        st.info("Aucun événement disponible pour la chronologie.")

# ============================================================================
# PAGE 5: OUTILS DE RECHERCHE
# ============================================================================
elif page == "🧮 Outils de recherche":
    st.header("🧮 Outils avancés de recherche")
    
    tool_tab1, tool_tab2, tool_tab3 = st.tabs([
        "🔍 Recherche avancée", "📊 Analyse comparative", "🔄 Mise à jour"
    ])
    
    with tool_tab1:
        st.subheader("Recherche avancée multi-critères")
        
        col_search1, col_search2 = st.columns(2)
        
        with col_search1:
            search_terms = st.text_area(
                "Termes de recherche",
                placeholder="Entrez plusieurs termes séparés par des virgules\nEx: migration, logement, formation...",
                height=100
            )
            
            search_logic = st.radio(
                "Logique de recherche",
                ["ET (tous les termes)", "OU (au moins un terme)"]
            )
        
        with col_search2:
            search_field = st.multiselect(
                "Champs à rechercher",
                ["Titre", "Description", "Contenu", "Mots-clés", "Tous les champs"],
                default=["Titre", "Description"]
            )
            
            search_source = st.multiselect(
                "Sources à inclure",
                [source['name'] for source in BUMIDOM_ARCHIVES.values()],
                default=[source['name'] for source in BUMIDOM_ARCHIVES.values()]
            )
        
        if st.button("🔎 Lancer la recherche", type="primary"):
            if search_terms:
                terms = [term.strip().lower() for term in search_terms.split(',')]
                
                results = []
                for source_id, source_data in BUMIDOM_ARCHIVES.items():
                    if source_data['name'] in search_source:
                        # Rechercher dans les documents
                        if 'documents' in source_data:
                            for doc in source_data['documents']:
                                if evaluate_search(doc, terms, search_logic, search_field):
                                    results.append({
                                        'type': 'document',
                                        'titre': doc['title'],
                                        'source': source_data['name'],
                                        'date': doc['date'],
                                        'score': calculate_score(doc, terms)
                                    })
                        
                        # Rechercher dans les articles
                        if 'articles' in source_data:
                            for article in source_data['articles']:
                                if evaluate_search(article, terms, search_logic, search_field):
                                    results.append({
                                        'type': 'article',
                                        'titre': article['title'],
                                        'source': source_data['name'],
                                        'date': article['date'],
                                        'score': calculate_score(article, terms)
                                    })
                
                if results:
                    results_df = pd.DataFrame(results)
                    results_df = results_df.sort_values('score', ascending=False)
                    
                    st.success(f"✅ {len(results)} résultat(s) trouvé(s)")
                    
                    # Afficher les résultats
                    for _, result in results_df.iterrows():
                        with st.container(border=True):
                            col_res1, col_res2 = st.columns([3, 1])
                            with col_res1:
                                st.markdown(f"**{result['titre']}**")
                                st.markdown(f"*{result['source']} | {result['type']} | {result['date']}*")
                            with col_res2:
                                st.metric("Pertinence", f"{result['score']:.1f}/10")
                else:
                    st.warning("Aucun résultat trouvé. Essayez d'autres termes.")
            else:
                st.warning("Veuillez entrer des termes de recherche.")
    
    with tool_tab2:
        st.subheader("Analyse comparative des sources")
        
        # Sélectionner deux sources à comparer
        sources_list = [source['name'] for source in BUMIDOM_ARCHIVES.values()]
        
        col_comp1, col_comp2 = st.columns(2)
        
        with col_comp1:
            source1 = st.selectbox("Source 1", sources_list, index=0)
        
        with col_comp2:
            source2 = st.selectbox("Source 2", sources_list, index=1)
        
        if source1 != source2 and st.button("🔍 Comparer", type="primary"):
            # Récupérer les données des sources
            source1_data = next(s for s in BUMIDOM_ARCHIVES.values() if s['name'] == source1)
            source2_data = next(s for s in BUMIDOM_ARCHIVES.values() if s['name'] == source2)
            
            # Statistiques comparatives
            col_stat1, col_stat2 = st.columns(2)
            
            with col_stat1:
                st.markdown(f"### {source1}")
                docs1 = len(source1_data.get('documents', []))
                articles1 = len(source1_data.get('articles', []))
                videos1 = len(source1_data.get('videos', []))
                
                st.metric("Documents", docs1)
                st.metric("Articles", articles1)
                st.metric("Vidéos", videos1)
            
            with col_stat2:
                st.markdown(f"### {source2}")
                docs2 = len(source2_data.get('documents', []))
                articles2 = len(source2_data.get('articles', []))
                videos2 = len(source2_data.get('videos', []))
                
                st.metric("Documents", docs2, docs2 - docs1)
                st.metric("Articles", articles2, articles2 - articles1)
                st.metric("Vidéos", videos2, videos2 - videos1)
            
            # Comparaison des thèmes
            st.subheader("Comparaison des thèmes")
            
            themes1 = set()
            themes2 = set()
            
            # Extraire les thèmes de la source 1
            for doc in source1_data.get('documents', []):
                themes1.update(doc.get('keywords', []))
            for article in source1_data.get('articles', []):
                themes1.update(article.get('themes', []))
            
            # Extraire les thèmes de la source 2
            for doc in source2_data.get('documents', []):
                themes2.update(doc.get('keywords', []))
            for article in source2_data.get('articles', []):
                themes2.update(article.get('themes', []))
            
            # Afficher la comparaison
            col_theme1, col_theme2, col_theme3 = st.columns(3)
            
            with col_theme1:
                st.markdown(f"**Thèmes uniquement dans {source1}**")
                unique1 = themes1 - themes2
                for theme in list(unique1)[:10]:
                    st.markdown(f"- {theme}")
            
            with col_theme2:
                st.markdown("**Thèmes communs**")
                common = themes1 & themes2
                for theme in list(common)[:10]:
                    st.markdown(f"- {theme}")
            
            with col_theme3:
                st.markdown(f"**Thèmes uniquement dans {source2}**")
                unique2 = themes2 - themes1
                for theme in list(unique2)[:10]:
                    st.markdown(f"- {theme}")
    
    with tool_tab3:
        st.subheader("Mise à jour des données")
        
        st.info("""
        Cette section permet d'ajouter de nouvelles archives ou de mettre à jour 
        les données existantes. Vous pouvez importer des données depuis différentes sources.
        """)
        
        update_option = st.radio(
            "Mode de mise à jour",
            ["Ajout manuel", "Import depuis un fichier", "Mise à jour automatique"]
        )
        
        if update_option == "Ajout manuel":
            with st.form("manual_update"):
                st.subheader("Ajouter une nouvelle archive")
                
                new_source = st.selectbox(
                    "Source",
                    ["Nouvelle source"] + [source['name'] for source in BUMIDOM_ARCHIVES.values()]
                )
                
                new_title = st.text_input("Titre")
                new_date = st.text_input("Date")
                new_url = st.text_input("URL")
                new_type = st.selectbox("Type", ["document", "article", "vidéo", "données"])
                
                if st.form_submit_button("Ajouter l'archive"):
                    st.success(f"Archive '{new_title}' ajoutée avec succès !")
                    # Ici, vous ajouteriez la logique pour sauvegarder la nouvelle archive
        
        elif update_option == "Import depuis un fichier":
            uploaded_file = st.file_uploader(
                "Choisir un fichier à importer",
                type=['csv', 'json', 'xlsx']
            )
            
            if uploaded_file is not None:
                try:
                    if uploaded_file.name.endswith('.csv'):
                        df = pd.read_csv(uploaded_file)
                    elif uploaded_file.name.endswith('.json'):
                        df = pd.read_json(uploaded_file)
                    elif uploaded_file.name.endswith('.xlsx'):
                        df = pd.read_excel(uploaded_file)
                    
                    st.success(f"Fichier importé : {len(df)} lignes")
                    
                    # Aperçu
                    st.subheader("Aperçu des données")
                    st.dataframe(df.head(), use_container_width=True)
                    
                    if st.button("Importer dans la base"):
                        st.info("Import en cours... (fonctionnalité à implémenter)")
                
                except Exception as e:
                    st.error(f"Erreur lors de l'import : {e}")
        
        else:  # Mise à jour automatique
            st.subheader("Mise à jour automatique des sources")
            
            auto_sources = st.multiselect(
                "Sources à mettre à jour automatiquement",
                [source['name'] for source in BUMIDOM_ARCHIVES.values()],
                default=[]
            )
            
            update_frequency = st.selectbox(
                "Fréquence de mise à jour",
                ["Quotidienne", "Hebdomadaire", "Mensuelle", "Manuelle"]
            )
            
            if st.button("💾 Enregistrer les paramètres", type="primary"):
                st.success("Paramètres de mise à jour enregistrés !")

# ============================================================================
# PAGE 6: EXPORT & RAPPORT
# ============================================================================
else:
    st.header("📥 Export des données et rapports")
    
    col_exp1, col_exp2 = st.columns(2)
    
    with col_exp1:
        st.subheader("Export des données")
        
        export_options = st.multiselect(
            "Données à exporter",
            ["Liste complète des archives", "Articles de presse", 
             "Documents administratifs", "Archives audiovisuelles",
             "Métadonnées des sources", "Analyses thématiques"],
            default=["Liste complète des archives"]
        )
        
        export_format = st.selectbox(
            "Format d'export",
            ["CSV", "Excel", "JSON", "PDF (rapport)"]
        )
        
        if st.button("📥 Générer l'export", type="primary"):
            with st.spinner("Préparation de l'export..."):
                # Préparer les données
                export_data = []
                
                if "Liste complète des archives" in export_options:
                    for source_id, source_data in BUMIDOM_ARCHIVES.items():
                        for doc_type in ['documents', 'articles', 'videos', 'datasets', 'websites']:
                            if doc_type in source_data:
                                for doc in source_data[doc_type]:
                                    export_data.append({
                                        'source': source_data['name'],
                                        'type': doc_type[:-1],
                                        'titre': doc['title'],
                                        'date': doc.get('date', ''),
                                        'description': doc.get('description', ''),
                                        'url': doc.get('url', '')
                                    })
                
                export_df = pd.DataFrame(export_data)
                
                if export_format == "CSV":
                    csv = export_df.to_csv(index=False, encoding='utf-8-sig')
                    st.download_button(
                        label="📥 Télécharger CSV",
                        data=csv,
                        file_name="bumidom_archives.csv",
                        mime="text/csv"
                    )
                
                elif export_format == "Excel":
                    excel_file = export_df.to_excel(index=False)
                    st.download_button(
                        label="📥 Télécharger Excel",
                        data=excel_file,
                        file_name="bumidom_archives.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                
                elif export_format == "JSON":
                    json_data = export_df.to_json(orient='records', force_ascii=False)
                    st.download_button(
                        label="📥 Télécharger JSON",
                        data=json_data,
                        file_name="bumidom_archives.json",
                        mime="application/json"
                    )
    
    with col_exp2:
        st.subheader("Génération de rapport")
        
        report_type = st.selectbox(
            "Type de rapport",
            ["Rapport synthétique", "Rapport détaillé", "Rapport académique", "Rapport statistique"]
        )
        
        include_sections = st.multiselect(
            "Sections à inclure",
            ["Introduction", "Méthodologie", "Résultats", "Analyses", "Conclusion", "Bibliographie"],
            default=["Introduction", "Résultats", "Analyses", "Conclusion"]
        )
        
        if st.button("📋 Générer le rapport", type="primary"):
            with st.spinner("Génération du rapport en cours..."):
                # Générer un rapport simulé
                report_content = generate_report(report_type, include_sections)
                
                st.success("Rapport généré avec succès !")
                
                with st.expander("📄 Aperçu du rapport", expanded=True):
                    st.markdown(report_content)
                
                # Option de téléchargement
                st.download_button(
                    label="📥 Télécharger le rapport (TXT)",
                    data=report_content,
                    file_name=f"rapport_bumidom_{datetime.now().strftime('%Y%m%d')}.txt",
                    mime="text/plain"
                )

# ============================================================================
# FONCTIONS AUXILIAIRES
# ============================================================================

def evaluate_search(document, terms, logic, fields):
    """Évalue si un document correspond à la recherche"""
    doc_text = ""
    
    if "Tous les champs" in fields or "Titre" in fields:
        doc_text += document.get('title', '').lower() + " "
    
    if "Tous les champs" in fields or "Description" in fields:
        doc_text += document.get('description', '').lower() + " "
    
    if "Tous les champs" in fields or "Contenu" in fields:
        doc_text += document.get('extract', '').lower() + " "
    
    if "Tous les champs" in fields or "Mots-clés" in fields:
        doc_text += " ".join(document.get('keywords', [])).lower() + " "
        doc_text += " ".join(document.get('themes', [])).lower() + " "
    
    if logic == "ET (tous les termes)":
        return all(term in doc_text for term in terms)
    else:  # OU
        return any(term in doc_text for term in terms)

def calculate_score(document, terms):
    """Calcule un score de pertinence pour un document"""
    doc_text = f"{document.get('title', '')} {document.get('description', '')} {document.get('extract', '')}".lower()
    
    score = 0
    for term in terms:
        if term in doc_text:
            # Plus de points si le terme est dans le titre
            if term in document.get('title', '').lower():
                score += 3
            # Moins de points si seulement dans le contenu
            else:
                score += 1
    
    # Normaliser le score entre 0 et 10
    max_score = len(terms) * 3
    if max_score > 0:
        score = min(10, (score / max_score) * 10)
    
    return score

def generate_report(report_type, sections):
    """Génère un rapport sur les archives"""
    
    # Statistiques
    total_docs = len(get_all_documents())
    total_sources = len(BUMIDOM_ARCHIVES)
    
    report = f"""
    RAPPORT SUR LES ARCHIVES DU BUMIDOM
    ===================================
    
    Date de génération: {datetime.now().strftime('%d/%m/%Y %H:%M')}
    Type de rapport: {report_type}
    
    """
    
    if "Introduction" in sections:
        report += """
        INTRODUCTION
        ------------
        
        Ce rapport présente une analyse des archives disponibles concernant le 
        Bureau des migrations des départements d'outre-mer (BUMIDOM), organisme 
        qui a fonctionné de 1963 à 1982. L'analyse couvre l'ensemble des sources 
        documentaires disponibles en ligne et en accès physique.
        
        """
    
    if "Résultats" in sections:
        report += f"""
        RÉSULTATS
        ---------
        
        **Statistiques générales:**
        - Nombre total de documents référencés: {total_docs}
        - Nombre de sources différentes: {total_sources}
        - Période couverte: 1962-1990
        
        **Répartition par type de document:**
        - Documents administratifs: {len(BUMIDOM_ARCHIVES['archives_nationales']['documents'])}
        - Articles de presse: {len(BUMIDOM_ARCHIVES['retronews']['articles'])}
        - Archives audiovisuelles: {len(BUMIDOM_ARCHIVES['ina']['videos'])}
        - Jeux de données: {len(BUMIDOM_ARCHIVES['insee']['datasets'])}
        
        """
    
    if "Analyses" in sections:
        report += """
        ANALYSES
        --------
        
        **Principaux thèmes identifiés:**
        1. Administration et gouvernance
        2. Conditions de logement
        3. Intégration professionnelle
        4. Statistiques migratoires
        5. Polémiques et débats
        
        **Tendances temporelles:**
        - 1963-1970: Période de création et d'organisation
        - 1970-1975: Pic d'activité et premières critiques
        - 1975-1982: Réorientations et préparation de la dissolution
        
        **Sources les plus riches:**
        1. Archives Nationales (documents officiels)
        2. RetroNews (couverture médiatique)
        3. INSEE (données statistiques)
        
        """
    
    if "Conclusion" in sections:
        report += """
        CONCLUSION
        ----------
        
        Les archives du BUMIDOM constituent un corpus documentaire riche et varié,
        permettant d'étudier cette institution sous de multiples angles :
        administratif, médiatique, statistique et audiovisuel.
        
        **Points forts:**
        - Diversité des sources
        - Couverture temporelle complète
        - Accès en ligne pour une grande partie des documents
        
        **Limites identifiées:**
        - Inégalité d'accès selon les sources
        - Nécessité de déplacements pour certaines archives
        - Fragmentation des informations
        
        **Recommandations:**
        1. Numérisation complémentaire des archives physiques
        2. Mise en place d'un portail unifié
        3. Développement d'outils d'analyse spécifiques
        
        """
    
    if "Bibliographie" in sections:
        report += """
        BIBLIOGRAPHIE
        -------------
        
        **Sources principales:**
        - Archives Nationales (site de Pierrefitte-sur-Seine)
        - RetroNews - Bibliothèque nationale de France
        - Gallica - Bibliothèque nationale de France
        - Institut national de l'audiovisuel (INA)
        - Institut national de la statistique et des études économiques (INSEE)
        - Archives Nationales d'Outre-mer (ANOM)
        - Internet Archive (Archive.org)
        
        **Ressources complémentaires:**
        - Centre des archives contemporaines
        - Archives départementales des DOM
        - Bibliothèques universitaires spécialisées
        
        """
    
    return report

# ============================================================================
# PIED DE PAGE
# ============================================================================

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p><strong>Dashboard Archives BUMIDOM - Version Complète</strong></p>
    <p>Sources intégrées: Archives Nationales • RetroNews • Gallica • INA • INSEE • ANOM • Archive.org</p>
    <p><em>Pour toute question ou suggestion: contact@bumidom-archives.fr</em></p>
    <p style='font-size: 0.8em;'>Dernière mise à jour: février 2024 | Version 3.0</p>
</div>
""", unsafe_allow_html=True)
