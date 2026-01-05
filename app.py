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
# --- 3. SIDEBAR CONTROLS ---
with st.sidebar:
    st.title("🎛️ Command Center")
    st.markdown("---")
    
    # Range Tahun (Tetap)
    min_year, max_year = int(df['Year'].min()), int(df['Year'].max())
    selected_years = st.slider("📅 Periode Waktu", min_year, max_year, (1995, 2016))
    
    # ---------------------------------------------------------
    # FILTER GENRE (Hybrid: All + Multiselect)
    # ---------------------------------------------------------
    all_genres = sorted(df['Genre'].unique())
    # Tambahkan opsi 'ALL GENRES' di paling awal list
    genre_options = ['ALL GENRES'] + all_genres
    
    # Default-nya kita set ke 'ALL GENRES' agar langsung muncul semua data
    selected_genres_raw = st.multiselect("🎭 Filter Genre", genre_options, default=['ALL GENRES'])
    
    # LOGIKA PINTAR:
    # 1. Jika user memilih 'ALL GENRES', maka kita anggap dia memilih semua genre.
    # 2. Jika user memilih genre spesifik (Action, Puzzle), kita pakai pilihan itu.
    # 3. Jika kosong, kita anggap semua (fail-safe).
    
    if 'ALL GENRES' in selected_genres_raw or not selected_genres_raw:
        final_selected_genres = all_genres # Pakai list asli (tanpa string 'ALL GENRES')
        # Opsional: Jika user memilih 'ALL' + 'Action', kita bisa memaksa UI hanya menampilkan 'ALL'
        # tapi di backend tetap load semua.
    else:
        final_selected_genres = selected_genres_raw

    # ---------------------------------------------------------
    # FILTER PLATFORM (Hybrid: All + Multiselect)
    # ---------------------------------------------------------
    all_platforms = sorted(df['Platform'].unique())
    platform_options = ['ALL PLATFORMS'] + all_platforms
    
    selected_platforms_raw = st.multiselect("🎮 Filter Platform", platform_options, default=['ALL PLATFORMS'])
    
    if 'ALL PLATFORMS' in selected_platforms_raw or not selected_platforms_raw:
        final_selected_platforms = all_platforms
    else:
        final_selected_platforms = selected_platforms_raw
    
    # Publisher (Biarkan Selectbox karena datanya terlalu banyak untuk multiselect)
    all_publishers = sorted(df['Publisher'].unique())
    selected_publisher = st.selectbox("🏢 Publisher (Opsional)", ["All Publishers"] + all_publishers)
    
    st.markdown("---")
    if st.button("🔄 Reset Filters", type="primary"):
        st.rerun()

# Apply Filters
filtered_df = df[
    (df['Year'] >= selected_years[0]) & 
    (df['Year'] <= selected_years[1]) &
    (df['Genre'].isin(final_selected_genres)) &      # Gunakan variabel hasil logika pintar tadi
    (df['Platform'].isin(final_selected_platforms))   # Gunakan variabel hasil logika pintar tadi
]

# Logika Filter Publisher (Tetap Selectbox)
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
st.markdown(f"Dashboard Intelijen Pasar untuk Video Game dari tahun **{selected_years[0]}** sampai **{selected_years[1]}**.")

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
if not filtered_df.empty:
    # Cari platform dengan penjualan tertinggi
    top_platform_sales = filtered_df.groupby('Platform')['Global_Sales'].sum().idxmax()
    top_platform_val = filtered_df.groupby('Platform')['Global_Sales'].sum().max()
    
    # Cari tahun paling cuan
    best_year = filtered_df.groupby('Year')['Global_Sales'].sum().idxmax()
    
    st.info(f"""
    💡 **Market Insight:** Pada periode **{selected_years[0]}-{selected_years[1]}**, pasar didominasi oleh platform **{top_platform_sales}** dengan total penjualan **${top_platform_val:,.1f}M**. 
    Puncak penjualan industri terjadi pada tahun **{int(best_year)}**.
    """)
else:
    st.warning("Data tidak tersedia untuk filter yang dipilih.")

# CHAPTER 1: TRENDS
st.header("1. Market Trends & Evolution")

# 1. Tambahkan Pilihan Region (Agar user bisa ganti-ganti Global, NA, EU, JP)
region_map = {
    "Global Sales": "Global_Sales",
    "North America Sales": "NA_Sales",
    "Europe Sales": "EU_Sales",
    "Japan Sales": "JP_Sales",
    "Other Regions": "Other_Sales"
}

selected_region_label = st.selectbox(
    "Pilih Wilayah Penjualan:",
    list(region_map.keys())
)
y_col = region_map[selected_region_label] # Mengambil nama kolom asli (misal: 'NA_Sales')

tab1, tab2 = st.tabs(["🌊 Stream Area", "📊 Stacked Bar"])

with tab1:
    # 2. Group by menggunakan kolom wilayah yang DIPILIH (y_col)
    sales_yearly = filtered_df.groupby(['Year', 'Genre'])[y_col].sum().reset_index()
    
    # Hitung Moving Average berdasarkan wilayah yang dipilih
    sales_total_yearly = filtered_df.groupby('Year')[y_col].sum().reset_index()
    sales_total_yearly['MA_3Year'] = sales_total_yearly[y_col].rolling(window=3).mean()

    # 3. Plot Area Chart
    fig_area = px.area(
        sales_yearly, 
        x="Year", 
        y=y_col, 
        color="Genre",
        color_discrete_sequence=NEON_PALETTE,
        # Format label agar jelas dalam 'Millions'
        labels={y_col: f"{selected_region_label} (Millions)", "Year": "Year"}
    )
    
    # Tambahkan garis tren putus-putus
    fig_area.add_scatter(
        x=sales_total_yearly['Year'], 
        y=sales_total_yearly['MA_3Year'], 
        mode='lines',
        name='3-Year Moving Avg',
        line=dict(color='white', width=3, dash='dash')
    )
    
    # Update layout agar tooltip formatnya rapi (2 desimal)
    fig_area.update_traces(hovertemplate='%{y:.2f} M') 
    update_chart_layout(fig_area, f"{selected_region_label} Trend + Moving Average")
    st.plotly_chart(fig_area, use_container_width=True)

