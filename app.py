import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- 1. CONFIGURATION & THEME SETUP ---
st.set_page_config(page_title="Video Game Sales Report Dashboard", layout="wide", initial_sidebar_state="expanded")

# Custom CSS untuk Dark Mode & Glassmorphism
st.markdown("""
<style>
    /* Main Background */
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #161B22;
        border-right: 1px solid #30363D;
    }
    
    /* Custom Metric Card (Glassmorphism) */
    div.css-1r6slb0, div.stMetric {
        background-color: rgba(255, 255, 255, 0.05); /* Transparan */
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    
    div.stMetric:hover {
        background-color: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.3);
    }
    
    /* Typography Colors */
    h1, h2, h3 {
        color: #FFFFFF !important;
        font-family: 'Inter', sans-serif;
    }
    
    h1 {
        background: linear-gradient(90deg, #00C9FF 0%, #92FE9D 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }

    /* Metric Values Colors */
    div[data-testid="stMetricValue"] {
        color: #00C9FF !important;
        font-weight: 700;
    }
    
    div[data-testid="stMetricLabel"] {
        color: #B0B0B0 !important;
    }
    
    /* Chart Containers */
    .stPlotlyChart {
        background-color: rgba(255, 255, 255, 0.02);
        border-radius: 10px;
        padding: 10px;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
</style>
""", unsafe_allow_html=True)

# Palet Warna Neon untuk Dark Mode
NEON_PALETTE = ['#00E5FF', '#FF2975', '#F2FF49', '#8C1EFF', '#00FF94', '#FF901F']
REGION_COLORS = {'NA_Sales': '#00E5FF', 'EU_Sales': '#F2FF49', 'JP_Sales': '#FF2975', 'Other_Sales': '#8C1EFF'}

# --- 2. DATA LOADING ---
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('data/processed/vgsales_cleaned.csv')
    except:
        df = pd.read_csv('vgsales_cleaned.csv')
    return df

try:
    df = load_data()
except Exception as e:
    st.error("Data file not found. Please ensure 'vgsales_cleaned.csv' exists.")
    st.stop()

# --- 3. SIDEBAR CONTROLS ---
with st.sidebar:
    st.title("🎛️ Command Center")
    st.markdown("---")
    
    # Range Tahun
    min_year, max_year = int(df['Year'].min()), int(df['Year'].max())
    selected_years = st.slider("📅 Periode Waktu", min_year, max_year, (1995, 2016))
    
    # Filter Genre
    all_genres = sorted(df['Genre'].unique())
    selected_genres = st.multiselect("🎭 Filter Genre", all_genres, default=['Action', 'Sports', 'Role-Playing', 'Shooter'])
    
    # Filter Platform
    all_platforms = sorted(df['Platform'].unique())
    selected_platforms = st.multiselect("🎮 Filter Platform", all_platforms, default=['Wii', 'PS3', 'X360', 'DS', 'PS2'])
    
    # Publisher (Optional)
    all_publishers = sorted(df['Publisher'].unique())
    selected_publisher = st.selectbox("🏢 Publisher (Opsional)", ["All Publishers"] + all_publishers)
    
    st.markdown("---")
    if st.button("🔄 Reset Filters", type="primary"):
        st.rerun()

# Apply Filters
filtered_df = df[
    (df['Year'] >= selected_years[0]) & 
    (df['Year'] <= selected_years[1]) & 
    (df['Genre'].isin(selected_genres)) &
    (df['Platform'].isin(selected_platforms))
]

if selected_publisher != "All Publishers":
    filtered_df = filtered_df[filtered_df['Publisher'] == selected_publisher]

# Helper function untuk styling grafik konsisten
def update_chart_layout(fig, title=""):
    fig.update_layout(
        title=dict(text=title, font=dict(size=18, color="white")),
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color="#B0B0B0"),
        margin=dict(t=50, l=20, r=20, b=20),
        hovermode="x unified"
    )
    return fig

# --- 4. MAIN DASHBOARD ---

st.title("Video Game Sales Dashboard 🚀")
st.markdown(f"Market intelligence dashboard for video games from **{selected_years[0]}** to **{selected_years[1]}**.")

# KPI CARDS
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Revenue", f"${filtered_df['Global_Sales'].sum():,.1f}M", "Global")
with col2:
    st.metric("Games Released", f"{len(filtered_df):,}", "Titles")
with col3:
    top_genre = filtered_df['Genre'].mode()[0] if not filtered_df.empty else "-"
    st.metric("Top Genre", top_genre)
with col4:
    top_pub = filtered_df['Publisher'].mode()[0] if not filtered_df.empty else "-"
    st.metric("Top Publisher", top_pub)

st.markdown("---")

# CHAPTER 1: TRENDS
st.header("1. Market Trends & Evolution")

tab1, tab2 = st.tabs(["🌊 Stream Area", "📊 Stacked Bar"])

