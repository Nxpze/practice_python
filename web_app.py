import os
import time
import textwrap
import numpy as np
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import create_engine
import plotly.express as px
import plotly.graph_objects as go

# ---------------------------------------------------------
# 1. PAGE CONFIGURATION
# ---------------------------------------------------------
st.set_page_config(
    page_title="Netflix User Analytics | Executive Dashboard",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load environment variables
load_dotenv()
DB_URL = os.getenv("DB_URL")

# ---------------------------------------------------------
# 2. PROFESSIONAL & CLEAN MODERN CSS
# ---------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* Global Font */
html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* Background */
.stApp {
    background-color: #111418;
    color: #E2E8F0;
}

/* Clean Professional Metric Cards */
.metric-card {
    background: #1A1F26;
    border: 1px solid #28303C;
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
    margin-bottom: 1rem;
    transition: all 0.2s ease-in-out;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
}

.metric-card:hover {
    transform: translateY(-2px);
    border-color: #E50914;
    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.35);
}

.metric-title {
    font-size: 0.8rem;
    font-weight: 600;
    color: #94A3B8;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 0.35rem;
}

.metric-val {
    font-size: 1.85rem;
    font-weight: 700;
    color: #FFFFFF;
    line-height: 1.2;
}

.metric-sub {
    font-size: 0.8rem;
    color: #64748B;
    margin-top: 0.4rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.badge-green {
    background: rgba(16, 185, 129, 0.15);
    color: #34D399;
    padding: 2px 8px;
    border-radius: 4px;
    font-weight: 600;
    font-size: 0.75rem;
}

.badge-red {
    background: rgba(239, 68, 68, 0.15);
    color: #F87171;
    padding: 2px 8px;
    border-radius: 4px;
    font-weight: 600;
    font-size: 0.75rem;
}

.badge-blue {
    background: rgba(59, 130, 246, 0.15);
    color: #60A5FA;
    padding: 2px 8px;
    border-radius: 4px;
    font-weight: 600;
    font-size: 0.75rem;
}

/* Header */
.dashboard-header {
    background: #181D24;
    border: 1px solid #28303C;
    border-radius: 12px;
    padding: 1.5rem 1.75rem;
    margin-bottom: 1.5rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 1rem;
}

/* Tab Styling */
.stTabs [data-baseweb="tab-list"] {
    gap: 6px;
    background: #181D24;
    padding: 4px;
    border-radius: 8px;
    border: 1px solid #28303C;
}

.stTabs [data-baseweb="tab"] {
    font-weight: 500;
    font-size: 0.9rem;
    color: #94A3B8;
    padding: 6px 14px;
    border-radius: 6px;
    border: none !important;
    background: transparent;
    transition: all 0.2s ease;
}

.stTabs [aria-selected="true"] {
    background: #E50914 !important;
    color: #FFFFFF !important;
    font-weight: 600;
}

.stTabs [data-baseweb="tab"]:hover {
    color: #FFFFFF;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #14171D;
    border-right: 1px solid #28303C;
}

/* Card Container */
.chart-box {
    background: #1A1F26;
    border: 1px solid #28303C;
    border-radius: 12px;
    padding: 1.25rem;
    margin-bottom: 1.25rem;
    transition: border-color 0.2s ease;
}

.chart-box:hover {
    border-color: #3B4758;
}

/* User Profile Card */
.profile-card {
    background: #181D24;
    border: 1px solid #28303C;
    border-left: 4px solid #E50914;
    border-radius: 10px;
    padding: 1.25rem;
    margin-bottom: 1rem;
}
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# 3. DATA LOADING & RESILIENT FALLBACK
# ---------------------------------------------------------
@st.cache_data(ttl=1800, show_spinner=False)
def load_netflix_dataset():
    """
    Loads data from DB_URL if available and responsive (5s timeout).
    Falls back cleanly to local CSV replica if DB is offline.
    """
    db_url = os.getenv("DB_URL")
    source_status = "UNKNOWN"
    load_time = 0.0
    start_t = time.time()
    
    if db_url:
        try:
            engine = create_engine(db_url, connect_args={"connect_timeout": 5})
            query = "SELECT * FROM netflix_titles;"
            df = pd.read_sql(query, con=engine)
            load_time = round(time.time() - start_t, 2)
            source_status = "LIVE_DATABASE"
            return df, source_status, load_time
        except Exception:
            pass

    local_path = "Dataset/netflix_user_behavior_dataset.csv"
    if os.path.exists(local_path):
        df = pd.read_csv(local_path)
        load_time = round(time.time() - start_t, 2)
        source_status = "LOCAL_REPLICA"
        return df, source_status, load_time
    else:
        raise FileNotFoundError("Could not find dataset or connect to database.")


def clean_and_prepare_data(raw_df: pd.DataFrame) -> pd.DataFrame:
    df = raw_df.copy()
    
    # Numeric column coercion
    numeric_cols = [
        'age', 'account_age_months', 'monthly_fee', 'devices_used',
        'avg_watch_time_minutes', 'watch_sessions_per_week',
        'binge_watch_sessions', 'completion_rate', 'rating_given',
        'content_interactions', 'recommendation_click_rate', 'days_since_last_login'
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Clean text columns
    cat_cols = ['gender', 'country', 'subscription_type', 'payment_method', 'primary_device', 'favorite_genre', 'churned']
    for col in cat_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
    
    # Derived flags
    if 'churned' in df.columns:
        df['is_churned'] = df['churned'].apply(lambda x: 1 if str(x).lower() in ['yes', '1', 'true'] else 0)
        df['status_label'] = df['is_churned'].apply(lambda x: 'Churned' if x == 1 else 'Active')
        
    return df


# ---------------------------------------------------------
# 4. CLEAN PLOTLY THEME
# ---------------------------------------------------------
def apply_clean_theme(fig: go.Figure, height: int = 360) -> go.Figure:
    """Applies a clean, professional dark layout to Plotly figures."""
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=height,
        margin=dict(l=15, r=15, t=35, b=15),
        font=dict(family="Inter, sans-serif", color="#CBD5E1", size=12),
        hoverlabel=dict(
            bgcolor="#1E293B",
            bordercolor="#475569",
            font=dict(family="Inter, sans-serif", color="#FFFFFF", size=12)
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=11),
            bgcolor="rgba(0,0,0,0)"
        )
    )
    fig.update_xaxes(
        showgrid=True,
        gridcolor="#262F3D",
        zerolinecolor="#262F3D",
        tickfont=dict(color="#94A3B8")
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor="#262F3D",
        zerolinecolor="#262F3D",
        tickfont=dict(color="#94A3B8")
    )
    return fig


