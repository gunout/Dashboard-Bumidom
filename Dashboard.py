import streamlit as st
import pandas as pd

# Correction du tableau récapitulatif dans la section "Vue d'ensemble"

def display_source_summary():
    """Affiche le tableau récapitulatif des sources avec des liens cliquables"""
    
    st.subheader("📋 Tableau récapitulatif des sources")
    
    # Créer le tableau avec les liens
    source_summary = []
    
    for source_id, source_data in BUMIDOM_ARCHIVES.items():
        # Compter le nombre de documents
        doc_count = 0
        for doc_type in ['documents', 'articles', 'videos', 'datasets', 'websites']:
            doc_count += len(source_data.get(doc_type, []))
        
        # Déterminer le type principal
        if 'documents' in source_data:
            main_type = '📄 Archives'
        elif 'articles' in source_data:
            main_type = '📰 Presse'
        elif 'videos' in source_data:
            main_type = '🎥 Audiovisuel'
        elif 'datasets' in source_data:
            main_type = '📈 Données'
        else:
            main_type = '🌐 Web'
        
        # Déterminer l'URL principale
        main_url = ""
        if source_id == 'archives_nationales':
            main_url = 'https://www.archives-nationales.culture.gouv.fr/'
        elif source_id == 'retronews':
            main_url = 'https://www.retronews.fr/'
        elif source_id == 'gallica':
            main_url = 'https://gallica.bnf.fr/'
        elif source_id == 'ina':
            main_url = 'https://www.ina.fr/'
        elif source_id == 'insee':
            main_url = 'https://www.insee.fr/'
        elif source_id == 'archive_org':
            main_url = 'https://archive.org/'
        elif source_id == 'anom':
            main_url = 'https://www.archives-nationales.culture.gouv.fr/anom/fr/'
        
        source_summary.append({
            'Source': f"{source_data['icon']} {source_data['name']}",
            'Documents': doc_count,
            'Type': main_type,
            'Accès': '🟢 Gratuit' if source_id in ['retronews', 'gallica', 'insee', 'archive_org'] else '🟡 Sur place',
            'Lien': main_url
        })
    
    # Convertir en DataFrame
    source_df = pd.DataFrame(source_summary)
    
    # Afficher avec des liens cliquables
    for idx, row in source_df.iterrows():
        with st.container(border=True):
            col1, col2, col3, col4 = st.columns([2, 1, 1, 2])
            
            with col1:
                st.markdown(f"**{row['Source']}**")
            
            with col2:
                st.metric("Documents", row['Documents'])
            
            with col3:
                st.write(row['Type'])
                st.write(row['Accès'])
            
            with col4:
                if row['Lien']:
                    st.link_button("🌐 Visiter le site", row['Lien'])
                else:
                    st.info("Pas de site web")

# ============================================================================
# VERSION ALTERNATIVE : Tableau interactif avec HTML
# ============================================================================