with tab1:
    sales_yearly = filtered_df.groupby(['Year', 'Genre'])['Global_Sales'].sum().reset_index()
    fig_area = px.area(
        sales_yearly, x="Year", y="Global_Sales", color="Genre",
        color_discrete_sequence=NEON_PALETTE
    )
    update_chart_layout(fig_area, "")
    st.plotly_chart(fig_area, use_container_width=True)

with tab2:
    fig_bar = px.bar(
        sales_yearly, x="Year", y="Global_Sales", color="Genre",
        color_discrete_sequence=NEON_PALETTE
    )
    update_chart_layout(fig_bar, "")
    st.plotly_chart(fig_bar, use_container_width=True)

# CHAPTER 2: REGIONAL
st.markdown("---")
st.header("2. Regional Dominance")

col_reg1, col_reg2 = st.columns([2, 1])

with col_reg1:
    st.subheader("Scatter Analysis")
    c1, c2 = st.columns(2)
    x_ax = c1.selectbox("X-Axis", ['NA_Sales', 'EU_Sales', 'JP_Sales', 'Other_Sales'], index=0)
    y_ax = c2.selectbox("Y-Axis", ['NA_Sales', 'EU_Sales', 'JP_Sales', 'Other_Sales'], index=2)
    
    # Ambil sample untuk scatter agar tidak terlalu berat visualnya
    scatter_data = filtered_df.nlargest(500, 'Global_Sales')
    
    fig_scat = px.scatter(
        scatter_data, x=x_ax, y=y_ax, color="Genre", size="Global_Sales",
        hover_name="Name", color_discrete_sequence=NEON_PALETTE, opacity=0.8
    )
    update_chart_layout(fig_scat, f"{x_ax} vs {y_ax}")
    st.plotly_chart(fig_scat, use_container_width=True)

with col_reg2:
    st.subheader("Market Share")
    reg_sum = filtered_df[['NA_Sales', 'EU_Sales', 'JP_Sales', 'Other_Sales']].sum().reset_index()
    reg_sum.columns = ['Region', 'Sales']
    
    fig_pie = px.pie(
        reg_sum, values='Sales', names='Region', color='Region',
        color_discrete_map=REGION_COLORS, hole=0.5
    )
    update_chart_layout(fig_pie)
    fig_pie.update_traces(textinfo='percent+label', textposition='inside')
    fig_pie.update_layout(showlegend=False)
    st.plotly_chart(fig_pie, use_container_width=True)

# Heatmap
st.subheader("Genre Preferences by Region")
hm_data = filtered_df.groupby('Genre')[['NA_Sales', 'EU_Sales', 'JP_Sales', 'Other_Sales']].sum()
# Normalisasi
hm_norm = hm_data.div(hm_data.sum(axis=1), axis=0)

fig_hm = px.imshow(
    hm_norm, x=['North America', 'Europe', 'Japan', 'Other'],
    labels=dict(color="Share"), color_continuous_scale="Viridis", text_auto=".0%"
)
update_chart_layout(fig_hm)
st.plotly_chart(fig_hm, use_container_width=True)

# CHAPTER 3: PLATFORM WARS (Logic Reverted to Filtered DF)
st.markdown("---")
st.header("3. The Console Wars")
st.caption("Menampilkan tren penjualan platform berdasarkan filter yang Anda pilih.")

# Menggunakan filtered_df langsung (Sesuai Permintaan)
# Jika user memilih 'Wii' di sidebar, maka hanya garis 'Wii' yang muncul.
plat_trend = filtered_df.groupby(['Year', 'Platform'])['Global_Sales'].sum().reset_index()

fig_war = px.line(
    plat_trend, x="Year", y="Global_Sales", color="Platform",
    line_shape="spline", markers=True,
    color_discrete_sequence=px.colors.qualitative.Bold 
)
update_chart_layout(fig_war, f"Platform Trends ({selected_years[0]}-{selected_years[1]})")
st.plotly_chart(fig_war, use_container_width=True)

# CHAPTER 4: HALL OF FAME
st.markdown("---")
st.header("4. Hall of Fame 🏆")

top_games = filtered_df.nlargest(100, 'Global_Sales')[['Rank', 'Name', 'Platform', 'Year', 'Genre', 'Publisher', 'Global_Sales']]

st.dataframe(
    top_games,
    column_config={
        "Name": st.column_config.TextColumn("Game Title", width="large"),
        "Global_Sales": st.column_config.ProgressColumn(
            "Global Sales (M)", format="$%.2f", min_value=0, max_value=top_games['Global_Sales'].max()
        ),
        "Year": st.column_config.NumberColumn("Year", format="%d")
    },
    use_container_width=True,
    hide_index=True,
    height=500
)

# Footer
# st.markdown("""
# <br>
# <div style="text-align: center; color: #555; padding: 20px;">
#     Developed with ❤️ using Streamlit & Plotly
# </div>
# """, unsafe_allow_html=True)