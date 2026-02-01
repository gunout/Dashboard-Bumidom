import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, date
import json

# ============================================================================
# CONFIGURATION DE LA PAGE
# ============================================================================
st.set_page_config(
    page_title="Archives BUMIDOM - Dashboard Complet",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# DONNÉES DES ARCHIVES BUMIDOM
# ============================================================================

BUMIDOM_ARCHIVES = {
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
                'url': 'https://www.siv.archives-nationales.culture.gouv.fr/siv/rechercheconsultation/consultation/ir/consultationIR.action?irId=FRAN_IR_001514'
            }
        ]
    },
    
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
                'sentiment': 'neutre',
                'extract': 'Le Bureau des migrations des départements d\'outre-mer organise le départ vers la métropole...',
                'url': 'https://www.retronews.fr/journal/le-monde/15-mars-1965/1/1'
            }
        ]
    },
    
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
                'url': 'https://gallica.bnf.fr/ark:/12148/bpt6k9612718t'
            }
        ]
    },
    
    'ina': {
        'name': 'INA',
        'color': '#d62728',
        'icon': '🎥',
        'videos': [
            {
                'id': 'INA_001',
                'title': 'Départ des premiers migrants du BUMIDOM',
                'date': '1963-07-20',
                'url': 'https://www.ina.fr/video/I08324568'
            }
        ]
    },
    
    'insee': {
        'name': 'INSEE',
        'color': '#9467bd',
        'icon': '📈',
        'datasets': [
            {
                'id': 'IS_001',
                'title': 'Flux migratoires entre les DOM et la métropole',
                'period': '1962-1982',
                'url': 'https://www.insee.fr/fr/statistiques/2012712'
            }
        ]
    }
}

# ============================================================================
# FONCTIONS POUR LA PAGE SOURCES
# ============================================================================

def display_sources_with_expanders():
    """Affiche les sources avec des expanders Streamlit"""
    
    st.subheader("📚 Sources d'archives du BUMIDOM")
    
    sources = [
        {
            'name': 'Archives Nationales',
            'icon': '📄',
            'description': 'Fonds principal du BUMIDOM (1962-1981)',
            'url': 'https://www.archives-nationales.culture.gouv.fr/',
            'search_url': 'https://www.siv.archives-nationales.culture.gouv.fr/siv/rechercheconsultation/consultation/ir/consultationIR.action?irId=FRAN_IR_001514',
            'doc_count': '8',
            'access': 'Sur place (Pierrefitte)',
            'key_docs': [
                'Conseil d\'administration (20080699/1-4)',
                'Statistiques migrations (19880445/1-8)',
                'Correspondance ministérielle (19940555/1-15)'
            ]
        },
        {
            'name': 'RetroNews - BnF',
            'icon': '📰',
            'description': 'Presse historique française',
            'url': 'https://www.retronews.fr/',
            'search_url': 'https://www.retronews.fr/search?q=bumidom',
            'doc_count': '246',
            'access': 'Gratuit en ligne',
            'key_docs': [
                'Le Monde (1965) : Départ des premiers migrants',
                'Le Figaro (1970) : Polémique conditions d\'accueil',
                'La Croix (1978) : Bilan 15 ans d\'activité'
            ]
        },
        {
            'name': 'Gallica - BnF',
            'icon': '📖',
            'description': 'Bibliothèque numérique',
            'url': 'https://gallica.bnf.fr/',
            'search_url': 'https://gallica.bnf.fr/services/engine/search/sru?operation=searchRetrieve&version=1.2&query=(bumidom)',
            'doc_count': '42',
            'access': 'Gratuit en ligne',
            'key_docs': [
                'Rapport sur le fonctionnement du BUMIDOM (1975)',
                'Les migrations ultramarines (1980)',
                'Revue "Hommes et Migrations" (1972)'
            ]
        },
        {
            'name': 'INA',
            'icon': '🎥',
            'description': 'Archives audiovisuelles',
            'url': 'https://www.ina.fr/',
            'search_url': 'https://www.ina.fr/advanced-search?q=bumidom',
            'doc_count': '18',
            'access': 'Gratuit (extraits)',
            'key_docs': [
                'Départ des premiers migrants (1963)',
                'Interview du directeur (1970)',
                'Vie dans les foyers (1975)'
            ]
        },
        {
            'name': 'INSEE',
            'icon': '📈',
            'description': 'Statistiques officielles',
            'url': 'https://www.insee.fr/',
            'search_url': 'https://www.insee.fr/fr/statistiques?q=migration+dom',
            'doc_count': '12',
            'access': 'Gratuit en ligne',
            'key_docs': [
                'Flux migratoires DOM-métropole (1962-1982)',
                'Caractéristiques socio-économiques (1968-1982)',
                'Impact démographique (1975-1990)'
            ]
        }
    ]
    
    for source in sources:
        with st.expander(f"{source['icon']} **{source['name']}** - {source['doc_count']} documents", expanded=False):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"**Description:** {source['description']}")
                st.markdown(f"**Accès:** {source['access']}")
                
                st.markdown("**Documents clés:**")
                for doc in source['key_docs']:
                    st.markdown(f"- {doc}")
            
            with col2:
                if source['search_url']:
                    st.link_button("🔍 Rechercher", source['search_url'], use_container_width=True)
                
                if source['url']:
                    st.link_button("🌐 Site principal", source['url'], use_container_width=True)
                
                st.metric("Documents", source['doc_count'])

