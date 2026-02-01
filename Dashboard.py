import streamlit as st
import pandas as pd
import plotly.express as px

# ============================================================================
# FONCTIONS CORRIGÉES
# ============================================================================

def display_sources_with_expanders():
    """Affiche les sources avec des expanders Streamlit - VERSION CORRIGÉE"""
    
    st.subheader("📚 Sources d'archives du BUMIDOM")
    
    # Définir les sources avec toutes les informations
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
        },
        {
            'name': 'Archive.org',
            'icon': '🌐',
            'description': 'Archives du web',
            'url': 'https://archive.org/',
            'search_url': 'https://web.archive.org/web/*/bumidom',
            'doc_count': '24',
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
            'doc_count': '15',
            'access': 'Sur place (Aix-en-Provence)',
            'key_docs': [
                'Archives préfectures DOM (1958-1985)'
            ]
        }
    ]
    
    # Afficher chaque source dans un expander
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
                # Boutons d'accès
                if source['search_url']:
                    st.link_button("🔍 Rechercher", source['search_url'], use_container_width=True)
                
                if source['url']:
                    st.link_button("🌐 Site principal", source['url'], use_container_width=True)
                
                # Métrique
                st.metric("Documents", source['doc_count'])

def display_access_statistics():
    """Affiche les statistiques d'accès aux sources - VERSION SIMPLIFIÉE"""
    
    st.subheader("📊 Statistiques d'accès aux sources")
    
    # Données d'accès (version simplifiée sans erreur)
    access_data = [
        {
            'Source': 'RetroNews',
            'Type': 'Presse historique',
            'Documents': 246,
            'Accès': '🟢 En ligne gratuit',
            '% en ligne': 100
        },
        {
            'Source': 'Gallica',
            'Type': 'Livres/Rapports',
            'Documents': 42,
            'Accès': '🟢 En ligne gratuit',
            '% en ligne': 100
        },
        {
            'Source': 'INSEE',
            'Type': 'Données statistiques',
            'Documents': 12,
            'Accès': '🟢 En ligne gratuit',
            '% en ligne': 100
        },
        {
            'Source': 'Archive.org',
            'Type': 'Sites web archivés',
            'Documents': 24,
            'Accès': '🟢 En ligne gratuit',
            '% en ligne': 100
        },
        {
            'Source': 'INA',
            'Type': 'Audiovisuel',
            'Documents': 18,
            'Accès': '🟡 En ligne (extraits)',
            '% en ligne': 100
        },
        {
            'Source': 'Archives Nationales',
            'Type': 'Archives officielles',
            'Documents': 1200,
            'Accès': '🔴 Sur place uniquement',
            '% en ligne': 0
        },
        {
            'Source': 'ANOM',
            'Type': 'Archives Outre-mer',
            'Documents': 500,
            'Accès': '🔴 Sur place uniquement',
            '% en ligne': 0
        }
    ]
    
    # Convertir en DataFrame
    df_access = pd.DataFrame(access_data)
    
    # 1. Graphique à barres simple
    st.markdown("### 📈 Nombre de documents par source")
    
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
    
    # Personnaliser le graphique
    fig.update_layout(
        height=400,
        showlegend=True,
        xaxis_title="Source d'archive",
        yaxis_title="Nombre de documents"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 2. Tableau interactif
    st.markdown("### 📋 Tableau récapitulatif")
    
    # Afficher avec st.dataframe
    st.dataframe(
        df_access.sort_values('Documents', ascending=False),
        column_config={
            "Source": st.column_config.TextColumn("Source", width="medium"),
            "Type": st.column_config.TextColumn("Type", width="medium"),
            "Documents": st.column_config.NumberColumn("Documents", format="%d"),
            "Accès": st.column_config.TextColumn("Accès", width="medium"),
            "% en ligne": st.column_config.ProgressColumn(
                "% en ligne",
                format="%d%%",
                min_value=0,
                max_value=100,
                width="medium"
            )
        },
        use_container_width=True,
        hide_index=True
    )
    
    # 3. Métriques résumées
    st.markdown("### 🎯 Résumé")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_online = df_access[df_access['Accès'].str.contains('En ligne')]['Documents'].sum()
        st.metric("Documents en ligne", f"{total_online:,}")
    
    with col2:
        total_all = df_access['Documents'].sum()
        st.metric("Documents totaux", f"{total_all:,}")
    
    with col3:
        percentage = (total_online / total_all * 100) if total_all > 0 else 0
        st.metric("% en ligne", f"{percentage:.1f}%")

def unified_search_section():
    """Section de recherche unifiée dans toutes les sources"""
    
    st.subheader("🔍 Recherche dans toutes les sources")
    
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
            
            st.link_button(
                "🎥 INA - Archives audiovisuelles",
                f"https://www.ina.fr/advanced-search?q={search_term}",
                use_container_width=True
            )
        
        with col2:
            st.link_button(
                "📈 INSEE - Statistiques",
                f"https://www.insee.fr/fr/statistiques?q={search_term}",
                use_container_width=True
            )
            
            st.link_button(
                "🌐 Archive.org - Sites archivés",
                f"https://web.archive.org/web/*/{search_term}",
                use_container_width=True
            )
            
            st.link_button(
                "📄 FranceArchives",
                f"https://francearchives.gouv.fr/fr/search?q={search_term}",
                use_container_width=True
            )
    
    # Conseils de recherche
    with st.expander("💡 Conseils de recherche avancée", expanded=False):
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

# ============================================================================
# PAGE DÉDIÉE AUX SOURCES - Version complète et fonctionnelle
# ============================================================================

def sources_page():
    """Page dédiée aux sources d'archives - VERSION FONCTIONNELLE"""
    
    st.title("🔗 Sources d'Archives du BUMIDOM")
    st.markdown("*Accédez directement à toutes les archives disponibles en ligne*")
    
    # 1. Tableau récapitulatif
    display_sources_with_expanders()
    
    st.markdown("---")
    
    # 2. Recherche unifiée
    unified_search_section()
    
    st.markdown("---")
    
    # 3. Statistiques d'accès
    display_access_statistics()
    
    st.markdown("---")
    
    # 4. Guide d'utilisation
    with st.expander("📖 Guide d'utilisation des archives", expanded=False):
        st.markdown("""
        ### Comment utiliser ces sources ?
        
        **1. Pour les chercheurs:**
        - Commencez par **RetroNews** pour le contexte médiatique
        - Puis **Gallica** pour les rapports officiels
        - Complétez avec **INSEE** pour les données statistiques
        
        **2. Pour les étudiants:**
        - **Archives Nationales** : Documents originaux
        - **INA** : Témoignages audiovisuels
        - **Archive.org** : Documentation complémentaire
        
        **3. Pour le grand public:**
        - **RetroNews** : Articles accessibles
        - **INA** : Vidéos historiques
        - **Gallica** : Documents numérisés
        
        ### ⚠️ Limitations connues
        
        | Source | Limitation | Solution |
        |--------|------------|----------|
        | Archives Nationales | Consultation sur place | Planifier une visite |
        | INA | Extraits gratuits seulement | Demander les droits |
        | INSEE | Données agrégées | Contacter le service statistique |
        
        ### 📞 Contacts utiles
        
        - **Archives Nationales** : 01 75 47 20 00
        - **BnF (Gallica/RetroNews)** : 01 53 79 59 59
        - **INA** : 01 49 83 20 00
        - **INSEE** : 09 72 72 40 00
        """)

# ============================================================================
# INTÉGRATION DANS VOTRE DASHBOARD
# ============================================================================

# Dans votre sidebar, ajoutez cette option :
sidebar_options = [
    "📊 Vue d'ensemble",
    "🔍 Exploreur d'archives", 
    "📈 Analyses thématiques",
    "🕰️ Chronologie",
    "🔗 Sources d'archives",  # ← NOUVELLE OPTION
    "🧮 Outils de recherche",
    "📥 Export & Rapport"
]

# Dans votre logique principale :
page = st.sidebar.radio("Navigation", sidebar_options)

if page == "🔗 Sources d'archives":
    sources_page()
elif page == "📊 Vue d'ensemble":
    # Votre code existant...
    pass
# ... autres pages