def display_source_summary_html():
    """Affiche le tableau avec des liens HTML cliquables"""
    
    st.subheader("📋 Tableau récapitulatif des sources")
    
    # Données des sources
    sources_data = [
        {
            'icon': '📄',
            'nom': 'Archives Nationales',
            'documents': 8,
            'type': 'Archives officielles',
            'acces': 'Sur place / En ligne',
            'url': 'https://www.archives-nationales.culture.gouv.fr/',
            'description': 'Fonds principal BUMIDOM'
        },
        {
            'icon': '📰',
            'nom': 'RetroNews (BnF)',
            'documents': 246,
            'type': 'Presse historique',
            'acces': 'Gratuit en ligne',
            'url': 'https://www.retronews.fr/search?q=bumidom',
            'description': 'Articles de presse 1963-1982'
        },
        {
            'icon': '📖',
            'nom': 'Gallica (BnF)',
            'documents': 42,
            'type': 'Livres et rapports',
            'acces': 'Gratuit en ligne',
            'url': 'https://gallica.bnf.fr/services/engine/search/sru?operation=searchRetrieve&version=1.2&query=(bumidom)',
            'description': 'Rapports officiels numérisés'
        },
        {
            'icon': '🎥',
            'nom': 'INA',
            'documents': 18,
            'type': 'Archives audiovisuelles',
            'acces': 'Gratuit (extraits)',
            'url': 'https://www.ina.fr/advanced-search?q=bumidom',
            'description': 'Reportages et interviews'
        },
        {
            'icon': '📈',
            'nom': 'INSEE',
            'documents': 12,
            'type': 'Données statistiques',
            'acces': 'Gratuit en ligne',
            'url': 'https://www.insee.fr/fr/statistiques?q=migration+dom',
            'description': 'Statistiques migratoires'
        },
        {
            'icon': '🌐',
            'nom': 'Archive.org',
            'documents': 24,
            'type': 'Sites web archivés',
            'acces': 'Gratuit en ligne',
            'url': 'https://web.archive.org/web/*/bumidom',
            'description': 'Versions archivées de sites'
        },
        {
            'icon': '🏝️',
            'nom': 'Archives Nationales d\'Outre-mer',
            'documents': 15,
            'type': 'Archives DOM-TOM',
            'acces': 'Sur place',
            'url': 'https://www.archivesnationales.culture.gouv.fr/anom/fr/',
            'description': 'Archives des préfectures'
        }
    ]
    
    # Créer un tableau HTML avec des liens
    html_table = """
    <style>
    .sources-table {
        width: 100%;
        border-collapse: collapse;
        margin: 20px 0;
        font-family: Arial, sans-serif;
    }
    .sources-table th {
        background-color: #1E3A8A;
        color: white;
        padding: 12px;
        text-align: left;
        border: 1px solid #ddd;
    }
    .sources-table td {
        padding: 12px;
        border: 1px solid #ddd;
        vertical-align: top;
    }
    .sources-table tr:nth-child(even) {
        background-color: #f8f9fa;
    }
    .sources-table tr:hover {
        background-color: #e9ecef;
    }
    .source-link {
        color: #1E3A8A;
        text-decoration: none;
        font-weight: bold;
    }
    .source-link:hover {
        text-decoration: underline;
        color: #3B82F6;
    }
    .badge {
        display: inline-block;
        padding: 4px 8px;
        border-radius: 12px;
        font-size: 0.8em;
        margin: 2px;
    }
    .badge-archive { background-color: #dbeafe; color: #1e40af; }
    .badge-presse { background-color: #fef3c7; color: #92400e; }
    .badge-data { background-color: #dcfce7; color: #166534; }
    .badge-video { background-color: #fae8ff; color: #86198f; }
    </style>
    
    <table class="sources-table">
        <thead>
            <tr>
                <th>Source</th>
                <th>Documents</th>
                <th>Type</th>
                <th>Accès</th>
                <th>Lien direct</th>
                <th>Description</th>
            </tr>
        </thead>
        <tbody>
    """
    
    for source in sources_data:
        # Déterminer la classe du badge selon le type
        badge_class = ""
        if 'Archive' in source['type']:
            badge_class = "badge-archive"
        elif 'Presse' in source['type']:
            badge_class = "badge-presse"
        elif 'Données' in source['type']:
            badge_class = "badge-data"
        elif 'Audiovisuel' in source['type']:
            badge_class = "badge-video"
        
        html_table += f"""
        <tr>
            <td><strong>{source['icon']} {source['nom']}</strong></td>
            <td><strong>{source['documents']}</strong></td>
            <td><span class="badge {badge_class}">{source['type']}</span></td>
            <td>{source['acces']}</td>
            <td><a href="{source['url']}" target="_blank" class="source-link">🔗 Visiter</a></td>
            <td>{source['description']}</td>
        </tr>
        """
    
    html_table += """
        </tbody>
    </table>
    """
    
    # Afficher le tableau HTML
    st.markdown(html_table, unsafe_allow_html=True)
    
    # Ajouter des boutons d'accès rapide
    st.subheader("🚀 Accès rapide aux principales sources")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.link_button("📰 RetroNews - Articles BUMIDOM", 
                      "https://www.retronews.fr/search?q=bumidom")
    
    with col2:
        st.link_button("📖 Gallica - Rapports BUMIDOM", 
                      "https://gallica.bnf.fr/services/engine/search/sru?operation=searchRetrieve&version=1.2&query=(bumidom)")
    
    with col3:
        st.link_button("🎥 INA - Vidéos BUMIDOM", 
                      "https://www.ina.fr/advanced-search?q=bumidom")

# ============================================================================
# VERSION STREAMLIT NATIVE (Recommandée)
# ============================================================================