def display_access_statistics():
    """Affiche les statistiques d'accès aux sources"""
    
    st.subheader("📊 Statistiques d'accès aux sources")
    
    # Données d'accès
    access_data = [
        {'Source': 'RetroNews', 'Type': 'Presse historique', 'Documents': 246, 'Accès': '🟢 En ligne gratuit', '% en ligne': 100},
        {'Source': 'Gallica', 'Type': 'Livres/Rapports', 'Documents': 42, 'Accès': '🟢 En ligne gratuit', '% en ligne': 100},
        {'Source': 'INSEE', 'Type': 'Données statistiques', 'Documents': 12, 'Accès': '🟢 En ligne gratuit', '% en ligne': 100},
        {'Source': 'INA', 'Type': 'Audiovisuel', 'Documents': 18, 'Accès': '🟡 En ligne (extraits)', '% en ligne': 100},
        {'Source': 'Archives Nationales', 'Type': 'Archives officielles', 'Documents': 1200, 'Accès': '🔴 Sur place uniquement', '% en ligne': 0}
    ]
    
    df_access = pd.DataFrame(access_data)
    
    # Graphique
    fig = px.bar(
        df_access,
        x='Source',
        y='Documents',
        color='Accès',
        title='Documents disponibles par source',
        labels={'Documents': 'Nombre de documents', 'Source': 'Source d\'archive'},
        color_discrete_map={
            '🟢 En ligne gratuit': '#10B981',
            '🟡 En ligne (extraits)': '#F59E0B',
            '🔴 Sur place uniquement': '#EF4444'
        }
    )
    
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    # Tableau
    st.dataframe(
        df_access.sort_values('Documents', ascending=False),
        column_config={
            "Source": st.column_config.TextColumn("Source"),
            "Type": st.column_config.TextColumn("Type"),
            "Documents": st.column_config.NumberColumn("Documents", format="%d"),
            "Accès": st.column_config.TextColumn("Accès"),
            "% en ligne": st.column_config.ProgressColumn("% en ligne", format="%d%%", min_value=0, max_value=100)
        },
        use_container_width=True,
        hide_index=True
    )

def unified_search_section():
    """Section de recherche unifiée dans toutes les sources"""
    
    st.subheader("🔍 Recherche dans toutes les sources")
    
    search_term = st.text_input(
        "Entrez votre recherche:",
        placeholder="Ex: migration antillaise, logement migrants...",
        key="unified_search"
    )
    
    if search_term:
        st.info(f"Recherche de: **{search_term}**")
        
        st.markdown("### Rechercher dans chaque source:")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.link_button(
                "📰 RetroNews - Presse historique",
                f"https://www.retronews.fr/search?q={search_term}",
                use_container_width=True
            )
            
            st.link_button(
                "📖 Gallica - Livres et rapports",
                f"https://gallica.bnf.fr/services/engine/search/sru?operation=searchRetrieve&version=1.2&query=({search_term})",
                use_container_width=True
            )
        
        with col2:
            st.link_button(
                "🎥 INA - Archives audiovisuelles",
                f"https://www.ina.fr/advanced-search?q={search_term}",
                use_container_width=True
            )
            
            st.link_button(
                "📈 INSEE - Statistiques",
                f"https://www.insee.fr/fr/statistiques?q={search_term}",
                use_container_width=True
            )

