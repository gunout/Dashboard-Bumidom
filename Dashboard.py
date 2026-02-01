import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, date
import json

# Configuration
st.set_page_config(page_title="Archives BUMIDOM", layout="wide")
st.title("📚 Archives du BUMIDOM - Version Hors Ligne")

# ============================================================================
# DONNÉES DE RÉFÉRENCE POUR MODE HORS LIGNE
# ============================================================================

BUMIDOM_ARCHIVES_DATA = {
    'main_archive': {
        'id': '4cf8e64493541970a9407a30ff47693657bd18f9',
        'label': 'Conseil d’administration du BUMIDOM',
        'date': '1962 - 1981',
        'cote': '20080699/1-20080699/4',
        'content': 'Procès-verbaux, rapports d’activités, budget, bilans.',
        'location': 'Archives Nationales, Pierrefitte-sur-Seine',
        'access': 'Consultation sur place uniquement',
        'status': 'Communicable'
    },
    
    'related_archives': [
        {
            'title': 'Ministère des Outre-mer - Correspondance',
            'period': '1958-1985',
            'cote': '19940555/1-15',
            'type': 'Correspondance administrative'
        },
        {
            'title': 'Statistiques migratoires DOM-TOM',
            'period': '1954-1982',
            'cote': '19880445/1-8',
            'type': 'Rapports statistiques'
        },
        {
            'title': 'Budget et financement BUMIDOM',
            'period': '1963-1982',
            'cote': '20070233/1-6',
            'type': 'Documents budgétaires'
        },
        {
            'title': 'Presse et médias sur les migrations',
            'period': '1960-1985',
            'cote': 'Divers (BnF)',
            'type': 'Coupures de presse'
        }
    ],
    
    'thematic_analysis': {
        'themes': [
            {'name': 'Recrutement', 'weight': 0.25, 'color': '#1f77b4'},
            {'name': 'Logement', 'weight': 0.20, 'color': '#ff7f0e'},
            {'name': 'Formation', 'weight': 0.18, 'color': '#2ca02c'},
            {'name': 'Budget', 'weight': 0.15, 'color': '#d62728'},
            {'name': 'Transport', 'weight': 0.12, 'color': '#9467bd'},
            {'name': 'Politique', 'weight': 0.10, 'color': '#8c564b'}
        ],
        'timeline': [
            {'year': 1963, 'event': 'Création du BUMIDOM', 'type': 'institutionnel'},
            {'year': 1965, 'event': 'Premiers centres d\'accueil', 'type': 'infrastructure'},
            {'year': 1968, 'event': 'Accords logement sociaux', 'type': 'politique'},
            {'year': 1973, 'event': 'Choc pétrolier - révisions', 'type': 'économique'},
            {'year': 1974, 'event': 'Arrêt immigration travail', 'type': 'politique'},
            {'year': 1981, 'event': 'Préparation dissolution', 'type': 'institutionnel'}
        ]
    }
}

# ============================================================================
# FONCTIONS D'AFFICHAGE
# ============================================================================

def display_archive_card(archive_data):
    """Affiche une carte pour une archive"""
    with st.container(border=True):
        col1, col2 = st.columns([3, 1])
        with col1:
            st.subheader(archive_data['label'])
            st.markdown(f"""
            **📅 Période :** {archive_data['date']}  
            **📂 Cote :** `{archive_data['cote']}`  
            **📍 Localisation :** {archive_data['location']}  
            **🔓 Accès :** {archive_data['access']}  
            **📝 Description :** {archive_data['content']}
            """)
        with col2:
            st.metric("État", archive_data['status'])
            st.metric("Boîtes", "4", archive_data['cote'].split('/')[-1])
        
        # Badge source
        source = archive_data.get('source', 'Données de référence')
        st.caption(f"Source: {source}")