# ---------------------------------------------------------
# 5. INITIALIZE DATA
# ---------------------------------------------------------
with st.spinner("Loading Netflix Analytics Data..."):
    raw_df, db_status, latency = load_netflix_dataset()
    df = clean_and_prepare_data(raw_df)


# ---------------------------------------------------------
# 6. SIDEBAR: FILTERS
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("""
        <div style="display:flex; align-items:center; gap:10px; margin-bottom:1rem;">
            <div style="background:#E50914; color:white; font-weight:800; font-size:1.2rem; padding:3px 9px; border-radius:6px;">N</div>
            <div>
                <div style="font-weight:700; font-size:1.1rem; color:#FFFFFF;">Netflix Analytics</div>
                <div style="font-size:0.75rem; color:#94A3B8;">User Intelligence Platform</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Status Badge
    if db_status == "LIVE_DATABASE":
        st.caption(f"🟢 Database Connected ({latency}s)")
    else:
        st.caption(f"🔵 Local Data Cache ({len(df):,} records)")

    st.markdown("---")
    st.markdown("##### 🔍 Data Filters")
    
    # Quick filter
    quick_filter = st.selectbox(
        "Quick Segment View",
        options=["All Subscribers", "Active Only", "Churned Only", "Premium Plan Only"]
    )
    
    temp_df = df.copy()
    if quick_filter == "Active Only":
        temp_df = temp_df[temp_df['is_churned'] == 0]
    elif quick_filter == "Churned Only":
        temp_df = temp_df[temp_df['is_churned'] == 1]
    elif quick_filter == "Premium Plan Only":
        temp_df = temp_df[temp_df['subscription_type'] == 'Premium']

    # Country
    all_countries = sorted(df['country'].unique().tolist())
    selected_countries = st.multiselect("Country / Region", options=all_countries, default=all_countries)
    
    # Subscription Tier
    all_tiers = sorted(df['subscription_type'].unique().tolist())
    selected_tiers = st.multiselect("Subscription Plan", options=all_tiers, default=all_tiers)
    
    # Device & Genre
    col1, col2 = st.columns(2)
    with col1:
        devices = ["All"] + sorted(df['primary_device'].unique().tolist())
        selected_device = st.selectbox("Primary Device", options=devices)
    with col2:
        genres = ["All"] + sorted(df['favorite_genre'].unique().tolist())
        selected_genre = st.selectbox("Favorite Genre", options=genres)
        
    # Age Range Slider
    min_age, max_age = int(df['age'].min()), int(df['age'].max())
    age_range = st.slider("User Age Range", min_value=min_age, max_value=max_age, value=(min_age, max_age))
    
    # Account Tenure Slider
    min_m, max_m = int(df['account_age_months'].min()), int(df['account_age_months'].max())
    tenure_range = st.slider("Account Age (Months)", min_value=min_m, max_value=max_m, value=(min_m, max_m))

    if st.button("🔄 Refresh Data Cache", width="stretch"):
        st.cache_data.clear()
        st.rerun()


# ---------------------------------------------------------
# 7. APPLY FILTERS
# ---------------------------------------------------------
filtered_df = temp_df.copy()

if selected_countries:
    filtered_df = filtered_df[filtered_df['country'].isin(selected_countries)]
if selected_tiers:
    filtered_df = filtered_df[filtered_df['subscription_type'].isin(selected_tiers)]
if selected_device != "All":
    filtered_df = filtered_df[filtered_df['primary_device'] == selected_device]
if selected_genre != "All":
    filtered_df = filtered_df[filtered_df['favorite_genre'] == selected_genre]

filtered_df = filtered_df[
    (filtered_df['age'] >= age_range[0]) & (filtered_df['age'] <= age_range[1]) &
    (filtered_df['account_age_months'] >= tenure_range[0]) & (filtered_df['account_age_months'] <= tenure_range[1])
]

if len(filtered_df) == 0:
    st.warning("No records match your selected filters. Please adjust the sidebar options.")
    st.stop()


# ---------------------------------------------------------
# 8. TOP HEADER
# ---------------------------------------------------------
st.markdown(f"""
<div class="dashboard-header">
    <div>
        <h2 style="margin:0; font-size:1.8rem; font-weight:700; color:#FFFFFF;">
            Netflix User Behavior & Retention Dashboard
        </h2>
        <p style="color:#94A3B8; margin:0.25rem 0 0 0; font-size:0.9rem;">
            Overview of viewing metrics, subscription revenue, and churn analytics.
        </p>
    </div>
    <div style="background:#222933; border:1px solid #333F4E; padding:0.6rem 1rem; border-radius:8px; text-align:right;">
        <span style="font-size:0.75rem; color:#94A3B8; display:block;">Active Data Sample</span>
        <span style="font-weight:700; font-size:1.15rem; color:#FFFFFF;">{len(filtered_df):,} <span style="font-size:0.8rem; color:#64748B;">/ {len(df):,} rows</span></span>
    </div>
</div>
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# 9. KPI METRIC CARDS
# ---------------------------------------------------------
total_users = len(filtered_df)
churn_count = filtered_df['is_churned'].sum()
churn_rate = (churn_count / total_users) * 100 if total_users > 0 else 0
total_mrr = filtered_df['monthly_fee'].sum()
avg_watch = filtered_df['avg_watch_time_minutes'].mean()
avg_rating = filtered_df['rating_given'].mean()

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Active Subscribers</div>
        <div class="metric-val">{total_users - churn_count:,}</div>
        <div class="metric-sub">
            <span class="badge-green">{100 - churn_rate:.1f}% Retained</span>
            <span>Total: {total_users:,}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Total Monthly Revenue</div>
        <div class="metric-val">${total_mrr:,.0f}</div>
        <div class="metric-sub">
            <span class="badge-blue">Avg ${filtered_df['monthly_fee'].mean():.2f}/user</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    churn_badge = "badge-red" if churn_rate > 20 else "badge-green"
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Churn Rate</div>
        <div class="metric-val" style="color:{'#F87171' if churn_rate > 20 else '#34D399'};">{churn_rate:.1f}%</div>
        <div class="metric-sub">
            <span class="{churn_badge}">{churn_count:,} Left</span>
            <span>Target: &lt;20%</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Avg Daily Watch Time</div>
        <div class="metric-val">{avg_watch:.0f} <span style="font-size:1rem; color:#94A3B8; font-weight:400;">min</span></div>
        <div class="metric-sub">
            <span class="badge-blue">{(avg_watch/60):.1f} hrs/day</span>
            <span>{filtered_df['completion_rate'].mean():.1f}% Completed</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ---------------------------------------------------------
# 10. MAIN TABS
# ---------------------------------------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Executive Summary",
    "🎬 Viewing Patterns",
    "⚠️ Churn Analysis",
    "👥 Customer Segments",
    "🔍 User Lookup & Data"
])


