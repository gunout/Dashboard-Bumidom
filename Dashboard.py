# app_advanced.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# Configuration
st.set_page_config(
    page_title="BUMIDOM - Analyses Avancées",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé
st.markdown("""
<style>
    .big-font { font-size: 2.5rem; color: #1E3A8A; }
    .medium-font { font-size: 1.8rem; color: #2563EB; }
    .small-font { font-size: 1.2rem; color: #4B5563; }
    .highlight { background-color: #DBEAFE; padding: 10px; border-radius: 5px; }
    .insight-box { 
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .stat-card {
        background: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Titre
st.markdown('<p class="big-font">🔍 BUMIDOM - Analyses Poussées et Insights Avancés</p>', unsafe_allow_html=True)

# ============================================================================
# FONCTIONS DE CHARGEMENT DE DONNÉES SIMULÉES (À REMPLACER PAR VOS DONNÉES)
# ============================================================================

@st.cache_data
def load_comprehensive_data():
    """Charge un ensemble complet de données simulées pour analyse"""
    
    # Données migratoires principales 1963-1982
    years = list(range(1963, 1983))
    n_years = len(years)
    
    # 1. Données démographiques détaillées
    demography_data = {
        'Année': years,
        'Total_Migrations': [],
        'Guadeloupe': [],
        'Martinique': [],
        'Guyane': [],
        'Réunion': [],
        'Hommes': [],
        'Femmes': [],
        'Age_18_25': [],
        'Age_26_35': [],
        'Age_36_45': [],
        'Age_46_plus': [],
        'Mariés': [],
        'Célibataires': [],
        'Enfants_Accompagnants': []
    }
    
    # Simulation avec tendances réalistes
    base_total = 1500
    for i, year in enumerate(years):
        trend = 1 + (i * 0.08)  # Croissance de 8% par an
        seasonal = 1 + 0.2 * np.sin(2 * np.pi * i / 12)  # Variation saisonnière
        
        total = int(base_total * trend * seasonal + np.random.normal(0, 100))
        demography_data['Total_Migrations'].append(total)
        
        # Répartition par région
        demography_data['Guadeloupe'].append(int(total * 0.35 * (1 + np.random.normal(0, 0.05))))
        demography_data['Martinique'].append(int(total * 0.40 * (1 + np.random.normal(0, 0.05))))
        demography_data['Guyane'].append(int(total * 0.10 * (1 + np.random.normal(0, 0.05))))
        demography_data['Réunion'].append(int(total * 0.15 * (1 + np.random.normal(0, 0.05))))
        
        # Démographie
        demography_data['Hommes'].append(int(total * 0.55 * (1 + np.random.normal(0, 0.03))))
        demography_data['Femmes'].append(int(total * 0.45 * (1 + np.random.normal(0, 0.03))))
        
        # Tranches d'âge
        demography_data['Age_18_25'].append(int(total * 0.45))
        demography_data['Age_26_35'].append(int(total * 0.35))
        demography_data['Age_36_45'].append(int(total * 0.15))
        demography_data['Age_46_plus'].append(int(total * 0.05))
        
        # État civil
        demography_data['Mariés'].append(int(total * 0.30))
        demography_data['Célibataires'].append(int(total * 0.65))
        demography_data['Enfants_Accompagnants'].append(int(total * 0.20))
    
    df_demo = pd.DataFrame(demography_data)
    
    # 2. Données socio-économiques
    socio_economic = {
        'Année': years,
        'PIB_France_Croissance': np.random.normal(4.5, 1.5, n_years),
        'Chomage_France': np.random.normal(5.0, 1.0, n_years),
        'Salaire_Moyen_Reel': [1000 * (1.03)**i + np.random.normal(0, 50) for i in range(n_years)],
        'Cout_Vie_Index': [100 * (1.04)**i for i in range(n_years)],
        'Investissements_Publics': np.random.normal(500, 50, n_years),
        'Logements_Construits': np.random.randint(50000, 150000, n_years)
    }
    
    df_socio = pd.DataFrame(socio_economic)
    
    # 3. Données par secteur d'emploi
    secteurs = {
        'Secteur': ['BTP', 'Automobile', 'Métallurgie', 'Santé', 'Administration', 
                   'Transports', 'Nettoyage', 'Restauration', 'Agriculture'],
        'Pourcentage_1970': [35, 15, 12, 8, 10, 7, 5, 4, 4],
        'Pourcentage_1980': [30, 10, 10, 12, 15, 8, 7, 5, 3],
        'Salaire_Moyen': [1800, 2000, 2200, 2500, 2300, 1900, 1600, 1700, 1500],
        'Conditions_Travail': [2.8, 3.2, 3.5, 4.0, 4.2, 3.0, 2.5, 2.7, 2.3]  # Sur 5
    }
    
    df_secteurs = pd.DataFrame(secteurs)
    
    # 4. Données de retour et intégration
    integration = {
        'Année': years,
        'Taux_Retour_5ans': np.random.normal(0.25, 0.05, n_years),
        'Taux_Emploi_1an': np.random.normal(0.85, 0.03, n_years),
        'Duree_Chomage_Moyenne': np.random.normal(4.5, 1.0, n_years),  # mois
        'Acces_Logement_Moins_6mois': np.random.normal(0.65, 0.05, n_years),
        'Naturalisations': np.random.randint(200, 800, n_years)
    }
    
    df_integration = pd.DataFrame(integration)
    
    # 5. Données contextuelles historiques
    events = [
        {'Année': 1968, 'Evenement': 'Accords de mai', 'Impact_Migrations': -0.15},
        {'Année': 1973, 'Evenement': 'Choc pétrolier', 'Impact_Migrations': -0.25},
        {'Année': 1974, 'Evenement': 'Arrêt immigration travail', 'Impact_Migrations': -0.40},
        {'Année': 1976, 'Evenement': 'Plan social DOM', 'Impact_Migrations': 0.10},
        {'Année': 1981, 'Evenement': 'Changement politique', 'Impact_Migrations': 0.05}
    ]
    
    df_events = pd.DataFrame(events)
    
    return df_demo, df_socio, df_secteurs, df_integration, df_events

# Chargement des données
df_demo, df_socio, df_secteurs, df_integration, df_events = load_comprehensive_data()

# ============================================================================
# SIDEBAR - CONFIGURATION
# ============================================================================

with st.sidebar:
    st.image("https://via.placeholder.com/150x50/1E3A8A/FFFFFF?text=BUMIDOM", width=150)
    st.title("⚙️ Configuration des Analyses")
    
    st.subheader("Période d'analyse")
    year_range = st.slider(
        "Sélectionnez la période",
        1963, 1982, (1963, 1982)
    )
    
    st.subheader("Régions à analyser")
    regions = st.multiselect(
        "Sélectionnez les régions",
        ['Guadeloupe', 'Martinique', 'Guyane', 'Réunion'],
        default=['Guadeloupe', 'Martinique', 'Guyane', 'Réunion']
    )
    
    st.subheader("Type d'analyse")
    analysis_type = st.selectbox(
        "Choisissez le type d'analyse",
        ['Démographique', 'Socio-économique', 'Sectorielle', 'Intégration', 'Corrélations']
    )
    
    st.subheader("Paramètres statistiques")
    confidence_level = st.slider("Niveau de confiance", 0.90, 0.99, 0.95)
    show_advanced = st.checkbox("Afficher les analyses avancées")
    
    st.markdown("---")
    with st.expander("📚 À propos des données"):
        st.info("""
        **BUMIDOM (1963-1982)**:
        - 160,000 migrants environ
        - Principalement vers la métropole
        - Secteurs: BTP, industrie, services
        - Contexte: Croissance des Trente Glorieuses
        """)

# ============================================================================
# SECTION 1: ANALYSE DÉMOGRAPHIQUE AVANCÉE
# ============================================================================

if analysis_type == 'Démographique':
    st.markdown('<p class="medium-font">📈 Analyse Démographique Avancée</p>', unsafe_allow_html=True)
    
    # KPI Principaux
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_migrants = df_demo['Total_Migrations'].sum()
        st.metric("Total migrants période", f"{total_migrants:,}", "160K estimés")
    
    with col2:
        growth_rate = ((df_demo['Total_Migrations'].iloc[-1] - df_demo['Total_Migrations'].iloc[0]) / 
                      df_demo['Total_Migrations'].iloc[0] * 100)
        st.metric("Taux croissance période", f"{growth_rate:.1f}%", "1963-1982")
    
    with col3:
        avg_age = (df_demo['Age_18_25'].mean() * 21.5 + df_demo['Age_26_35'].mean() * 30.5 + 
                  df_demo['Age_36_45'].mean() * 40.5 + df_demo['Age_46_plus'].mean() * 50) / df_demo['Total_Migrations'].mean()
        st.metric("Âge moyen pondéré", f"{avg_age:.1f} ans", "Jeune population")
    
    with col4:
        gender_ratio = df_demo['Hommes'].sum() / df_demo['Femmes'].sum()
        st.metric("Ratio H/F", f"{gender_ratio:.2f}", "+ d'hommes")
    
    # Graphiques détaillés
    tab1, tab2, tab3, tab4 = st.tabs(["Évolution temporelle", "Pyramide des âges", "Analyse régionale", "Projections"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            # Évolution avec tendance
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=df_demo['Année'], 
                y=df_demo['Total_Migrations'],
                mode='lines+markers',
                name='Migrations réelles',
                line=dict(color='blue', width=2)
            ))
            
            # Ajout de la tendance linéaire
            z = np.polyfit(df_demo.index, df_demo['Total_Migrations'], 1)
            p = np.poly1d(z)
            
            fig.add_trace(go.Scatter(
                x=df_demo['Année'],
                y=p(df_demo.index),
                mode='lines',
                name='Tendance linéaire',
                line=dict(color='red', width=2, dash='dash')
            ))
            
            # Événements historiques
            for _, event in df_events.iterrows():
                fig.add_vline(
                    x=event['Année'],
                    line_width=2,
                    line_dash="dot",
                    line_color="green",
                    annotation_text=event['Evenement']
                )
            
            fig.update_layout(
                title='Évolution avec tendance et événements marquants',
                xaxis_title='Année',
                yaxis_title='Nombre de migrants',
                height=500
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Analyse saisonnière et cycles
            fig = make_subplots(
                rows=2, cols=1,
                subplot_titles=('Composante saisonnière', 'Décomposition tendance-saisonnalité')
            )
            
            # Simulation de données mensuelles
            months = pd.date_range(start='1963-01', end='1982-12', freq='M')
            seasonal_pattern = np.sin(2 * np.pi * np.arange(len(months)) / 12)
            trend = np.arange(len(months)) * 0.5
            noise = np.random.normal(0, 50, len(months))
            monthly_data = 1000 + trend + 200 * seasonal_pattern + noise
            
            fig.add_trace(
                go.Scatter(x=months, y=seasonal_pattern * 200, mode='lines', name='Saisonnalité'),
                row=1, col=1
            )
            
            fig.add_trace(
                go.Scatter(x=months, y=monthly_data, mode='lines', name='Données mensuelles simulées'),
                row=2, col=1
            )
            
            fig.update_layout(height=500, showlegend=True)
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        # Pyramide des âges interactive
        year_selected = st.slider("Sélectionnez l'année pour la pyramide", 1963, 1982, 1975)
        
        year_data = df_demo[df_demo['Année'] == year_selected].iloc[0]
        
        ages_male = [
            year_data['Age_18_25'] * 0.55,
            year_data['Age_26_35'] * 0.55,
            year_data['Age_36_45'] * 0.55,
            year_data['Age_46_plus'] * 0.55
        ]
        
        ages_female = [
            year_data['Age_18_25'] * 0.45,
            year_data['Age_26_35'] * 0.45,
            year_data['Age_36_45'] * 0.45,
            year_data['Age_46_plus'] * 0.45
        ]
        
        age_groups = ['18-25 ans', '26-35 ans', '36-45 ans', '46+ ans']
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            y=age_groups,
            x=[-x for x in ages_male],
            name='Hommes',
            orientation='h',
            marker=dict(color='powderblue')
        ))
        
        fig.add_trace(go.Bar(
            y=age_groups,
            x=ages_female,
            name='Femmes',
            orientation='h',
            marker=dict(color='seagreen')
        ))
        
        fig.update_layout(
            title=f'Pyramide des âges des migrants - {year_selected}',
            barmode='relative',
            xaxis=dict(
                title='Nombre de migrants',
                tickvals=[-3000, -2000, -1000, 0, 1000, 2000, 3000],
                ticktext=['3000', '2000', '1000', '0', '1000', '2000', '3000']
            ),
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Analyse statistique de la distribution d'âge
        st.markdown("#### Analyse statistique de la distribution par âge")
        
        age_distribution = np.concatenate([
            np.full(int(year_data['Age_18_25']), 21.5),
            np.full(int(year_data['Age_26_35']), 30.5),
            np.full(int(year_data['Age_36_45']), 40.5),
            np.full(int(year_data['Age_46_plus']), 50)
        ])
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Moyenne d'âge", f"{np.mean(age_distribution):.1f} ans")
        with col2:
            st.metric("Médiane d'âge", f"{np.median(age_distribution):.1f} ans")
        with col3:
            st.metric("Écart-type", f"{np.std(age_distribution):.1f} ans")
    
    with tab3:
        # Analyse comparative régionale
        st.markdown("#### Analyse comparative des régions d'origine")
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Évolution comparative', 'Parts relatives',
                          'Croissance cumulée', 'Variabilité annuelle'),
            specs=[[{'type': 'scatter'}, {'type': 'pie'}],
                   [{'type': 'bar'}, {'type': 'box'}]]
        )
        
        # Graphique 1: Évolution
        for region in ['Guadeloupe', 'Martinique', 'Guyane', 'Réunion']:
            fig.add_trace(
                go.Scatter(x=df_demo['Année'], y=df_demo[region], name=region),
                row=1, col=1
            )
        
        # Graphique 2: Parts relatives
        total_by_region = [df_demo[region].sum() for region in ['Guadeloupe', 'Martinique', 'Guyane', 'Réunion']]
        fig.add_trace(
            go.Pie(labels=['Guadeloupe', 'Martinique', 'Guyane', 'Réunion'], 
                   values=total_by_region),
            row=1, col=2
        )
        
        # Graphique 3: Croissance cumulée
        cumulative = df_demo[['Guadeloupe', 'Martinique', 'Guyane', 'Réunion']].cumsum()
        for i, region in enumerate(['Guadeloupe', 'Martinique', 'Guyane', 'Réunion']):
            fig.add_trace(
                go.Bar(x=df_demo['Année'], y=cumulative[region], name=region),
                row=2, col=1
            )
        
        # Graphique 4: Variabilité (box plot)
        fig.add_trace(
            go.Box(y=df_demo['Guadeloupe'], name='Guadeloupe'),
            row=2, col=2
        )
        fig.add_trace(
            go.Box(y=df_demo['Martinique'], name='Martinique'),
            row=2, col=2
        )
        
        fig.update_layout(height=700, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        
        # Analyse ANOVA entre régions (simulée)
        st.markdown("#### Test d'hypothèse: Différences significatives entre régions")
        
        # Simulation de données pour ANOVA
        np.random.seed(42)
        data_guadeloupe = np.random.normal(df_demo['Guadeloupe'].mean(), df_demo['Guadeloupe'].std(), 1000)
        data_martinique = np.random.normal(df_demo['Martinique'].mean(), df_demo['Martinique'].std(), 1000)
        
        # Test t simulé
        t_stat, p_value = stats.ttest_ind(data_guadeloupe, data_martinique)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Statistique t", f"{t_stat:.4f}")
        with col2:
            st.metric("p-value", f"{p_value:.6f}")
            
        if p_value < 0.05:
            st.success("Différence statistiquement significative entre les régions (p < 0.05)")
        else:
            st.warning("Pas de différence statistiquement significative entre les régions")
    
    with tab4:
        # Modélisation et projections
        st.markdown("#### Modélisation et projections")
        
        # Régression polynomiale
        X = df_demo.index.values
        y = df_demo['Total_Migrations'].values
        
        # Ajustement polynomial degré 3
        coeffs = np.polyfit(X, y, 3)
        poly = np.poly1d(coeffs)
        
        # Projection
        future_years = list(range(1983, 1990))
        future_X = list(range(len(X), len(X) + len(future_years)))
        projections = poly(future_X)
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df_demo['Année'], y=y,
            mode='lines+markers',
            name='Données réelles',
            line=dict(color='blue')
        ))
        
        fig.add_trace(go.Scatter(
            x=future_years, y=projections,
            mode='lines+markers',
            name='Projection',
            line=dict(color='red', dash='dash')
        ))
        
        # Intervalle de confiance
        residuals = y - poly(X)
        std_residuals = np.std(residuals)
        ci_upper = projections + 1.96 * std_residuals
        ci_lower = projections - 1.96 * std_residuals
        
        fig.add_trace(go.Scatter(
            x=future_years + future_years[::-1],
            y=list(ci_upper) + list(ci_lower[::-1]),
            fill='toself',
            fillcolor='rgba(255,0,0,0.2)',
            line=dict(color='rgba(255,255,255,0)'),
            name='Intervalle de confiance 95%'
        ))
        
        fig.update_layout(
            title='Projection des migrations avec intervalle de confiance',
            xaxis_title='Année',
            yaxis_title='Nombre de migrants',
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Metrics de qualité du modèle
        r_squared = 1 - np.sum(residuals**2) / np.sum((y - np.mean(y))**2)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("R² du modèle", f"{r_squared:.4f}")
        with col2:
            st.metric("Erreur moyenne", f"{np.mean(np.abs(residuals)):.0f}")
        with col3:
            st.metric("Projection 1990", f"{int(projections[-1]):,}")

# ============================================================================
# SECTION 2: ANALYSE SOCIO-ÉCONOMIQUE
# ============================================================================

elif analysis_type == 'Socio-économique':
    st.markdown('<p class="medium-font">💼 Analyse Socio-économique Contextuelle</p>', unsafe_allow_html=True)
    
    # Fusion des données
    df_merged = pd.merge(df_demo, df_socio, on='Année')
    df_merged = pd.merge(df_merged, df_integration, on='Année')
    
    # Corrélations
    st.markdown("#### Matrice de corrélation entre variables")
    
    corr_columns = ['Total_Migrations', 'PIB_France_Croissance', 'Chomage_France', 
                   'Salaire_Moyen_Reel', 'Cout_Vie_Index', 'Taux_Emploi_1an']
    
    corr_matrix = df_merged[corr_columns].corr()
    
    fig = px.imshow(
        corr_matrix,
        text_auto='.2f',
        color_continuous_scale='RdBu',
        zmin=-1, zmax=1,
        title='Corrélations entre migrations et indicateurs économiques'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Insights des corrélations
    st.markdown("#### Insights clés des corrélations")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        corr_pib = corr_matrix.loc['Total_Migrations', 'PIB_France_Croissance']
        st.metric(
            "Corrélation avec PIB",
            f"{corr_pib:.3f}",
            "Positive" if corr_pib > 0 else "Négative"
        )
    
    with col2:
        corr_chomage = corr_matrix.loc['Total_Migrations', 'Chomage_France']
        st.metric(
            "Corrélation avec chômage",
            f"{corr_chomage:.3f}",
            "Évite chômage élevé" if corr_chomage < 0 else "Coïncide"
        )
    
    with col3:
        corr_salaire = corr_matrix.loc['Total_Migrations', 'Salaire_Moyen_Reel']
        st.metric(
            "Corrélation avec salaire",
            f"{corr_salaire:.3f}",
            "Attiré par salaires" if corr_salaire > 0 else "Indépendant"
        )
    
    # Analyse de régression multiple
    st.markdown("#### Analyse de régression multiple")
    
    # Préparation des données
    from sklearn.preprocessing import StandardScaler
    from sklearn.linear_model import LinearRegression
    
    X_vars = ['PIB_France_Croissance', 'Chomage_France', 'Salaire_Moyen_Reel']
    X = df_merged[X_vars].values
    y = df_merged['Total_Migrations'].values
    
    # Standardisation
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Régression
    model = LinearRegression()
    model.fit(X_scaled, y)
    
    # Affichage des coefficients
    coef_df = pd.DataFrame({
        'Variable': X_vars,
        'Coefficient': model.coef_,
        'Importance_absolue': np.abs(model.coef_)
    }).sort_values('Importance_absolue', ascending=False)
    
    fig = px.bar(
        coef_df,
        x='Variable',
        y='Coefficient',
        title='Importance relative des facteurs économiques',
        color='Coefficient',
        color_continuous_scale='RdYlBu'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Analyse d'impact des événements
    st.markdown("#### Analyse d'impact des événements historiques")
    
    impact_data = []
    for _, event in df_events.iterrows():
        year = event['Année']
        if year in df_merged['Année'].values:
            actual = df_merged[df_merged['Année'] == year]['Total_Migrations'].values[0]
            
            # Estimation de ce qui aurait été attendu (moyenne mobile)
            prev_years = df_merged[(df_merged['Année'] >= year-3) & (df_merged['Année'] < year)]
            expected = prev_years['Total_Migrations'].mean() if len(prev_years) > 0 else actual
            
            impact = (actual - expected) / expected * 100
            
            impact_data.append({
                'Événement': event['Evenement'],
                'Année': year,
                'Impact_Estimé': impact,
                'Impact_Théorique': event['Impact_Migrations'] * 100
            })
    
    impact_df = pd.DataFrame(impact_data)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=impact_df['Événement'],
        y=impact_df['Impact_Estimé'],
        name='Impact estimé',
        marker_color='coral'
    ))
    
    fig.add_trace(go.Scatter(
        x=impact_df['Événement'],
        y=impact_df['Impact_Théorique'],
        mode='markers+lines',
        name='Impact théorique',
        marker=dict(size=10, color='navy')
    ))
    
    fig.update_layout(
        title="Impact des événements historiques sur les migrations",
        xaxis_title="Événement",
        yaxis_title="Impact (%)",
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# SECTION 3: ANALYSE SECTORIELLE
# ============================================================================

elif analysis_type == 'Sectorielle':
    st.markdown('<p class="medium-font">🏭 Analyse Sectorielle des Emplois</p>', unsafe_allow_html=True)
    
    # Vue d'ensemble
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.sunburst(
            df_secteurs,
            path=['Secteur'],
            values='Pourcentage_1970',
            title='Répartition sectorielle 1970',
            color='Salaire_Moyen',
            color_continuous_scale='Viridis'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.sunburst(
            df_secteurs,
            path=['Secteur'],
            values='Pourcentage_1980',
            title='Répartition sectorielle 1980',
            color='Salaire_Moyen',
            color_continuous_scale='Viridis'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Évolution sectorielle
    st.markdown("#### Évolution de la structure sectorielle 1970-1980")
    
    # Préparation des données pour le graphique en cascade
    df_secteurs['Evolution'] = df_secteurs['Pourcentage_1980'] - df_secteurs['Pourcentage_1970']
    df_secteurs = df_secteurs.sort_values('Pourcentage_1970', ascending=False)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=df_secteurs['Secteur'],
        y=df_secteurs['Pourcentage_1970'],
        name='1970',
        marker_color='lightblue'
    ))
    
    fig.add_trace(go.Bar(
        x=df_secteurs['Secteur'],
        y=df_secteurs['Evolution'],
        name='Évolution 1970-1980',
        marker_color=['green' if x > 0 else 'red' for x in df_secteurs['Evolution']]
    ))
    
    fig.update_layout(
        barmode='stack',
        title='Évolution de la répartition sectorielle',
        xaxis_title='Secteur',
        yaxis_title='Pourcentage',
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Analyse qualité emploi vs salaire
    st.markdown("#### Relation entre qualité d'emploi et salaire moyen")
    
    fig = px.scatter(
        df_secteurs,
        x='Salaire_Moyen',
        y='Conditions_Travail',
        size='Pourcentage_1980',
        color='Secteur',
        hover_name='Secteur',
        title='Salaire vs Conditions de travail par secteur',
        labels={
            'Salaire_Moyen': 'Salaire moyen (francs/mois)',
            'Conditions_Travail': 'Indice conditions de travail (1-5)'
        }
    )
    
    # Ajout de lignes de référence
    fig.add_hline(y=df_secteurs['Conditions_Travail'].mean(), 
                 line_dash="dash", line_color="red",
                 annotation_text="Moyenne conditions")
    
    fig.add_vline(x=df_secteurs['Salaire_Moyen'].mean(), 
                 line_dash="dash", line_color="blue",
                 annotation_text="Moyenne salaire")
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Analyse de concentration
    st.markdown("#### Analyse de concentration sectorielle (Indice de Herfindahl-Hirschman)")
    
    # Calcul HHI
    hhi_1970 = np.sum((df_secteurs['Pourcentage_1970'] / 100) ** 2) * 10000
    hhi_1980 = np.sum((df_secteurs['Pourcentage_1980'] / 100) ** 2) * 10000
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("HHI 1970", f"{hhi_1970:.0f}", 
                 "Concentration modérée" if hhi_1970 < 1500 else "Concentré")
    
    with col2:
        st.metric("HHI 1980", f"{hhi_1980:.0f}", 
                 f"{'Moins concentré' if hhi_1980 < hhi_1970 else 'Plus concentré'}")
    
    with col3:
        change_hhi = ((hhi_1980 - hhi_1970) / hhi_1970 * 100)
        st.metric("Évolution HHI", f"{change_hhi:.1f}%",
                 "Diversification" if change_hhi < 0 else "Concentration")
    
    # Recommandations stratégiques
    st.markdown("#### Recommandations stratégiques basées sur l'analyse sectorielle")
    
    with st.expander("📋 Voir les recommandations détaillées"):
        st.markdown("""
        **1. Secteurs prioritaires pour l'intégration:**
        - Santé et Administration: bons salaires et conditions
        - Métallurgie: bon équilibre salaire/conditions
        
        **2. Secteurs à surveiller:**
        - BTP: concentration importante, conditions difficiles
        - Nettoyage/Restauration: salaires bas
        
        **3. Évolution positive:**
        - Croissance des services (santé, administration)
        - Légère diversification de l'économie
        
        **4. Actions recommandées:**
        - Formation ciblée vers les secteurs en croissance
        - Amélioration conditions dans les secteurs difficiles
        - Suivi rapproché de la qualité de l'emploi
        """)

# ============================================================================
# SECTION 4: ANALYSE D'INTÉGRATION
# ============================================================================

elif analysis_type == 'Intégration':
    st.markdown('<p class="medium-font">🏠 Analyse de l\'Intégration et du Retour</p>', unsafe_allow_html=True)
    
    # Métriques d'intégration
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_return = df_integration['Taux_Retour_5ans'].mean() * 100
        st.metric("Taux de retour moyen (5 ans)", f"{avg_return:.1f}%", "1 migrant sur 4")
    
    with col2:
        avg_employment = df_integration['Taux_Emploi_1an'].mean() * 100
        st.metric("Emploi à 1 an", f"{avg_employment:.1f}%", "Bonne intégration")
    
    with col3:
        avg_housing = df_integration['Acces_Logement_Moins_6mois'].mean() * 100
        st.metric("Logement en < 6 mois", f"{avg_housing:.1f}%", "Accès relativement rapide")
    
    with col4:
        total_naturalizations = df_integration['Naturalisations'].sum()
        st.metric("Naturalisations totales", f"{total_naturalizations:,}", "Intégration longue")
    
    # Analyse temporelle de l'intégration
    st.markdown("#### Évolution des indicateurs d'intégration")
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Taux de retour (5 ans)', 'Taux d\'emploi (1 an)',
                       'Durée chômage moyenne', 'Accès au logement (<6 mois)'),
        specs=[[{'type': 'scatter'}, {'type': 'scatter'}],
               [{'type': 'scatter'}, {'type': 'scatter'}]]
    )
    
    fig.add_trace(
        go.Scatter(x=df_integration['Année'], y=df_integration['Taux_Retour_5ans']*100,
                  mode='lines+markers', name='Retour'),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(x=df_integration['Année'], y=df_integration['Taux_Emploi_1an']*100,
                  mode='lines+markers', name='Emploi'),
        row=1, col=2
    )
    
    fig.add_trace(
        go.Scatter(x=df_integration['Année'], y=df_integration['Duree_Chomage_Moyenne'],
                  mode='lines+markers', name='Chômage'),
        row=2, col=1
    )
    
    fig.add_trace(
        go.Scatter(x=df_integration['Année'], y=df_integration['Acces_Logement_Moins_6mois']*100,
                  mode='lines+markers', name='Logement'),
        row=2, col=2
    )
    
    fig.update_layout(height=600, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
    
    # Analyse des corrélations avec les migrations
    st.markdown("#### Relation entre flux migratoires et indicateurs d'intégration")
    
    df_merged_int = pd.merge(df_demo[['Année', 'Total_Migrations']], df_integration, on='Année')
    
    fig = px.scatter_matrix(
        df_merged_int,
        dimensions=['Total_Migrations', 'Taux_Retour_5ans', 'Taux_Emploi_1an', 
                   'Acces_Logement_Moins_6mois'],
        color='Année',
        title='Relations multivariées entre migrations et intégration',
        height=700
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Modèle de prédiction du retour
    st.markdown("#### Modèle prédictif du taux de retour")
    
    # Préparation des données
    X_retour = df_merged_int[['Total_Migrations', 'Taux_Emploi_1an', 'Duree_Chomage_Moyenne']]
    y_retour = df_merged_int['Taux_Retour_5ans']
    
    # Régression simple
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.model_selection import train_test_split
    
    X_train, X_test, y_train, y_test = train_test_split(X_retour, y_retour, test_size=0.2, random_state=42)
    
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Importance des features
    feature_importance = pd.DataFrame({
        'Variable': X_retour.columns,
        'Importance': model.feature_importances_
    }).sort_values('Importance', ascending=False)
    
    fig = px.bar(
        feature_importance,
        x='Variable',
        y='Importance',
        title='Importance des facteurs dans la prédiction du retour',
        color='Importance',
        color_continuous_scale='Teal'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Analyse de survie (simulée)
    st.markdown("#### Analyse de survie: durée de séjour avant retour")
    
    # Simulation de données de survie
    np.random.seed(42)
    n_sim = 1000
    durations = np.random.exponential(scale=10, size=n_sim)  # en années
    events = np.random.binomial(1, 0.7, n_sim)  # 70% de retours observés
    
    # Courbe de survie de Kaplan-Meier
    from lifelines import KaplanMeierFitter
    
    kmf = KaplanMeierFitter()
    kmf.fit(durations, event_observed=events)
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=kmf.timeline,
        y=kmf.survival_function_['KM_estimate'],
        mode='lines',
        name='Fonction de survie',
        line=dict(color='blue', width=2)
    ))
    
    # Intervalle de confiance
    fig.add_trace(go.Scatter(
        x=np.concatenate([kmf.timeline, kmf.timeline[::-1]]),
        y=np.concatenate([kmf.confidence_interval_['KM_estimate_lower_0.95'],
                         kmf.confidence_interval_['KM_estimate_upper_0.95'][::-1]]),
        fill='toself',
        fillcolor='rgba(0,100,80,0.2)',
        line=dict(color='rgba(255,255,255,0)'),
        name='IC 95%'
    ))
    
    fig.update_layout(
        title='Courbe de survie: Probabilité de rester en métropole',
        xaxis_title='Années depuis migration',
        yaxis_title='Probabilité de non-retour',
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Statistiques de survie
    median_survival = kmf.median_survival_time_
    survival_5y = kmf.predict(5)
    survival_10y = kmf.predict(10)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Médiane de survie", f"{median_survival:.1f} ans")
    with col2:
        st.metric("Survie à 5 ans", f"{survival_5y.values[0]*100:.1f}%")
    with col3:
        st.metric("Survie à 10 ans", f"{survival_10y.values[0]*100:.1f}%")

# ============================================================================
# SECTION 5: ANALYSE DE CORRÉLATIONS AVANCÉE
# ============================================================================

else:
    st.markdown('<p class="medium-font">🔗 Analyse de Corrélations et Réseaux</p>', unsafe_allow_html=True)
    
    # Fusion de toutes les données
    df_all = pd.merge(df_demo, df_socio, on='Année')
    df_all = pd.merge(df_all, df_integration, on='Année')
    
    # Matrice de corrélation complète
    st.markdown("#### Matrice de corrélation complète")
    
    corr_matrix_full = df_all.select_dtypes(include=[np.number]).corr()
    
    fig = px.imshow(
        corr_matrix_full,
        text_auto='.2f',
        color_continuous_scale='RdBu_r',
        zmin=-1, zmax=1,
        title='Matrice de corrélations complète',
        width=1000,
        height=800
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Analyse en composantes principales (simplifiée)
    st.markdown("#### Analyse en Composantes Principales (ACP)")
    
    # Sélection des variables pour ACP
    acp_vars = ['Total_Migrations', 'PIB_France_Croissance', 'Chomage_France',
               'Salaire_Moyen_Reel', 'Taux_Emploi_1an', 'Taux_Retour_5ans',
               'Age_18_25', 'Age_26_35']
    
    df_acp = df_all[acp_vars].dropna()
    
    # Standardisation
    from sklearn.decomposition import PCA
    from sklearn.preprocessing import StandardScaler
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df_acp)
    
    # ACP
    pca = PCA(n_components=2)
    principal_components = pca.fit_transform(X_scaled)
    
    df_pca = pd.DataFrame(data=principal_components, columns=['PC1', 'PC2'])
    df_pca['Année'] = df_all['Année'].iloc[:len(df_pca)]
    
    # Graphique des composantes
    fig = px.scatter(
        df_pca,
        x='PC1',
        y='PC2',
        color='Année',
        hover_name='Année',
        title='Projection des années sur les deux premières composantes principales',
        labels={'PC1': f'Composante 1 ({pca.explained_variance_ratio_[0]*100:.1f}%)',
                'PC2': f'Composante 2 ({pca.explained_variance_ratio_[1]*100:.1f}%)'}
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Cercle des corrélations
    st.markdown("#### Cercle des corrélations")
    
    # Calcul des corrélations avec les composantes
    components = pca.components_
    fig = go.Figure()
    
    # Ajout des variables
    for i, var in enumerate(acp_vars):
        fig.add_trace(go.Scatter(
            x=[0, components[0, i]],
            y=[0, components[1, i]],
            mode='lines+markers+text',
            name=var,
            text=[None, var],
            textposition="top center",
            line=dict(width=2)
        ))
    
    # Cercle unité
    theta = np.linspace(0, 2*np.pi, 100)
    fig.add_trace(go.Scatter(
        x=np.cos(theta),
        y=np.sin(theta),
        mode='lines',
        name='Cercle unité',
        line=dict(color='gray', dash='dash')
    ))
    
    fig.update_layout(
        title='Cercle des corrélations',
        xaxis_title='Composante 1',
        yaxis_title='Composante 2',
        showlegend=True,
        height=600
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Analyse de clustering
    st.markdown("#### Analyse de clustering des années")
    
    from sklearn.cluster import KMeans
    
    # Détermination du nombre optimal de clusters
    wcss = []
    max_clusters = 10
    
    for i in range(1, max_clusters+1):
        kmeans = KMeans(n_clusters=i, random_state=42, n_init=10)
        kmeans.fit(X_scaled)
        wcss.append(kmeans.inertia_)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=list(range(1, max_clusters+1)),
        y=wcss,
        mode='lines+markers',
        name='WCSS'
    ))
    
    fig.update_layout(
        title='Méthode du coude pour déterminer le nombre de clusters',
        xaxis_title='Nombre de clusters',
        yaxis_title='WCSS (Within-Cluster Sum of Squares)',
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Application du clustering
    optimal_clusters = 4  # Déterminé visuellement
    kmeans = KMeans(n_clusters=optimal_clusters, random_state=42, n_init=10)
    clusters = kmeans.fit_predict(X_scaled)
    
    df_pca['Cluster'] = clusters
    
    fig = px.scatter(
        df_pca,
        x='PC1',
        y='PC2',
        color='Cluster',
        hover_name='Année',
        title=f'Clustering des années ({optimal_clusters} groupes)',
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Caractérisation des clusters
    st.markdown("#### Caractérisation des clusters identifiés")
    
    df_all['Cluster'] = list(clusters) + [np.nan] * (len(df_all) - len(clusters))
    
    cluster_stats = df_all.groupby('Cluster')[acp_vars].mean()
    
    fig = px.imshow(
        cluster_stats.T,
        text_auto='.2f',
        color_continuous_scale='Viridis',
        title='Caractéristiques moyennes par cluster',
        labels=dict(x="Cluster", y="Variable", color="Valeur moyenne")
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Analyse de série temporelle
    st.markdown("#### Analyse de série temporelle: décomposition")
    
    from statsmodels.tsa.seasonal import seasonal_decompose
    
    # Utilisation des données de migration
    ts_data = df_all.set_index('Année')['Total_Migrations']
    
    # Décomposition additive
    decomposition = seasonal_decompose(ts_data, model='additive', period=5)
    
    fig = make_subplots(
        rows=4, cols=1,
        subplot_titles=('Série originale', 'Tendance', 
                       'Saisonnalité', 'Résidus'),
        shared_xaxes=True
    )
    
    fig.add_trace(
        go.Scatter(x=ts_data.index, y=ts_data.values, name='Original'),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(x=ts_data.index, y=decomposition.trend, name='Tendance'),
        row=2, col=1
    )
    
    fig.add_trace(
        go.Scatter(x=ts_data.index, y=decomposition.seasonal, name='Saisonnalité'),
        row=3, col=1
    )
    
    fig.add_trace(
        go.Scatter(x=ts_data.index, y=decomposition.resid, name='Résidus'),
        row=4, col=1
    )
    
    fig.update_layout(height=800, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# FOOTER ET RAPPORT SYNTHÈSE
# ============================================================================

st.markdown("---")
with st.expander("📄 Générer un rapport d'analyse synthétique"):
    st.markdown("""
    ## 📊 Rapport d'Analyse BUMIDOM - Synthèse
    
    ### Principaux Insights:
    
    1. **Démographie migratoire:**
       - Population jeune (moyenne ~28 ans)
       - Majorité masculine (ratio H/F: ~1.2)
       - Forte concentration 18-35 ans
    
    2. **Dynamique temporelle:**
       - Croissance soutenue 1963-1973
       - Impact négatif du choc pétrolier 1973
       - Stabilisation après 1974
    
    3. **Facteurs économiques:**
       - Forte corrélation avec croissance PIB
       - Relation inverse avec taux de chômage
       - Attrait des secteurs à salaire moyen
    
    4. **Intégration:**
       - Taux d'emploi élevé à 1 an (~85%)
       - Taux de retour modéré (~25% en 5 ans)
       - Accès au logement relativement rapide
    
    5. **Secteurs d'emploi:**
       - Concentration dans BTP et industrie
       - Évolution vers services et administration
       - Conditions de travail variables
    
    ### Recommandations stratégiques:
    
    1. **Politiques d'accueil:**
       - Renforcer l'accompagnement à l'emploi
       - Faciliter l'accès au logement
       - Développer la formation sectorielle
    
    2. **Suivi et évaluation:**
       - Système de suivi longitudinal
       - Indicateurs qualité de l'emploi
       - Analyse coût-bénéfice des migrations
    
    3. **Perspectives historiques:**
       - Tirer les leçons du passé
       - Adapter aux nouvelles réalités économiques
       - Préserver la mémoire migratoire
    """)

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #6B7280; padding: 20px;'>
    <p><strong>Dashboard BUMIDOM - Analyses Avancées</strong></p>
    <p>Outils d'analyse: Statistiques descriptives, corrélations, modélisation, projections</p>
    <p>⚠️ Note: Les données présentées sont des simulations pour démonstration</p>
    <p>Pour les données réelles, consulter les archives nationales et les études historiques</p>
</div>
""", unsafe_allow_html=True)