def display_thematic_analysis():
    """Affiche l'analyse thématique"""
    st.subheader("📊 Analyse thématique des documents")
    
    # Graphique des thèmes
    themes_df = pd.DataFrame(BUMIDOM_ARCHIVES_DATA['thematic_analysis']['themes'])
    
    fig = px.pie(
        themes_df, 
        values='weight', 
        names='name',
        color='name',
        color_discrete_map={t['name']: t['color'] for t in BUMIDOM_ARCHIVES_DATA['thematic_analysis']['themes']},
        title='Répartition thématique des procès-verbaux'
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig, use_container_width=True)
    
    # Frise chronologique
    st.subheader("🕰️ Frise chronologique des décisions")
    
    timeline_df = pd.DataFrame(BUMIDOM_ARCHIVES_DATA['thematic_analysis']['timeline'])
    
    # Création d'une frise interactive
    fig = go.Figure()
    
    for event_type in timeline_df['type'].unique():
        type_df = timeline_df[timeline_df['type'] == event_type]
        fig.add_trace(go.Scatter(
            x=type_df['year'],
            y=[1] * len(type_df),
            mode='markers+text',
            name=event_type.capitalize(),
            marker=dict(size=15),
            text=type_df['event'],
            textposition="top center",
            hovertemplate='<b>%{text}</b><br>Année: %{x}<extra></extra>'
        ))
    
    fig.update_layout(
        title='Événements clés documentés',
        xaxis_title='Année',
        yaxis=dict(showticklabels=False, range=[0.5, 1.5]),
        height=300,
        showlegend=True
    )
    
    st.plotly_chart(fig, use_container_width=True)

def display_research_tools():
    """Affiche les outils de recherche"""
    st.subheader("🧪 Outils de recherche qualitative")
    
    tab1, tab2, tab3 = st.tabs(["📝 Carnet de notes", "🔍 Grille d'analyse", "📚 Sources"])
    
    with tab1:
        st.markdown("""
        ### Carnet de notes de recherche
        
        Utilisez cette section pour noter vos observations lors de la consultation des archives.
        """)
        
        with st.form("research_notes"):
            date_consult = st.date_input("Date de consultation")
            cote_doc = st.text_input("Cote du document", value="20080699/")
            theme = st.selectbox("Thème", [t['name'] for t in BUMIDOM_ARCHIVES_DATA['thematic_analysis']['themes']])
            observation = st.text_area("Observation / Citation", height=150)
            
            if st.form_submit_button("💾 Sauvegarder la note"):
                st.success("Note sauvegardée (stockage local)")
                # Ici, vous pourriez sauvegarder dans un fichier JSON local
    
    with tab2:
        st.markdown("""
        ### Grille d'analyse des procès-verbaux
        
        **1. Contexte de la décision**
        - Date et lieu de la réunion
        - Participants présents
        - Ordre du jour
        
        **2. Décisions prises**
        - Recrutement et transport
        - Logement et intégration
        - Budget et financement
        - Formations proposées
        
        **3. Débats et controverses**
        - Points de désaccord
        - Arguments avancés
        - Alternatives discutées
        
        **4. Suivi et mise en œuvre**
        - Échéances fixées
        - Responsables désignés
        - Indicateurs de suivi
        """)
    
    with tab3:
        st.markdown("""
        ### Sources complémentaires
        
        **Archives Nationales**
        - Site de Pierrefitte-sur-Seine
        - 59 rue Guynemer, 93383 Pierrefitte-sur-Seine
        - Tél: 01 75 47 20 00
        
        **Archives Nationales d'Outre-mer (ANOM)**
        - 29 chemin du Moulin de Testa, 13090 Aix-en-Provence
        
        **Bibliothèque nationale de France (BnF)**
        - Site François-Mitterrand
        - Collections presse et périodiques
        
        **Bases de données en ligne**
        - Retronews (presse historique)
        - Gallica (documents numérisés)
        - Archives Portal Europe
        """)

# ============================================================================
# INTERFACE PRINCIPALE
# ============================================================================