with tab2:
    # 4. Bar Chart juga mengikuti pilihan wilayah
    fig_bar = px.bar(
        sales_yearly, 
        x="Year", 
        y=y_col, 
        color="Genre",
        color_discrete_sequence=NEON_PALETTE,
        labels={y_col: f"{selected_region_label} (Millions)", "Year": "Year"}
    )
    
    fig_bar.update_traces(hovertemplate='%{y:.2f} M')
    update_chart_layout(fig_bar, f"{selected_region_label} Breakdown by Genre")
    st.plotly_chart(fig_bar, use_container_width=True)
    
# --- CHAPTER 2: UNIVERSAL COMPARISON ---
st.markdown("---")
st.header("2. Sales Showdown ")
st.caption("Bandingkan performa penjualan antar kategori (Genre, Platform, atau Publisher).")

# 1. Pilih Kategori Perbandingan
comp_category = st.radio(
    "Pilih Kategori untuk Dibandingkan:",
    ["Genre", "Platform", "Publisher"],
    horizontal=True
)

# 2. Siapkan Data Dropdown Berdasarkan Kategori yang Dipilih
# Kita ambil list unik dari kolom yang dipilih (misal: list semua Platform)
item_list = sorted(filtered_df[comp_category].unique())

# Cek agar tidak error jika data kosong akibat filter di sidebar
if len(item_list) < 2:
    st.warning("Data tidak cukup untuk melakukan perbandingan. Coba longgarkan filter di sidebar.")
else:
    # 3. UI Perbandingan
    col_c1, col_c2 = st.columns(2)
    
    with col_c1:
        st.subheader("Kubu A 🔵")
        # Default index 0 (item pertama)
        item_a = st.selectbox(f"Pilih {comp_category} A", item_list, index=0, key='item_a')
        
        # Hitung Metrik A
        val_a = filtered_df[filtered_df[comp_category] == item_a]['Global_Sales'].sum()
        st.metric(f"Total Sales {item_a}", f"${val_a:,.1f}M")

    with col_c2:
        st.subheader("Kubu B 🔴")
        # Default index 1 (item kedua) agar tidak sama dengan A
        def_idx = 1 if len(item_list) > 1 else 0
        item_b = st.selectbox(f"Pilih {comp_category} B", item_list, index=def_idx, key='item_b')
        
        # Hitung Metrik B
        val_b = filtered_df[filtered_df[comp_category] == item_b]['Global_Sales'].sum()
        
        # Hitung Delta (Selisih Persentase)
        if val_a > 0:
            delta_val = ((val_b - val_a) / val_a) * 100
            st.metric(f"Total Sales {item_b}", f"${val_b:,.1f}M", f"{delta_val:+.1f}% vs {item_a}")
        else:
            st.metric(f"Total Sales {item_b}", f"${val_b:,.1f}M")

    # 4. Visualisasi Trend Perbandingan
    st.subheader(f"Trend Battle: {item_a} vs {item_b}")
    
    # Filter data hanya untuk 2 item yang dipilih
    comp_df = filtered_df[filtered_df[comp_category].isin([item_a, item_b])]
    
    # Grouping berdasarkan Tahun dan Kategori terpilih
    trend_comp = comp_df.groupby(['Year', comp_category])['Global_Sales'].sum().reset_index()
    
    fig_comp = px.line(
        trend_comp, 
        x='Year', 
        y='Global_Sales', 
        color=comp_category, # Warna otomatis beda berdasarkan kategori
        markers=True,
        color_discrete_sequence=['#00C9FF', '#FF2975'] # Biru vs Merah Neon
    )
    update_chart_layout(fig_comp, f"Head-to-Head History ({item_a} vs {item_b})")
    st.plotly_chart(fig_comp, use_container_width=True)
    
    # 5. Insight Tambahan (Optional)
    # Menunjukkan game terlaris dari masing-masing kubu
    col_best1, col_best2 = st.columns(2)
    with col_best1:
        best_game_a = filtered_df[filtered_df[comp_category] == item_a].nlargest(1, 'Global_Sales')
        if not best_game_a.empty:
            st.caption(f"🏆 Top Game ({item_a}): **{best_game_a.iloc[0]['Name']}**")
            
    with col_best2:
        best_game_b = filtered_df[filtered_df[comp_category] == item_b].nlargest(1, 'Global_Sales')
        if not best_game_b.empty:
            st.caption(f"🏆 Top Game ({item_b}): **{best_game_b.iloc[0]['Name']}**")
# CHAPTER 3: REGIONAL
st.markdown("---")
st.header("3. Regional Dominance")

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
    hm_norm, 
    x=['North America', 'Europe', 'Japan', 'Other'],
    labels=dict(color="Share"), 
    color_continuous_scale="Viridis", 
    text_auto=".0%",
    aspect="auto"  # <--- TAMBAHKAN INI
)

update_chart_layout(fig_hm)
st.plotly_chart(fig_hm, use_container_width=True)

# CHAPTER 4: PLATFORM WARS (Logic Reverted to Filtered DF)
st.markdown("---")
st.header("4. The Console Wars")
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


# CHAPTER 5: HALL OF FAME
st.markdown("---")
st.header("5. Hall of Fame 🏆")

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