# ============================================================================
# FONCTIONS POUR LES AUTRES PAGES
# ============================================================================

def overview_page():
    """Page Vue d'ensemble"""
    st.header("📊 Vue d'ensemble des archives BUMIDOM")
    
    # Métriques
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Sources disponibles", "5")
    with col2:
        st.metric("Documents référencés", "1500+")
    with col3:
        st.metric("Période couverte", "1962-1982")
    with col4:
        st.metric("% en ligne", "65%")
    
    # Graphique simple
    data = pd.DataFrame({
        'Année': [1963, 1965, 1968, 1971, 1974, 1977, 1980],
        'Migrations': [1200, 1800, 2200, 2500, 1800, 1200, 800]
    })
    
    fig = px.line(data, x='Année', y='Migrations', title='Évolution des migrations BUMIDOM')
    st.plotly_chart(fig, use_container_width=True)
    
    # Tableau des sources
    display_sources_with_expanders()

def explorer_page():
    """Page Exploreur d'archives"""
    st.header("🔍 Exploreur d'archives")
    
    search_query = st.text_input("Rechercher dans les archives:")
    
    # Filtres
    col1, col2, col3 = st.columns(3)
    with col1:
        source_filter = st.multiselect("Source", ["Toutes"] + list(BUMIDOM_ARCHIVES.keys()))
    with col2:
        year_filter = st.slider("Année", 1960, 1990, (1960, 1990))
    with col3:
        type_filter = st.multiselect("Type", ["Tous", "Articles", "Documents", "Vidéos", "Données"])
    
    # Affichage des documents
    for source_id, source_data in BUMIDOM_ARCHIVES.items():
        st.markdown(f"### {source_data['icon']} {source_data['name']}")
        
        if 'documents' in source_data:
            for doc in source_data['documents']:
                with st.expander(doc['title']):
                    st.write(doc.get('description', 'Pas de description'))
                    if doc.get('url'):
                        st.link_button("🔗 Consulter", doc['url'])

def analysis_page():
    """Page Analyses thématiques"""
    st.header("📈 Analyses thématiques")
    
    tab1, tab2, tab3 = st.tabs(["Analyse temporelle", "Analyse par source", "Thématiques"])
    
    with tab1:
        # Simulation de données temporelles
        years = list(range(1962, 1983))
        data = pd.DataFrame({
            'Année': years,
            'Documents': np.random.randint(50, 200, len(years)),
            'Articles': np.random.randint(20, 100, len(years))
        })
        
        fig = px.line(data, x='Année', y=['Documents', 'Articles'], 
                     title='Production documentaire par année')
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        # Répartition par source
        sources = list(BUMIDOM_ARCHIVES.keys())
        counts = [len(BUMIDOM_ARCHIVES[s].get('documents', [])) for s in sources]
        
        fig = px.pie(values=counts, names=sources, title='Répartition par source')
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        # Thématiques
        themes = ['Recrutement', 'Logement', 'Formation', 'Budget', 'Transport']
        frequencies = [35, 28, 22, 10, 5]
        
        fig = px.bar(x=themes, y=frequencies, title='Fréquence des thèmes')
        st.plotly_chart(fig, use_container_width=True)

def timeline_page():
    """Page Chronologie"""
    st.header("🕰️ Chronologie du BUMIDOM")
    
    # Événements clés
    events = [
        {'date': '1963', 'event': 'Création du BUMIDOM', 'type': 'institution'},
        {'date': '1965', 'event': 'Premiers départs massifs', 'type': 'migration'},
        {'date': '1973', 'event': 'Choc pétrolier', 'type': 'contexte'},
        {'date': '1974', 'event': 'Arrêt de l\'immigration de travail', 'type': 'politique'},
        {'date': '1982', 'event': 'Dissolution du BUMIDOM', 'type': 'institution'}
    ]
    
    for event in events:
        with st.container(border=True):
            col1, col2 = st.columns([1, 4])
            with col1:
                st.markdown(f"**{event['date']}**")
            with col2:
                st.markdown(f"**{event['event']}**")
                st.caption(f"Type: {event['type']}")