# Sidebar
with st.sidebar:
    st.image("https://via.placeholder.com/150x50/003366/FFFFFF?text=BUMIDOM", width=150)
    st.title("Archives BUMIDOM")
    
    st.info("""
    **Mode :** Hors ligne  
    **Données :** De référence  
    **Mise à jour :** Manuelle
    """)
    
    section = st.radio(
        "Navigation",
        ["📋 Archive principale", "🔗 Archives liées", "📊 Analyse", "🛠️ Outils"]
    )

# Contenu principal
if section == "📋 Archive principale":
    st.header("Archive principale du BUMIDOM")
    display_archive_card(BUMIDOM_ARCHIVES_DATA['main_archive'])
    
    # Informations de consultation
    with st.expander("📋 Informations pratiques de consultation", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **Conditions d'accès :**
            - Inscription gratuite sur place
            - Pièce d'identité requise
            - Carnet de notes autorisé
            
            **Matériel autorisé :**
            - Ordinateur portable
            - Appareil photo (sans flash)
            - Scanner portable
            """)
        
        with col2:
            st.markdown("""
            **Horaires :**
            - Lundi-vendredi: 9h-16h45
            - Samedi: 9h-16h45
            - Fermé dimanche et jours fériés
            
            **Services :**
            - Reproduction sur demande
            - Aide à la recherche
            - Wi-Fi gratuit
            """)

elif section == "🔗 Archives liées":
    st.header("Fonds d'archives complémentaires")
    
    for i, archive in enumerate(BUMIDOM_ARCHIVES_DATA['related_archives']):
        with st.container(border=True):
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.subheader(archive['title'])
                st.markdown(f"**Période :** {archive['period']} | **Type :** {archive['type']}")
            with col2:
                st.code(archive['cote'], language="text")
            with col3:
                if st.button("📄 Détails", key=f"btn_{i}"):
                    st.session_state[f'show_{i}'] = not st.session_state.get(f'show_{i}', False)
            
            if st.session_state.get(f'show_{i}', False):
                st.markdown(f"""
                **Description :** Documents complémentaires pour contextualiser l'action du BUMIDOM.
                **Localisation :** Archives Nationales - Site de Pierrefitte
                **État :** Communicable sous réserve de dérogation
                """)

elif section == "📊 Analyse":
    st.header("Analyse des archives")
    display_thematic_analysis()
    
    # Statistiques simulées
    st.subheader("📈 Statistiques de consultation")
    
    # Données simulées de consultation
    years = list(range(1963, 1983))
    consultation_data = pd.DataFrame({
        'Année': years,
        'Documents consultés': np.random.randint(50, 200, len(years)),
        'Pages numérisées': np.random.randint(100, 500, len(years)),
        'Réunions documentées': np.random.randint(10, 30, len(years))
    })
    
    fig = px.line(
        consultation_data, 
        x='Année', 
        y=['Documents consultés', 'Pages numérisées', 'Réunions documentées'],
        title='Volume documentaire par année',
        markers=True
    )
    st.plotly_chart(fig, use_container_width=True)

else:  # 🛠️ Outils
    display_research_tools()

# ============================================================================
# PIED DE PAGE
# ============================================================================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p><strong>Dashboard Archives BUMIDOM</strong> | Version hors ligne</p>
    <p><em>Pour des données actualisées, consultez directement le site 
    <a href='https://francearchives.gouv.fr' target='_blank'>FranceArchives.gouv.fr</a></em></p>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# FONCTIONNALITÉS DE SAUVEGARDE LOCALE
# ============================================================================

# Section cachée pour l'export des données
with st.expander("💾 Export des données", expanded=False):
    st.markdown("Exportez les données de référence au format JSON")
    
    if st.button("Télécharger les données"):
        # Création du fichier JSON
        json_data = json.dumps(BUMIDOM_ARCHIVES_DATA, indent=2, ensure_ascii=False)
        
        # Téléchargement
        st.download_button(
            label="📥 Télécharger JSON",
            data=json_data,
            file_name="bumidom_archives_data.json",
            mime="application/json"
        )