# =========================================================
# TAB 1: EXECUTIVE SUMMARY
# =========================================================
with tab1:
    col_t1, col_t2 = st.columns([1.5, 1])
    
    with col_t1:
        st.markdown('<div class="chart-box"><h4 style="margin:0 0 0.5rem 0;">🌍 Subscribers by Country</h4>', unsafe_allow_html=True)
        country_agg = filtered_df.groupby('country').agg(
            subscribers=('user_id', 'count'),
            mrr=('monthly_fee', 'sum'),
            churn_pct=('is_churned', lambda x: round(x.mean() * 100, 1))
        ).reset_index()
        
        fig_map = px.choropleth(
            country_agg,
            locations='country',
            locationmode='country names',
            color='subscribers',
            hover_name='country',
            hover_data={'subscribers': ':,', 'mrr': ':$,.0f', 'churn_pct': ':.1f%'},
            color_continuous_scale=[[0, '#1E293B'], [0.5, '#3B82F6'], [1, '#E50914']]
        )
        fig_map.update_geos(
            showframe=False,
            showcoastlines=True,
            coastlinecolor="#334155",
            projection_type='natural earth',
            bgcolor='rgba(0,0,0,0)',
            showland=True,
            landcolor="#1E293B",
            showocean=True,
            oceancolor="#111418"
        )
        st.plotly_chart(apply_clean_theme(fig_map, height=360), width="stretch")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_t2:
        st.markdown('<div class="chart-box"><h4 style="margin:0 0 0.5rem 0;">💳 Revenue by Subscription Plan</h4>', unsafe_allow_html=True)
        tier_agg = filtered_df.groupby('subscription_type').agg(
            revenue=('monthly_fee', 'sum'),
            users=('user_id', 'count')
        ).reset_index()
        
        fig_tier = px.pie(
            tier_agg,
            names='subscription_type',
            values='revenue',
            hole=0.55,
            color='subscription_type',
            color_discrete_map={'Premium': '#E50914', 'Standard': '#3B82F6', 'Basic': '#64748B'}
        )
        fig_tier.update_traces(
            textposition='inside',
            textinfo='percent+label',
            hovertemplate="<b>%{label}</b><br>Revenue: $%{value:,.0f}<br>Share: %{percent}<extra></extra>"
        )
        st.plotly_chart(apply_clean_theme(fig_tier, height=360), width="stretch")
        st.markdown('</div>', unsafe_allow_html=True)

    # Secondary Row
    col_t3, col_t4 = st.columns(2)
    with col_t3:
        st.markdown('<div class="chart-box"><h4 style="margin:0 0 0.5rem 0;">🏆 Top Country Ranking & Churn Rate</h4>', unsafe_allow_html=True)
        top_c = country_agg.sort_values(by='subscribers', ascending=True)
        fig_bar = go.Figure(go.Bar(
            y=top_c['country'],
            x=top_c['subscribers'],
            orientation='h',
            marker=dict(
                color=top_c['churn_pct'],
                colorscale=[[0, '#3B82F6'], [1, '#E50914']],
                colorbar=dict(title=dict(text="Churn %", font=dict(color="#CBD5E1", size=10)), thickness=10)
            ),
            hovertemplate="<b>%{y}</b><br>Subscribers: %{x:,}<br>Churn: %{marker.color:.1f}%<extra></extra>"
        ))
        st.plotly_chart(apply_clean_theme(fig_bar, height=300), width="stretch")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_t4:
        st.markdown('<div class="chart-box"><h4 style="margin:0 0 0.5rem 0;">💳 Payment Method Distribution</h4>', unsafe_allow_html=True)
        pay_agg = filtered_df.groupby(['payment_method', 'subscription_type']).size().reset_index(name='count')
        fig_pay = px.bar(
            pay_agg,
            x='payment_method',
            y='count',
            color='subscription_type',
            barmode='group',
            color_discrete_map={'Premium': '#E50914', 'Standard': '#3B82F6', 'Basic': '#64748B'}
        )
        st.plotly_chart(apply_clean_theme(fig_pay, height=300), width="stretch")
        st.markdown('</div>', unsafe_allow_html=True)