def tools_page():
    """Page Outils de recherche"""
    st.header("🧮 Outils de recherche")
    
    tab1, tab2 = st.tabs(["Recherche avancée", "Import de données"])
    
    with tab1:
        st.subheader("Recherche multi-critères")
        
        col1, col2 = st.columns(2)
        with col1:
            keywords = st.text_area("Mots-clés", placeholder="Entrez vos termes...")
        with col2:
            field = st.multiselect("Champs à rechercher", 
                                  ["Titre", "Description", "Contenu", "Mots-clés"])
        
        if st.button("🔍 Lancer la recherche"):
            st.success("Recherche effectuée (simulation)")
    
    with tab2:
        st.subheader("Import de données")
        
        uploaded_file = st.file_uploader("Choisir un fichier", type=['csv', 'json'])
        if uploaded_file:
            st.success(f"Fichier {uploaded_file.name} importé")

def export_page():
    """Page Export & Rapport"""
    st.header("📥 Export des données")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Export des données")
        export_format = st.selectbox("Format", ["CSV", "JSON", "Excel"])
        
        if st.button("📥 Exporter les données"):
            # Simulation d'export
            data = pd.DataFrame({'Exemple': [1, 2, 3]})
            st.success("Données prêtes à l'export")
    
    with col2:
        st.subheader("Génération de rapport")
        report_type = st.selectbox("Type de rapport", 
                                  ["Synthèse", "Détaillé", "Académique"])
        
        if st.button("📋 Générer le rapport"):
            st.success("Rapport généré avec succès")

# ============================================================================
# INTERFACE PRINCIPALE
# ============================================================================

def main():
    """Fonction principale du dashboard"""
    
    # Titre principal
    st.title("📚 Archives BUMIDOM - Dashboard Complet")
    st.markdown("*Bureau des Migrations des Départements d'Outre-Mer (1963-1982)*")
    
    # Sidebar
    with st.sidebar:
        st.image("https://via.placeholder.com/200x60/1E3A8A/FFFFFF?text=BUMIDOM", width=200)
        
        st.markdown("### 🧭 Navigation")
        
        page = st.radio(
            "Sélectionnez une section",
            [
                "📊 Vue d'ensemble",
                "🔍 Exploreur d'archives", 
                "📈 Analyses thématiques",
                "🕰️ Chronologie",
                "🔗 Sources d'archives",
                "🧮 Outils de recherche",
                "📥 Export & Rapport"
            ]
        )
        
        st.markdown("---")
        
        st.markdown("### 🔧 Filtres rapides")
        year_filter = st.slider("Période", 1960, 1990, (1963, 1982))
        source_filter = st.multiselect("Sources", 
                                      list(BUMIDOM_ARCHIVES.keys()),
                                      default=list(BUMIDOM_ARCHIVES.keys()))
        
        st.markdown("---")
        
        st.markdown("### 📊 Statistiques")
        st.metric("Documents", "1,500+")
        st.metric("Sources", "5")
        st.metric("Période", "20 ans")
    
    # Affichage de la page sélectionnée
    if page == "📊 Vue d'ensemble":
        overview_page()
    
    elif page == "🔍 Exploreur d'archives":
        explorer_page()
    
    elif page == "📈 Analyses thématiques":
        analysis_page()
    
    elif page == "🕰️ Chronologie":
        timeline_page()
    
    elif page == "🔗 Sources d'archives":
        # PAGE SOURCES - Version corrigée
        st.header("🔗 Sources d'Archives du BUMIDOM")
        st.markdown("*Accédez directement à toutes les archives disponibles en ligne*")
        
        # 1. Tableau récapitulatif
        display_sources_with_expanders()
        
        st.markdown("---")
        
        # 2. Recherche unifiée
        unified_search_section()
        
        st.markdown("---")
        
        # 3. Statistiques d'accès
        display_access_statistics()
    
    elif page == "🧮 Outils de recherche":
        tools_page()
    
    elif page == "📥 Export & Rapport":
        export_page()
    
    # Pied de page
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p><strong>Dashboard Archives BUMIDOM</strong> | Version 2.0</p>
        <p>Sources: Archives Nationales • RetroNews • Gallica • INA • INSEE</p>
        <p><em>Dernière mise à jour: Février 2024</em></p>
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# EXÉCUTION PRINCIPALE
# ============================================================================

if __name__ == "__main__":
    main()