def display_sources_with_expanders():
    """Affiche les sources avec des expanders Streamlit"""
    
    st.subheader("📚 Sources d'archives du BUMIDOM")
    
    # Définir les sources avec toutes les informations
    sources = [
        {
            'name': 'Archives Nationales',
            'icon': '📄',
            'description': 'Fonds principal du BUMIDOM (1962-1981)',
            'url': 'https://www.archives-nationales.culture.gouv.fr/',
            'search_url': 'https://www.siv.archives-nationales.culture.gouv.fr/siv/rechercheconsultation/consultation/ir/consultationIR.action?irId=FRAN_IR_001514',
            'doc_count': '8 cotes principales',
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
            'doc_count': '246+ articles',
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
            'doc_count': '42 documents',
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
            'doc_count': '18 vidéos',
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
            'doc_count': '12 jeux de données',
            'access': 'Gratuit en ligne',
            'key_docs': [
                'Flux migratoires DOM-métropole (1962-1982)',
                'Caractéristiques socio-économiques (1968-1982)',
                'Impact démographique (1975-1990)'
            ]
        },
        {
            'name': 'Archive.org',
            'icon': '🌐',
            'description': 'Archives du web',
            'url': 'https://archive.org/',
            'search_url': 'https://web.archive.org/web/*/bumidom',
            'doc_count': '24 captures',
            'access': 'Gratuit en ligne',
            'key_docs': [
                'Site de documentation BUMIDOM (2005-2010)',
                'Articles universitaires (1998-2015)'
            ]
        },
        {
            'name': 'ANOM',
            'icon': '🏝️',
            'description': 'Archives d\'Outre-mer',
            'url': 'https://www.archivesnationales.culture.gouv.fr/anom/fr/',
            'search_url': 'https://www.archivesnationales.culture.gouv.fr/anom/fr/Rechercher/Archives-en-ligne.html?q=bumidom',
            'doc_count': '15 boîtes',
            'access': 'Sur place (Aix-en-Provence)',
            'key_docs': [
                'Archives préfectures DOM (1958-1985)'
            ]
        }
    ]
    
    # Afficher chaque source dans un expander
    for source in sources:
        with st.expander(f"{source['icon']} **{source['name']}** - {source['doc_count']}", expanded=False):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"**Description:** {source['description']}")
                st.markdown(f"**Accès:** {source['access']}")
                
                st.markdown("**Documents clés:**")
                for doc in source['key_docs']:
                    st.markdown(f"- {doc}")
            
            with col2:
                # Boutons d'accès
                if source['search_url']:
                    st.link_button("🔍 Rechercher BUMIDOM", source['search_url'])
                
                if source['url']:
                    st.link_button("🌐 Site principal", source['url'])
                
                # Métrique
                st.metric("Documents", source['doc_count'].split()[0])
    
    # Tableau synthétique
    st.subheader("📊 Synthèse des sources")
    
    # Créer un DataFrame pour le tableau
    summary_data = []
    for source in sources:
        summary_data.append({
            'Source': f"{source['icon']} {source['name']}",
            'Documents': source['doc_count'],
            'Accès': '🟢 En ligne' if 'Gratuit' in source['access'] else '🟡 Sur place',
            'Recherche': source['search_url'],
            'Site': source['url']
        })
    
    # Afficher avec st.dataframe et column configuration
    df = pd.DataFrame(summary_data)
    
    # Configuration des colonnes pour les liens
    st.dataframe(
        df,
        column_config={
            "Source": st.column_config.TextColumn(
                "Source",
                width="medium",
            ),
            "Documents": st.column_config.TextColumn(
                "Documents",
                width="small",
            ),
            "Accès": st.column_config.TextColumn(
                "Accès",
                width="small",
            ),
            "Recherche": st.column_config.LinkColumn(
                "Recherche BUMIDOM",
                width="medium",
            ),
            "Site": st.column_config.LinkColumn(
                "Site principal",
                width="medium",
            )
        },
        hide_index=True,
        use_container_width=True
    )

# ============================================================================
# INTÉGRATION DANS VOTRE DASHBOARD
# ============================================================================

# Dans votre section "Vue d'ensemble", remplacez le tableau par :
st.header("📚 Sources d'archives du BUMIDOM")

# Utilisez une de ces fonctions :
display_sources_with_expanders()  # ← RECOMMANDÉ