# =========================================================
# TAB 2: VIEWING PATTERNS
# =========================================================
with tab2:
    col_v1, col_v2 = st.columns(2)
    with col_v1:
        st.markdown('<div class="chart-box"><h4 style="margin:0 0 0.5rem 0;">🍿 Genre vs Daily Watch Time & Completion</h4>', unsafe_allow_html=True)
        genre_summary = filtered_df.groupby('favorite_genre').agg(
            avg_watch=('avg_watch_time_minutes', 'mean'),
            avg_comp=('completion_rate', 'mean'),
            count=('user_id', 'count')
        ).reset_index()
        
        fig_genre = px.scatter(
            genre_summary,
            x='avg_watch',
            y='avg_comp',
            size='count',
            color='favorite_genre',
            text='favorite_genre',
            size_max=32
        )
        fig_genre.update_traces(textposition='top center')
        fig_genre.update_xaxes(title="Avg Daily Watch (Mins)")
        fig_genre.update_yaxes(title="Avg Completion Rate (%)")
        st.plotly_chart(apply_clean_theme(fig_genre, height=350), width="stretch")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_v2:
        st.markdown('<div class="chart-box"><h4 style="margin:0 0 0.5rem 0;">📱 Primary Device Share</h4>', unsafe_allow_html=True)
        device_agg = filtered_df.groupby('primary_device').agg(users=('user_id', 'count')).reset_index()
        fig_dev = px.bar(
            device_agg.sort_values(by='users', ascending=False),
            x='primary_device',
            y='users',
            color='primary_device',
            color_discrete_sequence=['#E50914', '#3B82F6', '#10B981', '#F59E0B']
        )
        fig_dev.update_xaxes(title="Device Type")
        fig_dev.update_yaxes(title="Number of Users")
        st.plotly_chart(apply_clean_theme(fig_dev, height=350), width="stretch")
        st.markdown('</div>', unsafe_allow_html=True)

    col_v3, col_v4 = st.columns(2)
    with col_v3:
        st.markdown('<div class="chart-box"><h4 style="margin:0 0 0.5rem 0;">🔥 Binge Watch Sessions vs Sessions Per Week</h4>', unsafe_allow_html=True)
        fig_density = px.density_heatmap(
            filtered_df,
            x='watch_sessions_per_week',
            y='binge_watch_sessions',
            nbinsx=15,
            nbinsy=15,
            color_continuous_scale=[[0, '#1E293B'], [0.5, '#3B82F6'], [1, '#E50914']]
        )
        fig_density.update_xaxes(title="Watch Sessions / Week")
        fig_density.update_yaxes(title="Binge Sessions / Month")
        st.plotly_chart(apply_clean_theme(fig_density, height=320), width="stretch")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_v4:
        st.markdown('<div class="chart-box"><h4 style="margin:0 0 0.5rem 0;">🎯 Recommendation Click Rate vs Rating Given</h4>', unsafe_allow_html=True)
        sample_subset = filtered_df.sample(min(1200, len(filtered_df)), random_state=42)
        fig_sc = px.scatter(
            sample_subset,
            x='recommendation_click_rate',
            y='rating_given',
            color='status_label',
            color_discrete_map={'Active': '#3B82F6', 'Churned': '#E50914'},
            opacity=0.6
        )
        fig_sc.update_xaxes(title="Recommendation CTR (%)")
        fig_sc.update_yaxes(title="Rating Given (1-5 ⭐)")
        st.plotly_chart(apply_clean_theme(fig_sc, height=320), width="stretch")
        st.markdown('</div>', unsafe_allow_html=True)


