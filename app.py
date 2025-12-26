import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- 1. CONFIGURATION & STYLE (Minimalist Setup) ---
st.set_page_config(page_title="Gaming History", layout="wide", initial_sidebar_state="expanded")

# Custom CSS untuk menyembunyikan elemen yang tidak perlu dan merapikan font
st.markdown("""
<style>
    /* Mengubah background main container menjadi sedikit off-white agar mata nyaman */
    .main { background-color: #fafafa; }
    
    /* Styling Metrics agar terlihat seperti kartu premium */
    div.stMetric {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #6c757d; /* Aksen abu-abu minimalis */
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    
    /* Judul section lebih rapi */
    h2, h3 { color: #2c3e50; font-family: 'Helvetica', sans-serif; font-weight: 300; }
</style>
""", unsafe_allow_html=True)

# Palet Warna Elegan (Muted Colors)
COLOR_PALETTE = px.colors.qualitative.G10 

# --- 2. DATA LOADING ---
@st.cache_data
def load_data():
    df = pd.read_csv('data/processed/vgsales_cleaned.csv') # Pastikan path sesuai
    return df

df = load_data()

# --- 3. SIDEBAR (The Controller) ---
st.sidebar.title("🎛️ Control Panel")
st.sidebar.markdown("Filter data untuk melihat era tertentu.")

# Filter Tahun (Slider Ganda)
min_year, max_year = int(df['Year'].min()), int(df['Year'].max())
selected_years = st.sidebar.slider("Rentang Waktu", min_year, max_year, (1990, 2015))

# Filter Genre
all_genres = sorted(df['Genre'].unique())
selected_genres = st.sidebar.multiselect("Pilih Genre", all_genres, default=['Action', 'Sports', 'Role-Playing', 'Shooter'])

# Apply Filter
filtered_df = df[
    (df['Year'] >= selected_years[0]) & 
    (df['Year'] <= selected_years[1]) & 
    (df['Genre'].isin(selected_genres))
]

# --- 4. MAIN NARRATIVE ---

# HERO SECTION: The Big Picture
st.title("The Evolution of Video Games 🎮")
st.markdown(f"""
> *Sebuah eksplorasi data interaktif mengenai tren industri game global dari tahun **{selected_years[0]}** hingga **{selected_years[1]}**.*
""")

# Key Metrics Row
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Revenue", f"${filtered_df['Global_Sales'].sum():.1f}M")
col2.metric("Games Released", f"{len(filtered_df):,}")
col3.metric("Dominant Genre", filtered_df['Genre'].mode()[0])
col4.metric("Top Publisher", filtered_df['Publisher'].mode()[0])

st.markdown("---")

# CHAPTER 1: THE SHIFTING TIDES (Time Series)
st.header("1. Pergeseran Tren Genre (The Shifting Tides)")
st.markdown("Visualisasi ini menceritakan bagaimana popularitas genre berubah. Perhatikan bagaimana **Shooter** dan **Action** mulai mendominasi di tahun-tahun belakangan.")

# Kita gunakan Area Chart karena lebih bagus untuk menunjukkan 'Volume' dan 'Dominasi' dibanding Line chart biasa
sales_per_year_genre = filtered_df.groupby(['Year', 'Genre'])['Global_Sales'].sum().reset_index()

fig_area = px.area(
    sales_per_year_genre, 
    x="Year", y="Global_Sales", color="Genre",
    color_discrete_sequence=COLOR_PALETTE,
    template="simple_white" # Template minimalis (tanpa grid lines berlebih)
)
fig_area.update_layout(
    xaxis_title="Tahun",
    yaxis_title="Penjualan Global (Juta)",
    hovermode="x unified", # Tooltip yang menyatu (clean)
    legend_title="Genre",
    margin=dict(l=20, r=20, t=30, b=20)
)
st.plotly_chart(fig_area, use_container_width=True)

# CHAPTER 2: EAST VS WEST (Regional Preference)
st.markdown("---")
st.header("2. Timur vs Barat: Perbedaan Selera")
st.markdown("Pasar Jepang (JP) memiliki karakteristik yang sangat unik dibandingkan Amerika Utara (NA) dan Eropa (EU).")

col_geo1, col_geo2 = st.columns([2, 1])

with col_geo1:
    # Heatmap untuk melihat intensitas penjualan Genre vs Region
    # Kita perlu mengubah data menjadi format matriks untuk heatmap
    region_cols = ['NA_Sales', 'EU_Sales', 'JP_Sales']
    heatmap_data = filtered_df.groupby('Genre')[region_cols].sum()
    
    # Normalisasi data agar perbandingannya adil (persentase dalam baris)
    heatmap_norm = heatmap_data.div(heatmap_data.sum(axis=1), axis=0)
    
    fig_heatmap = px.imshow(
        heatmap_norm,
        labels=dict(x="Wilayah", y="Genre", color="Dominasi Pasar"),
        x=['Amerika (NA)', 'Eropa (EU)', 'Jepang (JP)'],
        color_continuous_scale="RdBu_r", # Merah ke Biru (Elegan)
        text_auto=".1%" # Menampilkan persentase otomatis
    )
    fig_heatmap.update_layout(
        title="Peta Intensitas Genre per Wilayah (Proporsi)",
        template="simple_white"
    )
    st.plotly_chart(fig_heatmap, use_container_width=True)

with col_geo2:
    st.info("""
    **Cara Membaca Heatmap:**
    * **Warna Biru:** Menunjukkan genre tersebut sangat populer/dominan di wilayah itu.
    * **Warna Merah:** Menunjukkan genre tersebut kurang diminati.
    
    Perhatikan genre *Role-Playing*. Biasanya sangat merah/biru mencolok di Jepang dibandingkan Barat.
    """)

# CHAPTER 3: THE HALL OF FAME (Details on Demand)
st.markdown("---")
st.header("3. Hall of Fame")
st.markdown("Eksplorasi detail game dengan performa tertinggi pada filter yang Anda pilih.")

# Interactive Table dengan highlight
top_games = filtered_df.nlargest(100, 'Global_Sales')[['Rank', 'Name', 'Platform', 'Year', 'Genre', 'Publisher', 'Global_Sales']]
st.dataframe(
    top_games,
    column_config={
        "Global_Sales": st.column_config.ProgressColumn(
            "Global Sales (M)",
            help="Total penjualan global dalam juta kopi",
            format="%.2f",
            min_value=0,
            max_value=top_games['Global_Sales'].max(),
        ),
        "Year": st.column_config.NumberColumn("Tahun", format="%d")
    },
    hide_index=True,
    use_container_width=True,
    height=400
)

# Footer Minimalis
st.markdown("""
<div style="text-align: center; margin-top: 50px; color: #888;">
    <small>Data Source: VGChartz | Design by Nazar Azmi</small>
</div>
""", unsafe_allow_html=True)