# Ou pour un affichage plus simple :
# display_source_summary_html()

# ============================================================================
# SECTION SUPPLÉMENTAIRE : RECHERCHE UNIFIÉE
# ============================================================================

def unified_search_section():
    """Section de recherche unifiée dans toutes les sources"""
    
    st.subheader("🔍 Recherche unifiée dans toutes les sources")
    
    # Champ de recherche
    search_term = st.text_input(
        "Entrez votre recherche:",
        placeholder="Ex: migration antillaise, logement migrants, statistiques BUMIDOM...",
        key="unified_search"
    )
    
    if search_term:
        st.info(f"Recherche de: **{search_term}**")
        
        # Boutons de recherche rapide
        st.markdown("### Rechercher dans chaque source:")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.link_button(
                "📰 Rechercher dans RetroNews",
                f"https://www.retronews.fr/search?q={search_term}"
            )
            
            st.link_button(
                "📖 Rechercher dans Gallica",
                f"https://gallica.bnf.fr/services/engine/search/sru?operation=searchRetrieve&version=1.2&query=({search_term})"
            )
        
        with col2:
            st.link_button(
                "🎥 Rechercher dans l'INA",
                f"https://www.ina.fr/advanced-search?q={search_term}"
            )
            
            st.link_button(
                "📈 Rechercher dans l'INSEE",
                f"https://www.insee.fr/fr/statistiques?q={search_term}"
            )
        
        with col3:
            st.link_button(
                "🌐 Rechercher dans Archive.org",
                f"https://web.archive.org/web/*/{search_term}"
            )
            
            st.link_button(
                "📄 Rechercher FranceArchives",
                f"https://francearchives.gouv.fr/fr/search?q={search_term}"
            )
    
    # Conseils de recherche
    with st.expander("💡 Conseils de recherche avancée"):
        st.markdown("""
        **Mots-clés efficaces:**
        - `BUMIDOM` ou `Bureau migrations DOM`
        - `migration antillaise` ou `migration réunionnaise`
        - `travailleurs ultramarins`
        - `foyers migrants` ou `logement DOM`
        - `formation professionnelle DOM`
        
        **Combinaisons:**
        - `BUMIDOM ET logement`
        - `migration ET statistiques`
        - `DOM ET travail`
        
        **Périodes clés:**
        - 1963-1965 : Débuts du BUMIDOM
        - 1970-1975 : Pic des migrations
        - 1980-1982 : Fin du BUMIDOM
        """)

# Ajoutez cette section dans votre sidebar ou dans une page dédiée
unified_search_section()

# ============================================================================
# STATISTIQUES D'ACCÈS
# ============================================================================

def display_access_statistics():
    """Affiche les statistiques d'accès aux sources"""
    
    st.subheader("📊 Statistiques d'accès aux sources")
    
    # Données d'accès
    access_data = {
        'Source': ['RetroNews', 'Gallica', 'INSEE', 'Archive.org', 'INA', 'Archives Nationales', 'ANOM'],
        'Accès': ['En ligne gratuit', 'En ligne gratuit', 'En ligne gratuit', 'En ligne gratuit', 
                 'En ligne (extraits)', 'Sur place', 'Sur place'],
        'Documents en ligne': [246, 42, 12, 24, 18, 0, 0],
        'Documents totaux': [246, 42, 12, 24, 18, 1200, 500],
        'Pourcentage en ligne': [100, 100, 100, 100, 100, 0, 0]
    }
    
    df_access = pd.DataFrame(access_data)
    
    # Graphique d'accès
    fig = px.bar(
        df_access,
        x='Source',
        y=['Documents en ligne', 'Documents totaux'],
        title='Documents accessibles en ligne vs documents totaux',
        barmode='group',
        labels={'value': 'Nombre de documents', 'variable': 'Type'},
        color_discrete_sequence=['#3B82F6', '#1E3A8A']
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Tableau de statistiques
    st.dataframe(
        df_access.sort_values('Documents totaux', ascending=False),
        column_config={
            "Pourcentage en ligne": st.column_config.ProgressColumn(
                "En ligne",
                format="%d%%",
                min_value=0,
                max_value=100,
            )
        },
        use_container_width=True,
        hide_index=True
    )

# Appelez cette fonction où vous voulez afficher les statistiques
display_access_statistics()