# =========================================================
# TAB 3: CHURN ANALYSIS
# =========================================================
with tab3:
    st.markdown('<div class="chart-box"><h4 style="margin:0 0 0.5rem 0;">⚡ Churn Risk Estimator & Diagnostics</h4>', unsafe_allow_html=True)
    
    sc1, sc2 = st.columns([1.3, 1])
    with sc1:
        st.markdown("###### Adjust Parameters to Calculate Churn Probability")
        r1, r2 = st.columns(2)
        with r1:
            inact = st.slider("Days Inactive", 0, 60, 35)
            w_time = st.slider("Daily Watch Time (Mins)", 10, 300, 60)
        with r2:
            rating = st.slider("Rating Given", 1.0, 5.0, 2.5, 0.1)
            ctr = st.slider("Recommendation CTR (%)", 0, 100, 25)
            
        # Linear risk scoring formula
        r_score = min(100, max(0, (inact / 60.0)*50 + max(0, 1 - (w_time/200.0))*25 + max(0, 1 - (ctr/100.0))*15 + max(0, 1 - ((rating-1)/4.0))*10))
    
    with sc2:
        if r_score >= 70:
            r_label = "High Churn Risk"
            r_color = "#EF4444"
            r_action = "Urgent: Offer 30% retention discount or recommended trending shows."
        elif r_score >= 40:
            r_label = "Moderate Risk"
            r_color = "#F59E0B"
            r_action = "Action: Send weekend email digest of newly added movies in favorite genre."
        else:
            r_label = "Low Risk (Healthy)"
            r_color = "#10B981"
            r_action = "Action: Highly engaged user. Eligible for Premium 4K plan upgrade campaign."

        st.markdown(f"""
        <div style="background:#111418; border:1px solid {r_color}; border-radius:10px; padding:1.25rem; text-align:center; height:100%;">
            <div style="font-size:0.8rem; color:#94A3B8; text-transform:uppercase;">Calculated Risk Score</div>
            <div style="font-size:2.8rem; font-weight:800; color:{r_color}; margin:0.25rem 0;">{r_score:.1f}%</div>
            <div style="font-weight:600; color:{r_color}; margin-bottom:0.75rem;">{r_label}</div>
            <div style="font-size:0.85rem; color:#94A3B8; text-align:left; background:#181D24; padding:0.75rem; border-radius:6px;">
                <b>Suggested Action:</b><br>{r_action}
            </div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Churn Distribution by Inactivity
    st.markdown('<div class="chart-box"><h4 style="margin:0 0 0.5rem 0;">📊 Churn vs Inactivity (Days Since Last Login)</h4>', unsafe_allow_html=True)
    fig_hist = px.histogram(
        filtered_df,
        x='days_since_last_login',
        color='status_label',
        barmode='overlay',
        nbins=35,
        color_discrete_map={'Active': '#3B82F6', 'Churned': '#E50914'},
        opacity=0.75
    )
    fig_hist.update_xaxes(title="Days Since Last Login")
    fig_hist.update_yaxes(title="Number of Users")
    st.plotly_chart(apply_clean_theme(fig_hist, height=300), width="stretch")
    st.markdown('</div>', unsafe_allow_html=True)


# =========================================================
# TAB 4: CUSTOMER SEGMENTS
# =========================================================
with tab4:
    st.markdown('<div class="chart-box"><h4 style="margin:0 0 0.5rem 0;">👥 Behavioral Customer Personas</h4>', unsafe_allow_html=True)
    
    def get_persona(row):
        if row['avg_watch_time_minutes'] >= 200 and row['binge_watch_sessions'] >= 8:
            return "Binge Watcher"
        elif row['days_since_last_login'] >= 35:
            return "At-Risk / Dormant"
        elif row['account_age_months'] >= 24 and row['rating_given'] >= 3.5:
            return "Loyal Subscriber"
        else:
            return "Casual Streamer"

    persona_df = filtered_df.copy()
    persona_df['persona'] = persona_df.apply(get_persona, axis=1)

    pc1, pc2 = st.columns([1, 1.3])
    with pc1:
        counts = persona_df['persona'].value_counts().reset_index()
        counts.columns = ['persona', 'count']
        fig_p_pie = px.pie(
            counts,
            names='persona',
            values='count',
            hole=0.5,
            color='persona',
            color_discrete_map={
                "Binge Watcher": "#E50914",
                "Loyal Subscriber": "#3B82F6",
                "Casual Streamer": "#10B981",
                "At-Risk / Dormant": "#F59E0B"
            }
        )
        st.plotly_chart(apply_clean_theme(fig_p_pie, height=330), width="stretch")

    with pc2:
        seg_metrics = persona_df.groupby('persona').agg(
            avg_watch=('avg_watch_time_minutes', 'mean'),
            avg_monthly_fee=('monthly_fee', 'mean'),
            churn_rate=('is_churned', lambda x: round(x.mean() * 100, 1))
        ).reset_index()
        
        fig_p_bar = px.bar(
            seg_metrics,
            x='persona',
            y='churn_rate',
            color='persona',
            color_discrete_map={
                "Binge Watcher": "#E50914",
                "Loyal Subscriber": "#3B82F6",
                "Casual Streamer": "#10B981",
                "At-Risk / Dormant": "#F59E0B"
            }
        )
        fig_p_bar.update_xaxes(title="Customer Persona")
        fig_p_bar.update_yaxes(title="Churn Rate (%)")
        st.plotly_chart(apply_clean_theme(fig_p_bar, height=330), width="stretch")
    st.markdown('</div>', unsafe_allow_html=True)


# =========================================================
# TAB 5: USER LOOKUP & DATA HUB
# =========================================================
with tab5:
    col_u1, col_u2 = st.columns([1.1, 1.9])
    
    with col_u1:
        st.markdown('<div class="chart-box"><h4 style="margin:0 0 0.75rem 0;">👤 Single User Lookup</h4>', unsafe_allow_html=True)
        
        sample_ids = filtered_df['user_id'].head(3).tolist()
        default_val = str(sample_ids[0]) if sample_ids else "U100000"
        search_id = st.text_input("Enter User ID", value=default_val).strip()
        
        match = df[df['user_id'].str.strip().str.upper() == search_id.upper()]
        
        if len(match) > 0:
            u = match.iloc[0]
            is_c = str(u['churned']).lower() == 'yes'
            status_text = "CHURNED" if is_c else "ACTIVE"
            status_badge_color = "#F87171" if is_c else "#34D399"
            
            with st.container(border=True):
                col_h1, col_h2 = st.columns([2, 1])
                with col_h1:
                    st.subheader(f"🆔 {u['user_id']}")
                with col_h2:
                    st.markdown(f"<span style='color:{status_badge_color}; font-weight:700;'>● {status_text}</span>", unsafe_allow_html=True)
                
                # Profile Details
                d1, d2 = st.columns(2)
                with d1:
                    st.write(f"**Country:** {u['country']}")
                    st.write(f"**Age / Gender:** {u['age']} ({u['gender']})")
                    st.write(f"**Plan:** {u['subscription_type']}")
                    st.write(f"**Monthly Fee:** ${u['monthly_fee']:.2f}")
                    st.write(f"**Payment:** {u['payment_method']}")
                with d2:
                    st.write(f"**Device:** {u['primary_device']}")
                    st.write(f"**Favorite Genre:** {u['favorite_genre']}")
                    st.write(f"**Rating:** {u['rating_given']} ⭐")
                    st.write(f"**Tenure:** {u['account_age_months']} mos")
                    st.write(f"**Days Inactive:** {u['days_since_last_login']} d")
                
                # Watch metrics
                st.markdown("---")
                st.caption(f"Daily Watch Time: **{u['avg_watch_time_minutes']} mins** | Completion: **{u['completion_rate']}%**")
                st.progress(min(1.0, float(u['completion_rate']) / 100.0))
        else:
            st.info(f"User ID '{search_id}' not found in database.")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_u2:
        st.markdown('<div class="chart-box"><h4 style="margin:0 0 0.5rem 0;">🗂️ Data Table & Export</h4>', unsafe_allow_html=True)
        
        default_show = ['user_id', 'country', 'age', 'subscription_type', 'monthly_fee', 'favorite_genre', 'avg_watch_time_minutes', 'churned']
        cols_to_display = st.multiselect("Columns", options=filtered_df.columns.tolist(), default=default_show)
        
        col_cfg = {
            "monthly_fee": st.column_config.NumberColumn("Monthly Fee", format="$%.2f"),
            "rating_given": st.column_config.NumberColumn("Rating", format="%.1f ⭐"),
            "completion_rate": st.column_config.ProgressColumn("Completion", format="%d%%", min_value=0, max_value=100),
            "recommendation_click_rate": st.column_config.ProgressColumn("CTR", format="%d%%", min_value=0, max_value=100)
        }
        
        st.dataframe(
            filtered_df[cols_to_display].head(300),
            width="stretch",
            height=320,
            hide_index=True,
            column_config=col_cfg
        )
        
        csv_bytes = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Filtered Data as CSV",
            data=csv_bytes,
            file_name="netflix_subscribers_data.csv",
            mime="text/csv",
            width="stretch"
        )
        st.markdown('</div>', unsafe_allow_html=True)


# ---------------------------------------------------------
# 11. FOOTER
# ---------------------------------------------------------
st.markdown("""
<div style="text-align:center; padding:2rem 0 1rem 0; color:#64748B; font-size:0.8rem;">
    Netflix User Analytics Dashboard · Built with Python & Streamlit
</div>
""", unsafe_allow_html=True)