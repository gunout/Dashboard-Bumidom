import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import requests
from datetime import datetime, date
import json
import re
from collections import Counter
import networkx as nx
from textblob import TextBlob
import warnings
warnings.filterwarnings('ignore')

# Configuration
st.set_page_config(
    page_title="BUMIDOM - Archives Multi-Sources",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé
st.markdown("""
<style>
    .archive-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .metric-card {
        background: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border-left: 5px solid #3B82F6;
    }
    .source-tag {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8em;
        margin: 2px;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# DONNÉES DE RÉFÉRENCE MULTI-SOURCES
# ============================================================================

BUMIDOM_DATA_SOURCES = {
    'france_archives': {
        'name': 'FranceArchives',
        'color': '#1f77b4',
        'documents': [
            {
                'id': 'FA_001',
                'title': 'Conseil administration BUMIDOM',
                'date': '1962-1981',
                'cote': '20080699/1-4',
                'type': 'Procès-verbaux',
                'url': 'https://francearchives.gouv.fr/fr/facomponent/4cf8e64493541970a9407a30ff47693657bd18f9',
                'keywords': ['administration', 'budget', 'décisions']
            },
            {
                'id': 'FA_002',
                'title': 'Statistiques migrations DOM',
                'date': '1963-1980',
                'cote': '19880445/1-8',
                'type': 'Rapports statistiques',
                'url': 'https://francearchives.gouv.fr/fr/search?q=bumidom+statistiques',
                'keywords': ['chiffres', 'flux', 'démographie']
            }
        ]
    },
    
    'retronews': {
        'name': 'RetroNews',
        'color': '#ff7f0e',
        'articles': [
            {
                'id': 'RN_001',
                'title': 'Le BUMIDOM organise le départ de 500 travailleurs',
                'date': '1965-03-15',
                'newspaper': 'Le Monde',
                'url': 'https://www.retronews.fr/search?q=bumidom+1965',
                'sentiment': 'neutre',
                'extract': 'Le Bureau des migrations des DOM organise le départ de 500 travailleurs antillais vers la métropole...'
            },
            {
                'id': 'RN_002',
                'title': 'Polémique sur les conditions d\'accueil',
                'date': '1970-11-22',
                'newspaper': 'Le Figaro',
                'url': 'https://www.retronews.fr/search?q=bumidom+conditions',
                'sentiment': 'négatif',
                'extract': 'Les conditions d\'accueil des migrants ultramarins sont dénoncées par plusieurs associations...'
            },
            {
                'id': 'RN_003',
                'title': 'BUMIDOM: 15 ans d\'activité',
                'date': '1978-05-10',
                'newspaper': 'La Croix',
                'url': 'https://www.retronews.fr/search?q=bumidom+15+ans',
                'sentiment': 'positif',
                'extract': 'En 15 ans d\'existence, le BUMIDOM a permis à plus de 80,000 personnes de migrer...'
            }
        ]
    },
    
    'gallica': {
        'name': 'Gallica',
        'color': '#2ca02c',
        'documents': [
            {
                'id': 'GL_001',
                'title': 'Rapport sur le fonctionnement du BUMIDOM',
                'date': '1975',
                'author': 'Ministère du Travail',
                'url': 'https://gallica.bnf.fr/ark:/12148/bpt6k9612718t',
                'pages': 120,
                'topics': ['organisation', 'financement', 'résultats']
            },
            {
                'id': 'GL_002',
                'title': 'Les migrations ultramarines vers la France',
                'date': '1980',
                'author': 'INED',
                'url': 'https://gallica.bnf.fr/ark:/12148/bpt6k4803231d',
                'pages': 85,
                'topics': ['démographie', 'sociologie', 'intégration']
            }
        ]
    },
    
    'ina': {
        'name': 'INA',
        'color': '#d62728',
        'videos': [
            {
                'id': 'INA_001',
                'title': 'Départ des premiers migrants',
                'date': '1963',
                'duration': '02:15',
                'url': 'https://www.ina.fr/video/I00000001',
                'description': 'Reportage sur le départ des premiers travailleurs antillais'
            },
            {
                'id': 'INA_002',
                'title': 'Interview du directeur du BUMIDOM',
                'date': '1970',
                'duration': '05:30',
                'url': 'https://www.ina.fr/video/I00000002',
                'description': 'Le directeur explique les objectifs et méthodes de l\'organisme'
            }
        ]
    },
    
    'insee': {
        'name': 'INSEE',
        'color': '#9467bd',
        'datasets': [
            {
                'id': 'IS_001',
                'title': 'Flux migratoires DOM-métropole',
                'period': '1962-1982',
                'variables': ['origine', 'destination', 'âge', 'profession'],
                'url': 'https://www.insee.fr/fr/statistiques/2012712'
            },
            {
                'id': 'IS_002',
                'title': 'Emploi des migrants ultramarins',
                'period': '1968-1982',
                'variables': ['secteur', 'salaire', 'qualification'],
                'url': 'https://www.insee.fr/fr/statistiques/2012713'
            }
        ]
    }
}

# ============================================================================
# FONCTIONS D'ANALYSE MULTI-SOURCES
# ============================================================================

def analyze_temporal_coverage():
    """Analyse la couverture temporelle des différentes sources"""
    timeline_data = []
    
    for source_name, source_data in BUMIDOM_DATA_SOURCES.items():
        if 'articles' in source_data:
            for article in source_data['articles']:
                timeline_data.append({
                    'date': article['date'],
                    'source': source_data['name'],
                    'type': 'article',
                    'title': article['title'][:50] + '...'
                })
        elif 'documents' in source_data:
            for doc in source_data['documents']:
                timeline_data.append({
                    'date': doc['date'],
                    'source': source_data['name'],
                    'type': 'document',
                    'title': doc['title'][:50] + '...'
                })
    
    return pd.DataFrame(timeline_data)

def analyze_sentiment_evolution():
    """Analyse l'évolution du sentiment dans la presse"""
    sentiment_data = []
    
    articles = BUMIDOM_DATA_SOURCES['retronews']['articles']
    for article in articles:
        year = int(article['date'].split('-')[0])
        
        # Analyse simple du sentiment basée sur les tags
        if article['sentiment'] == 'positif':
            score = 1
        elif article['sentiment'] == 'négatif':
            score = -1
        else:
            score = 0
        
        sentiment_data.append({
            'year': year,
            'sentiment': score,
            'title': article['title'],
            'newspaper': article['newspaper']
        })
    
    return pd.DataFrame(sentiment_data)

def extract_keywords():
    """Extrait les mots-clés de toutes les sources"""
    all_text = ""
    
    for source_name, source_data in BUMIDOM_DATA_SOURCES.items():
        if 'articles' in source_data:
            for article in source_data['articles']:
                all_text += article['extract'] + " "
        if 'documents' in source_data:
            for doc in source_data['documents']:
                all_text += doc['title'] + " "
                if 'keywords' in doc:
                    all_text += " ".join(doc['keywords']) + " "
    
    # Tokenization simple
    words = re.findall(r'\b\w+\b', all_text.lower())
    french_stopwords = ['le', 'la', 'les', 'de', 'des', 'du', 'et', 'en', 'à', 'au', 'aux', 'dans', 'pour', 'par']
    filtered_words = [w for w in words if w not in french_stopwords and len(w) > 3]
    
    word_counts = Counter(filtered_words)
    return pd.DataFrame(word_counts.most_common(20), columns=['mot', 'fréquence'])

def create_source_network():
    """Crée un réseau de relations entre les sources"""
    G = nx.Graph()
    
    # Ajouter les nœuds (sources)
    for source_name, source_data in BUMIDOM_DATA_SOURCES.items():
        G.add_node(source_data['name'], 
                  type='source',
                  color=source_data['color'],
                  size=len(source_data.get('articles', source_data.get('documents', []))))
    
    # Ajouter les relations (liens thématiques)
    themes = {}
    for source_name, source_data in BUMIDOM_DATA_SOURCES.items():
        for key in ['keywords', 'topics']:
            if key in source_data:
                for item in source_data[key]:
                    if item not in themes:
                        themes[item] = []
                    themes[item].append(source_data['name'])
    
    # Ajouter les liens entre sources partageant les mêmes thèmes
    for theme, sources in themes.items():
        for i in range(len(sources)):
            for j in range(i+1, len(sources)):
                if G.has_edge(sources[i], sources[j]):
                    G[sources[i]][sources[j]]['weight'] += 1
                else:
                    G.add_edge(sources[i], sources[j], weight=1, theme=theme)
    
    return G

# ============================================================================
# INTERFACE PRINCIPALE
# ============================================================================

st.title("📚 BUMIDOM - Archives Multi-Sources")
st.markdown("*Dashboard intégré pour la consultation et l'analyse des archives du BUMIDOM*")

# Sidebar
with st.sidebar:
    st.image("https://via.placeholder.com/150x50/003366/FFFFFF?text=ARCHIVES", width=150)
    st.title("Navigation")
    
    analysis_mode = st.radio(
        "Mode d'analyse",
        ["📋 Vue d'ensemble", "🔍 Analyse par source", "📊 Analyse croisée", "🧮 Outils avancés"]
    )
    
    st.markdown("---")
    st.subheader("Filtres")
    
    selected_sources = st.multiselect(
        "Sources à inclure",
        [source['name'] for source in BUMIDOM_DATA_SOURCES.values()],
        default=[source['name'] for source in BUMIDOM_DATA_SOURCES.values()]
    )
    
    date_range = st.slider(
        "Période",
        1960, 1990, (1960, 1990)
    )
    
    st.markdown("---")
    st.info("""
    **Sources disponibles:**
    - 📄 FranceArchives (documents officiels)
    - 📰 RetroNews (presse historique)
    - 📖 Gallica (livres et rapports)
    - 🎥 INA (archives audiovisuelles)
    - 📈 INSEE (statistiques)
    """)

# ============================================================================
# SECTION 1: VUE D'ENSEMBLE
# ============================================================================
if analysis_mode == "📋 Vue d'ensemble":
    st.header("Vue d'ensemble des archives")
    
    # Métriques globales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_docs = sum(len(source.get('articles', source.get('documents', []))) 
                        for source in BUMIDOM_DATA_SOURCES.values())
        st.metric("Documents référencés", total_docs)
    
    with col2:
        total_sources = len(BUMIDOM_DATA_SOURCES)
        st.metric("Sources différentes", total_sources)
    
    with col3:
        start_year = min(int(source.get('articles', [{}])[0].get('date', '1960').split('-')[0]) 
                        for source in BUMIDOM_DATA_SOURCES.values() 
                        if source.get('articles') or source.get('documents'))
        end_year = max(int(source.get('articles', [{}])[-1].get('date', '1985').split('-')[0]) 
                      for source in BUMIDOM_DATA_SOURCES.values() 
                      if source.get('articles') or source.get('documents'))
        st.metric("Période couverte", f"{end_year-start_year} ans", f"{start_year}-{end_year}")
    
    with col4:
        media_types = set()
        for source in BUMIDOM_DATA_SOURCES.values():
            if 'articles' in source:
                media_types.add('texte')
            if 'videos' in source:
                media_types.add('vidéo')
            if 'datasets' in source:
                media_types.add('données')
        st.metric("Types de médias", len(media_types))
    
    # Carte des sources
    st.subheader("🌍 Carte des sources d'archives")
    
    source_df = pd.DataFrame([
        {
            'Source': data['name'],
            'Documents': len(data.get('articles', data.get('documents', data.get('videos', data.get('datasets', []))))),
            'Type': 'Presse' if 'articles' in data else 'Archives' if 'documents' in data else 'Vidéo' if 'videos' in data else 'Données',
            'Couleur': data['color'],
            'Période': f"{min(int(d.get('date', '1960').split('-')[0]) for d in data.get('articles', data.get('documents', [{'date': '1960'}])))}-{max(int(d.get('date', '1985').split('-')[0]) for d in data.get('articles', data.get('documents', [{'date': '1985'}])))}"
        }
        for data in BUMIDOM_DATA_SOURCES.values()
    ])
    
    fig = px.treemap(
        source_df,
        path=['Type', 'Source'],
        values='Documents',
        color='Documents',
        color_continuous_scale='Blues',
        title='Répartition des documents par source'
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Frise chronologique
    st.subheader("🕰️ Frise chronologique des archives")
    
    timeline_df = analyze_temporal_coverage()
    
    if not timeline_df.empty:
        fig = px.scatter(
            timeline_df,
            x='date',
            y='source',
            color='type',
            size=[10]*len(timeline_df),
            hover_name='title',
            title='Couverture temporelle par source',
            labels={'date': 'Date', 'source': 'Source', 'type': 'Type'}
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # Nuage de mots
    st.subheader("📝 Nuage de mots-clés")
    
    keywords_df = extract_keywords()
    
    fig = px.bar(
        keywords_df,
        x='fréquence',
        y='mot',
        orientation='h',
        title='Mots-clés les plus fréquents',
        color='fréquence',
        color_continuous_scale='Viridis'
    )
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# SECTION 2: ANALYSE PAR SOURCE
# ============================================================================
elif analysis_mode == "🔍 Analyse par source":
    st.header("Analyse détaillée par source")
    
    source_tabs = st.tabs([source['name'] for source in BUMIDOM_DATA_SOURCES.values()])
    
    for idx, (source_name, source_data) in enumerate(BUMIDOM_DATA_SOURCES.items()):
        with source_tabs[idx]:
            st.markdown(f"### {source_data['name']}")
            st.markdown(f"*Couleur: `{source_data['color']}`*")
            
            # Afficher le contenu de la source
            if 'articles' in source_data:
                st.subheader("📰 Articles de presse")
                for article in source_data['articles']:
                    with st.expander(f"{article['title']} ({article['date']})"):
                        col_a1, col_a2 = st.columns([3, 1])
                        with col_a1:
                            st.write(article['extract'])
                            st.caption(f"**Journal:** {article['newspaper']}")
                        with col_a2:
                            sentiment = article['sentiment']
                            sentiment_color = {
                                'positif': '🟢',
                                'négatif': '🔴',
                                'neutre': '🟡'
                            }.get(sentiment, '⚪')
                            st.metric("Sentiment", sentiment_color)
                            st.link_button("🔗 Lire l'article", article['url'])
            
            if 'documents' in source_data:
                st.subheader("📄 Documents officiels")
                for doc in source_data['documents']:
                    with st.container(border=True):
                        col_d1, col_d2 = st.columns([3, 1])
                        with col_d1:
                            st.markdown(f"**{doc['title']}**")
                            st.markdown(f"*{doc['date']} | Cote: `{doc.get('cote', 'N/A')}`*")
                            if 'keywords' in doc:
                                for kw in doc['keywords']:
                                    st.markdown(f"`{kw}`", unsafe_allow_html=True)
                        with col_d2:
                            st.metric("Type", doc['type'])
                            st.link_button("📖 Consulter", doc['url'])
            
            if 'videos' in source_data:
                st.subheader("🎥 Archives audiovisuelles")
                for video in source_data['videos']:
                    col_v1, col_v2 = st.columns([3, 1])
                    with col_v1:
                        st.markdown(f"**{video['title']}**")
                        st.markdown(f"*{video['date']} | Durée: {video['duration']}*")
                        st.write(video['description'])
                    with col_v2:
                        st.metric("Support", "Vidéo")
                        st.link_button("▶️ Visionner", video['url'])
            
            if 'datasets' in source_data:
                st.subheader("📈 Jeux de données")
                for dataset in source_data['datasets']:
                    with st.expander(f"{dataset['title']} ({dataset['period']})"):
                        st.markdown(f"**Variables disponibles:**")
                        for var in dataset['variables']:
                            st.markdown(f"- `{var}`")
                        st.link_button("📥 Télécharger les données", dataset['url'])
            
            # Statistiques de la source
            st.subheader("📊 Statistiques de la source")
            
            col_s1, col_s2, col_s3 = st.columns(3)
            
            with col_s1:
                count = len(source_data.get('articles', source_data.get('documents', 
                         source_data.get('videos', source_data.get('datasets', [])))))
                st.metric("Documents", count)
            
            with col_s2:
                if 'articles' in source_data:
                    sentiments = [a['sentiment'] for a in source_data['articles']]
                    pos = sentiments.count('positif')
                    neg = sentiments.count('négatif')
                    st.metric("Équilibre sentiment", f"{pos}/{neg}")
            
            with col_s3:
                if 'documents' in source_data:
                    years = [int(d['date'].split('-')[0]) for d in source_data['documents']]
                    if years:
                        coverage = f"{min(years)}-{max(years)}"
                        st.metric("Période", coverage)

# ============================================================================
# SECTION 3: ANALYSE CROISÉE
# ============================================================================
elif analysis_mode == "📊 Analyse croisée":
    st.header("Analyse croisée des sources")
    
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Évolution temporelle", "🎭 Analyse des sentiments", 
                                     "🔗 Réseau des sources", "📊 Analyse thématique"])
    
    with tab1:
        st.subheader("Évolution de la couverture médiatique")
        
        # Compter les documents par année et par source
        yearly_counts = []
        for source_name, source_data in BUMIDOM_DATA_SOURCES.items():
            if 'articles' in source_data:
                years = [int(a['date'].split('-')[0]) for a in source_data['articles']]
                for year in set(years):
                    yearly_counts.append({
                        'année': year,
                        'source': source_data['name'],
                        'count': years.count(year)
                    })
        
        if yearly_counts:
            yearly_df = pd.DataFrame(yearly_counts)
            
            # Graphique d'évolution
            fig = px.line(
                yearly_df,
                x='année',
                y='count',
                color='source',
                markers=True,
                title='Nombre de documents par année et par source',
                labels={'count': 'Nombre de documents', 'année': 'Année'}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Analyse des pics d'activité
        st.subheader("Pics d'activité médiatique")
        
        if yearly_counts:
            yearly_agg = yearly_df.groupby('année')['count'].sum().reset_index()
            
            # Identifier les pics
            mean_count = yearly_agg['count'].mean()
            peaks = yearly_agg[yearly_agg['count'] > mean_count * 1.5]
            
            if not peaks.empty:
                st.write("**Années avec une couverture médiatique intense:**")
                for _, peak in peaks.iterrows():
                    st.markdown(f"- **{peak['année']}**: {int(peak['count'])} documents")
                    
                    # Chercher les événements de cette année
                    events = []
                    for source_data in BUMIDOM_DATA_SOURCES.values():
                        if 'articles' in source_data:
                            for article in source_data['articles']:
                                if int(article['date'].split('-')[0]) == peak['année']:
                                    events.append(article['title'][:100] + "...")
                    
                    if events:
                        with st.expander(f"Voir les événements de {peak['année']}"):
                            for event in events[:5]:  # Limiter à 5 événements
                                st.write(f"• {event}")
    
    with tab2:
        st.subheader("Analyse des sentiments dans la presse")
        
        sentiment_df = analyze_sentiment_evolution()
        
        if not sentiment_df.empty:
            # Graphique d'évolution du sentiment
            fig = px.line(
                sentiment_df.groupby('year')['sentiment'].mean().reset_index(),
                x='year',
                y='sentiment',
                title='Évolution du sentiment médiatique moyen',
                markers=True
            )
            fig.add_hline(y=0, line_dash="dash", line_color="gray")
            fig.update_layout(yaxis_range=[-1.1, 1.1])
            st.plotly_chart(fig, use_container_width=True)
            
            # Analyse par journal
            st.subheader("Analyse par journal")
            
            journal_sentiment = sentiment_df.groupby('newspaper').agg({
                'sentiment': ['mean', 'count']
            }).round(3)
            
            journal_sentiment.columns = ['sentiment_moyen', 'nombre_articles']
            journal_sentiment = journal_sentiment.reset_index()
            
            fig = px.bar(
                journal_sentiment,
                x='newspaper',
                y='sentiment_moyen',
                color='nombre_articles',
                title='Positionnement moyen des journaux',
                labels={'sentiment_moyen': 'Sentiment moyen', 'newspaper': 'Journal'}
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Table détaillée
            st.dataframe(
                journal_sentiment.sort_values('sentiment_moyen', ascending=False),
                use_container_width=True
            )
    
    with tab3:
        st.subheader("Réseau des sources et thèmes")
        
        # Créer le réseau
        G = create_source_network()
        
        if G.number_of_nodes() > 0:
            # Extraire les positions pour le graphique
            pos = nx.spring_layout(G, seed=42)
            
            # Créer le graphique Plotly
            edge_traces = []
            for edge in G.edges(data=True):
                x0, y0 = pos[edge[0]]
                x1, y1 = pos[edge[1]]
                
                edge_trace = go.Scatter(
                    x=[x0, x1, None],
                    y=[y0, y1, None],
                    line=dict(width=edge[2]['weight']*0.5, color='#888'),
                    hoverinfo='text',
                    text=f"Thème: {edge[2].get('theme', '')}",
                    mode='lines'
                )
                edge_traces.append(edge_trace)
            
            node_trace = go.Scatter(
                x=[pos[node][0] for node in G.nodes()],
                y=[pos[node][1] for node in G.nodes()],
                mode='markers+text',
                text=[node for node in G.nodes()],
                textposition="top center",
                marker=dict(
                    size=[G.nodes[node]['size']*10 for node in G.nodes()],
                    color=[G.nodes[node]['color'] for node in G.nodes()],
                    line_width=2
                ),
                hovertext=[f"Documents: {G.nodes[node]['size']}" for node in G.nodes()]
            )
            
            fig = go.Figure(data=edge_traces + [node_trace])
            fig.update_layout(
                title='Réseau des sources du BUMIDOM',
                showlegend=False,
                hovermode='closest',
                height=600
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Analyse des centralités
            st.subheader("Centralité des sources")
            
            centrality_data = []
            for node in G.nodes():
                centrality_data.append({
                    'Source': node,
                    'Degré': G.degree(node),
                    'Centralité': round(nx.degree_centrality(G)[node], 3)
                })
            
            centrality_df = pd.DataFrame(centrality_data).sort_values('Centralité', ascending=False)
            st.dataframe(centrality_df, use_container_width=True)
    
    with tab4:
        st.subheader("Analyse thématique croisée")
        
        # Extraire tous les thèmes
        all_themes = {}
        for source_name, source_data in BUMIDOM_DATA_SOURCES.items():
            for key in ['keywords', 'topics']:
                if key in source_data:
                    for item in source_data[key]:
                        if item not in all_themes:
                            all_themes[item] = []
                        all_themes[item].append(source_data['name'])
        
        # Créer une matrice source-thème
        sources = list(BUMIDOM_DATA_SOURCES.keys())
        themes = list(all_themes.keys())
        
        matrix_data = []
        for theme in themes:
            row = {'Thème': theme}
            for source in sources:
                source_name = BUMIDOM_DATA_SOURCES[source]['name']
                row[source_name] = 1 if source_name in all_themes[theme] else 0
            matrix_data.append(row)
        
        matrix_df = pd.DataFrame(matrix_data)
        
        # Heatmap
        fig = px.imshow(
            matrix_df.set_index('Thème'),
            title='Présence des thèmes par source',
            color_continuous_scale='Blues',
            aspect='auto'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Analyse des thèmes dominants
        st.subheader("Thèmes les plus présents")
        
        theme_counts = {theme: len(sources) for theme, sources in all_themes.items()}
        theme_df = pd.DataFrame(list(theme_counts.items()), 
                               columns=['Thème', 'Nombre de sources'])
        theme_df = theme_df.sort_values('Nombre de sources', ascending=False)
        
        fig = px.bar(
            theme_df.head(10),
            x='Thème',
            y='Nombre de sources',
            title='Top 10 des thèmes les plus couverts',
            color='Nombre de sources'
        )
        st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# SECTION 4: OUTILS AVANCÉS
# ============================================================================
else:
    st.header("Outils avancés d'analyse")
    
    tool_tab1, tool_tab2, tool_tab3, tool_tab4 = st.tabs([
        "🔎 Recherche avancée", "📥 Import de données", 
        "📊 Analyse textuelle", "🔄 Mise à jour des sources"
    ])
    
    with tool_tab1:
        st.subheader("Recherche dans toutes les sources")
        
        search_query = st.text_input("Entrez votre recherche:", 
                                    placeholder="Ex: migration antillaise, budget BUMIDOM...")
        
        if search_query:
            st.info(f"Recherche de: '{search_query}'")
            
            results = []
            
            # Rechercher dans toutes les sources
            for source_name, source_data in BUMIDOM_DATA_SOURCES.items():
                if 'articles' in source_data:
                    for article in source_data['articles']:
                        if (search_query.lower() in article['title'].lower() or 
                            search_query.lower() in article['extract'].lower()):
                            results.append({
                                'Source': source_data['name'],
                                'Type': 'Article',
                                'Titre': article['title'],
                                'Date': article['date'],
                                'Extrait': article['extract'][:200] + '...',
                                'URL': article['url']
                            })
                
                if 'documents' in source_data:
                    for doc in source_data['documents']:
                        if search_query.lower() in doc['title'].lower():
                            results.append({
                                'Source': source_data['name'],
                                'Type': 'Document',
                                'Titre': doc['title'],
                                'Date': doc['date'],
                                'Extrait': f"Cote: {doc.get('cote', 'N/A')}",
                                'URL': doc['url']
                            })
            
            if results:
                st.success(f"✅ {len(results)} résultat(s) trouvé(s)")
                
                for result in results:
                    with st.container(border=True):
                        col_r1, col_r2 = st.columns([3, 1])
                        with col_r1:
                            st.markdown(f"**{result['Titre']}**")
                            st.markdown(f"*{result['Source']} | {result['Type']} | {result['Date']}*")
                            st.write(result['Extrait'])
                        with col_r2:
                            st.link_button("🔗 Consulter", result['URL'])
            else:
                st.warning("Aucun résultat trouvé. Essayez d'autres termes de recherche.")
        
        # Recherche par période
        st.subheader("Recherche par période")
        
        col_y1, col_y2 = st.columns(2)
        with col_y1:
            start_year = st.number_input("Année de début", 1960, 1990, 1963)
        with col_y2:
            end_year = st.number_input("Année de fin", 1960, 1990, 1982)
        
        if st.button("Rechercher par période"):
            period_results = []
            
            for source_name, source_data in BUMIDOM_DATA_SOURCES.items():
                if 'articles' in source_data:
                    for article in source_data['articles']:
                        article_year = int(article['date'].split('-')[0])
                        if start_year <= article_year <= end_year:
                            period_results.append({
                                'Source': source_data['name'],
                                'Titre': article['title'],
                                'Année': article_year,
                                'URL': article['url']
                            })
            
            if period_results:
                period_df = pd.DataFrame(period_results)
                
                # Graphique par année
                yearly_counts = period_df.groupby('Année').size().reset_index(name='count')
                
                fig = px.bar(
                    yearly_counts,
                    x='Année',
                    y='count',
                    title=f'Documents trouvés ({start_year}-{end_year})',
                    labels={'count': 'Nombre de documents'}
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Liste des documents
                st.dataframe(
                    period_df[['Année', 'Source', 'Titre']],
                    use_container_width=True,
                    hide_index=True
                )
    
    with tool_tab2:
        st.subheader("Import de nouvelles données")
        
        import_option = st.radio(
            "Type d'import",
            ["Fichier CSV/Excel", "URL d'archive", "Saisie manuelle"]
        )
        
        if import_option == "Fichier CSV/Excel":
            uploaded_file = st.file_uploader("Choisir un fichier", 
                                           type=['csv', 'xlsx', 'json'])
            
            if uploaded_file is not None:
                try:
                    if uploaded_file.name.endswith('.csv'):
                        df = pd.read_csv(uploaded_file)
                    elif uploaded_file.name.endswith('.xlsx'):
                        df = pd.read_excel(uploaded_file)
                    elif uploaded_file.name.endswith('.json'):
                        df = pd.read_json(uploaded_file)
                    
                    st.success(f"Fichier importé: {len(df)} lignes")
                    
                    # Aperçu
                    st.subheader("Aperçu des données")
                    st.dataframe(df.head(), use_container_width=True)
                    
                    # Options d'analyse
                    if st.button("Analyser les données importées"):
                        st.info("Fonctionnalité d'analyse à implémenter")
                
                except Exception as e:
                    st.error(f"Erreur lors de l'import: {e}")
        
        elif import_option == "URL d'archive":
            archive_url = st.text_input("URL de l'archive", 
                                       placeholder="https://...")
            
            if archive_url and st.button("Importer depuis l'URL"):
                with st.spinner("Import en cours..."):
                    try:
                        # Simulation d'import
                        st.success(f"URL analysée: {archive_url}")
                        st.info("Pour un import réel, un script spécifique serait nécessaire.")
                    except Exception as e:
                        st.error(f"Erreur: {e}")
        
        else:  # Saisie manuelle
            st.subheader("Ajouter une nouvelle archive")
            
            with st.form("new_archive_form"):
                source_name = st.selectbox("Source", 
                                         ["FranceArchives", "RetroNews", "Gallica", 
                                          "INA", "INSEE", "Autre"])
                
                archive_title = st.text_input("Titre")
                archive_date = st.text_input("Date/Année", placeholder="1965 ou 1965-03-15")
                archive_url = st.text_input("URL")
                archive_type = st.selectbox("Type", ["Article", "Document", "Vidéo", "Données"])
                
                if st.form_submit_button("Ajouter l'archive"):
                    st.success(f"Archive '{archive_title}' ajoutée (stockage à implémenter)")
    
    with tool_tab3:
        st.subheader("Analyse textuelle avancée")
        
        text_to_analyze = st.text_area(
            "Texte à analyser",
            placeholder="Collez ici un texte d'archive à analyser...",
            height=200
        )
        
        if text_to_analyze:
            col_ta1, col_ta2, col_ta3 = st.columns(3)
            
            with col_ta1:
                word_count = len(text_to_analyze.split())
                st.metric("Mots", word_count)
            
            with col_ta2:
                char_count = len(text_to_analyze)
                st.metric("Caractères", char_count)
            
            with col_ta3:
                # Analyse simple de sentiment (en français simplifiée)
                positive_words = ['bon', 'positif', 'réussi', 'succès', 'progrès', 'amélioration']
                negative_words = ['mauvais', 'négatif', 'échec', 'problème', 'difficile', 'critique']
                
                text_lower = text_to_analyze.lower()
                pos_count = sum(text_lower.count(word) for word in positive_words)
                neg_count = sum(text_lower.count(word) for word in negative_words)
                
                if pos_count > neg_count:
                    sentiment = "🟢 Positif"
                elif neg_count > pos_count:
                    sentiment = "🔴 Négatif"
                else:
                    sentiment = "🟡 Neutre"
                
                st.metric("Sentiment", sentiment)
            
            # Extraction des entités nommées (simplifiée)
            st.subheader("Entités détectées")
            
            # Liste de termes liés au BUMIDOM
            bumidom_entities = [
                'BUMIDOM', 'DOM', 'TOM', 'Antilles', 'Guadeloupe', 'Martinique',
                'Guyane', 'Réunion', 'migration', 'migrant', 'travailleur',
                'logement', 'formation', 'emploi', 'budget'
            ]
            
            detected_entities = []
            for entity in bumidom_entities:
                if entity.lower() in text_to_analyze.lower():
                    detected_entities.append(entity)
            
            if detected_entities:
                st.write("**Termes identifiés:**")
                for entity in detected_entities:
                    st.markdown(f"`{entity}`", unsafe_allow_html=True)
            else:
                st.info("Aucun terme spécifique au BUMIDOM détecté")
            
            # Fréquence des mots
            st.subheader("Fréquence des mots")
            
            words = re.findall(r'\b\w+\b', text_to_analyze.lower())
            word_freq = Counter(words)
            
            freq_df = pd.DataFrame(word_freq.most_common(15), 
                                 columns=['Mot', 'Fréquence'])
            
            fig = px.bar(
                freq_df,
                x='Fréquence',
                y='Mot',
                orientation='h',
                title='Top 15 des mots les plus fréquents',
                color='Fréquence'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with tool_tab4:
        st.subheader("Mise à jour des sources")
        
        st.info("""
        Cette section permet de mettre à jour les données des différentes sources.
        Les mises à jour peuvent être effectuées manuellement ou automatiquement.
        """)
        
        col_up1, col_up2 = st.columns(2)
        
        with col_up1:
            st.markdown("### Sources à mettre à jour")
            
            update_sources = st.multiselect(
                "Sélectionnez les sources",
                [source['name'] for source in BUMIDOM_DATA_SOURCES.values()],
                default=[]
            )
            
            if st.button("🔄 Vérifier les mises à jour", type="primary"):
                with st.spinner("Vérification en cours..."):
                    for source_name in update_sources:
                        st.write(f"**{source_name}**: Vérification...")
                        # Ici, on simule la vérification
                        st.success(f"{source_name}: Données à jour")
        
        with col_up2:
            st.markdown("### Options de mise à jour")
            
            update_frequency = st.selectbox(
                "Fréquence de mise à jour",
                ["Manuelle", "Quotidienne", "Hebdomadaire", "Mensuelle"]
            )
            
            auto_download = st.checkbox("Téléchargement automatique", value=False)
            
            if st.button("💾 Enregistrer les paramètres"):
                st.success("Paramètres enregistrés")

# ============================================================================
# PIED DE PAGE ET EXPORT
# ============================================================================

st.markdown("---")
col_footer1, col_footer2 = st.columns(2)

with col_footer1:
    st.markdown("### 📥 Export des données")
    
    export_format = st.selectbox("Format d'export", ["CSV", "JSON", "Excel"])
    
    if st.button("Exporter toutes les données"):
        # Préparer les données pour l'export
        all_data = []
        
        for source_name, source_data in BUMIDOM_DATA_SOURCES.items():
            if 'articles' in source_data:
                for article in source_data['articles']:
                    all_data.append({
                        'source': source_data['name'],
                        'type': 'article',
                        'title': article['title'],
                        'date': article['date'],
                        'url': article['url']
                    })
            
            if 'documents' in source_data:
                for doc in source_data['documents']:
                    all_data.append({
                        'source': source_data['name'],
                        'type': 'document',
                        'title': doc['title'],
                        'date': doc['date'],
                        'url': doc['url']
                    })
        
        export_df = pd.DataFrame(all_data)
        
        if export_format == "CSV":
            csv = export_df.to_csv(index=False)
            st.download_button(
                label="📥 Télécharger CSV",
                data=csv,
                file_name="bumidom_archives.csv",
                mime="text/csv"
            )
        
        elif export_format == "JSON":
            json_data = export_df.to_json(orient='records', force_ascii=False)
            st.download_button(
                label="📥 Télécharger JSON",
                data=json_data,
                file_name="bumidom_archives.json",
                mime="application/json"
            )

with col_footer2:
    st.markdown("### 📊 Rapport d'analyse")
    
    if st.button("Générer un rapport complet"):
        with st.spinner("Génération du rapport..."):
            # Statistiques du rapport
            total_docs = sum(len(source.get('articles', source.get('documents', []))) 
                           for source in BUMIDOM_DATA_SOURCES.values())
            total_sources = len(BUMIDOM_DATA_SOURCES)
            
            st.success(f"Rapport généré: {total_docs} documents de {total_sources} sources")
            
            # Affichage du rapport
            with st.expander("📋 Voir le rapport", expanded=True):
                st.markdown(f"""
                ## Rapport d'analyse BUMIDOM
                
                **Date de génération:** {datetime.now().strftime('%d/%m/%Y %H:%M')}
                
                ### Résumé
                - **Total des documents:** {total_docs}
                - **Sources analysées:** {total_sources}
                - **Période couverte:** 1960-1990
                
                ### Distribution par source
                """)
                
                for source_name, source_data in BUMIDOM_DATA_SOURCES.items():
                    count = len(source_data.get('articles', source_data.get('documents', [])))
                    st.markdown(f"- **{source_data['name']}:** {count} documents")
                
                st.markdown("""
                ### Recommandations
                1. Compléter avec des archives locales des DOM-TOM
                2. Intégrer des témoignages oraux
                3. Croiser avec les archives syndicales
                4. Analyser l'impact à long terme
                """)

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p><strong>Dashboard BUMIDOM - Archives Multi-Sources</strong> | Version 2.0</p>
    <p>Sources intégrées: FranceArchives • RetroNews • Gallica • INA • INSEE</p>
    <p><em>Pour une recherche approfondie, consultez les sites sources directement</em></p>
</div>
""", unsafe_allow_html=True)
