import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sklearn.cluster import KMeans

# =====================================
# CONFIG
# =====================================

st.set_page_config(
    page_title="Dashboard Curah Hujan NTB",
    page_icon="🌧️",
    layout="wide"
)

# =====================================
# STYLE
# =====================================

st.markdown("""
<style>
.main { padding-top: 1rem; }
.metric-container {
    background-color: #f0f4f8;
    padding: 12px;
    border-radius: 10px;
    border-left: 4px solid #2196F3;
}
[data-testid="stMetricValue"] { font-size: 1.6rem; }
</style>
""", unsafe_allow_html=True)

# =====================================
# LOAD DATA
# =====================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "curah_hujan_ntb.csv")

@st.cache_data
def load_data():
    df = pd.read_csv(CSV_PATH)

    # ── Perbaiki Latitude & Longitude yang terbalik ──
    # NTB: Latitude harusnya negatif (-8 s/d -9), Longitude positif (115-120)
    swap_mask = df['Latitude'] > 0
    df.loc[swap_mask, ['Latitude', 'Longitude']] = (
        df.loc[swap_mask, ['Longitude', 'Latitude']].values
    )

    # Buat kolom periode untuk filter
    df['Periode'] = df['Dasarian'] + " — Bulan " + df['Bulan'].astype(str) + "/" + df['Tahun'].astype(str)

    return df

df_raw = load_data()

# =====================================
# K-MEANS
# =====================================

@st.cache_data
def run_kmeans(data):
    X = data[['Curah Hujan (mm)']]
    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
    data = data.copy()
    data['Cluster'] = kmeans.fit_predict(X)

    cluster_mean = (
        data.groupby('Cluster')['Curah Hujan (mm)']
        .mean()
        .sort_values()
    )
    mapping = {
        cluster_mean.index[0]: "Rendah",
        cluster_mean.index[1]: "Menengah",
        cluster_mean.index[2]: "Tinggi",
    }
    data['Kategori Cluster'] = data['Cluster'].map(mapping)

    # Elbow method
    wcss = []
    for i in range(1, 11):
        km = KMeans(n_clusters=i, random_state=42, n_init=10)
        km.fit(X)
        wcss.append(km.inertia_)

    return data, wcss

df_all, wcss = run_kmeans(df_raw)

# =====================================
# WARNA CLUSTER
# =====================================

COLOR_MAP = {
    "Rendah":   "#2196F3",
    "Menengah": "#FF9800",
    "Tinggi":   "#F44336",
}

# =====================================
# HEADER
# =====================================

st.title("🌧️ Dashboard Curah Hujan NTB")
st.markdown(
    "### Penerapan K-Means Clustering untuk Pengelompokan Intensitas "
    "Curah Hujan di Nusa Tenggara Barat"
)

# =====================================
# SIDEBAR — FILTER
# =====================================

st.sidebar.header("⚙️ Filter Data")

# Filter Periode
periodes = ["Semua"] + sorted(df_all['Periode'].unique().tolist())
periode_filter = st.sidebar.selectbox("📅 Periode", periodes)

# Filter Kabupaten/Kota
kabupaten_list = ["Semua"] + sorted(df_all['Nama Kabupaten/Kota'].unique().tolist())
kabupaten_filter = st.sidebar.selectbox("🏙️ Kabupaten/Kota", kabupaten_list)

# Filter Kategori Cluster
cluster_filter = st.sidebar.selectbox(
    "🔵 Kategori Cluster",
    ["Semua", "Rendah", "Menengah", "Tinggi"]
)

# Cari pos hujan
search = st.sidebar.text_input("🔍 Cari Pos Hujan")

# ── Terapkan filter ──
df_tampil = df_all.copy()

if periode_filter != "Semua":
    df_tampil = df_tampil[df_tampil['Periode'] == periode_filter]

if kabupaten_filter != "Semua":
    df_tampil = df_tampil[df_tampil['Nama Kabupaten/Kota'] == kabupaten_filter]

if cluster_filter != "Semua":
    df_tampil = df_tampil[df_tampil['Kategori Cluster'] == cluster_filter]

if search:
    df_tampil = df_tampil[
        df_tampil['Nama Pos Hujan'].str.contains(search, case=False, na=False)
    ]

# =====================================
# KPI
# =====================================

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("📋 Jumlah Data", len(df_tampil))
with col2:
    st.metric("🔵 Cluster", 3)
with col3:
    val = df_tampil['Curah Hujan (mm)'].mean()
    st.metric("💧 Rata-rata (mm)", f"{val:.1f}" if not pd.isna(val) else "—")
with col4:
    val = df_tampil['Curah Hujan (mm)'].max()
    st.metric("📈 Maksimum (mm)", f"{val:.1f}" if not pd.isna(val) else "—")
with col5:
    val = df_tampil['Curah Hujan (mm)'].min()
    st.metric("📉 Minimum (mm)", f"{val:.1f}" if not pd.isna(val) else "—")

st.divider()

# =====================================
# TABS
# =====================================

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Dashboard",
    "📈 Analisis",
    "🗺️ Peta",
    "📋 Data",
    "💡 Insight",
])

# ─────────────────────────────────────
# TAB 1 — DASHBOARD
# ─────────────────────────────────────

with tab1:

    if df_tampil.empty:
        st.warning("Tidak ada data untuk filter yang dipilih.")
    else:
        # Bar chart per Pos Hujan
        st.subheader("📊 Distribusi Curah Hujan per Pos Hujan")

        fig_bar = px.bar(
            df_tampil.sort_values('Curah Hujan (mm)', ascending=False),
            x='Nama Pos Hujan',
            y='Curah Hujan (mm)',
            color='Kategori Cluster',
            color_discrete_map=COLOR_MAP,
            hover_data=['Nama Kabupaten/Kota', 'Dasarian'],
            title='Curah Hujan per Pos Hujan',
            labels={'Nama Pos Hujan': 'Pos Hujan', 'Curah Hujan (mm)': 'mm'},
        )
        fig_bar.update_layout(xaxis_tickangle=-45, height=450)
        st.plotly_chart(fig_bar, use_container_width=True)

        col_a, col_b = st.columns(2)

        with col_a:
            # Pie chart proporsi cluster
            st.subheader("🥧 Proporsi Cluster")
            fig_pie = px.pie(
                df_tampil,
                names='Kategori Cluster',
                color='Kategori Cluster',
                color_discrete_map=COLOR_MAP,
                title='Proporsi Kategori Cluster',
            )
            fig_pie.update_traces(textinfo='percent+label')
            st.plotly_chart(fig_pie, use_container_width=True)

        with col_b:
            # Bar rata-rata per Kabupaten
            st.subheader("🏙️ Rata-rata per Kabupaten/Kota")
            avg_kab = (
                df_tampil.groupby('Nama Kabupaten/Kota')['Curah Hujan (mm)']
                .mean()
                .reset_index()
                .sort_values('Curah Hujan (mm)', ascending=False)
            )
            fig_kab = px.bar(
                avg_kab,
                x='Nama Kabupaten/Kota',
                y='Curah Hujan (mm)',
                title='Rata-rata Curah Hujan per Kabupaten/Kota',
                color='Curah Hujan (mm)',
                color_continuous_scale='Blues',
            )
            fig_kab.update_layout(xaxis_tickangle=-30, showlegend=False)
            st.plotly_chart(fig_kab, use_container_width=True)

# ─────────────────────────────────────
# TAB 2 — ANALISIS
# ─────────────────────────────────────

with tab2:

    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("📉 Elbow Method")
        fig_elbow = go.Figure()
        fig_elbow.add_trace(go.Scatter(
            x=list(range(1, 11)),
            y=wcss,
            mode='lines+markers',
            marker=dict(color='#2196F3', size=8),
            line=dict(width=2),
        ))
        fig_elbow.add_vline(x=3, line_dash="dash", line_color="red",
                            annotation_text="K=3 (dipilih)")
        fig_elbow.update_layout(
            title='Elbow Method — Penentuan Jumlah Cluster Optimal',
            xaxis_title='Jumlah Cluster (K)',
            yaxis_title='WCSS (Within-Cluster Sum of Squares)',
        )
        st.plotly_chart(fig_elbow, use_container_width=True)

    with col_b:
        st.subheader("📦 Box Plot per Cluster")
        fig_box = px.box(
            df_tampil if not df_tampil.empty else df_all,
            x='Kategori Cluster',
            y='Curah Hujan (mm)',
            color='Kategori Cluster',
            color_discrete_map=COLOR_MAP,
            title='Sebaran Curah Hujan per Cluster',
            category_orders={'Kategori Cluster': ['Rendah', 'Menengah', 'Tinggi']},
        )
        st.plotly_chart(fig_box, use_container_width=True)

    st.subheader("🏆 Top 10 Curah Hujan Tertinggi")
    top10 = df_tampil.nlargest(10, 'Curah Hujan (mm)') if not df_tampil.empty else df_all.nlargest(10, 'Curah Hujan (mm)')
    st.dataframe(
        top10[['Nama Pos Hujan', 'Nama Kabupaten/Kota', 'Dasarian',
               'Curah Hujan (mm)', 'Kategori Cluster']].reset_index(drop=True),
        use_container_width=True,
    )

    st.subheader("📊 Statistik Deskriptif per Cluster")
    if not df_tampil.empty:
        stats = (
            df_tampil.groupby('Kategori Cluster')['Curah Hujan (mm)']
            .describe()
            .round(2)
        )
        st.dataframe(stats, use_container_width=True)

    st.subheader("📊 Statistik Deskriptif Keseluruhan")
    if not df_tampil.empty:
        st.dataframe(
            df_tampil[['Curah Hujan (mm)']].describe().round(2),
            use_container_width=True,
        )

# ─────────────────────────────────────
# TAB 3 — PETA
# ─────────────────────────────────────

with tab3:

    st.subheader("🗺️ Sebaran Spasial Pos Hujan NTB")

    if df_tampil.empty:
        st.warning("Tidak ada data untuk filter yang dipilih.")
    else:
        df_map = df_tampil.dropna(subset=['Latitude', 'Longitude']).copy()

        # Pastikan koordinat valid (Lat: -9 s/d -8, Lon: 115 s/d 120)
        df_map = df_map[
            (df_map['Latitude'].between(-10, 0)) &
            (df_map['Longitude'].between(114, 121))
        ]

        if df_map.empty:
            st.warning("Tidak ada koordinat valid untuk ditampilkan.")
        else:
            fig_map = px.scatter_mapbox(
                df_map,
                lat="Latitude",
                lon="Longitude",
                color="Kategori Cluster",
                color_discrete_map=COLOR_MAP,
                size="Curah Hujan (mm)",
                size_max=25,
                hover_name="Nama Pos Hujan",
                hover_data={
                    'Nama Kabupaten/Kota': True,
                    'Curah Hujan (mm)': True,
                    'Dasarian': True,
                    'Kategori Cluster': True,
                    'Latitude': False,
                    'Longitude': False,
                },
                zoom=7,
                center={"lat": -8.65, "lon": 117.5},
                mapbox_style="open-street-map",
                title="Distribusi Spasial Curah Hujan NTB",
                height=550,
            )
            fig_map.update_layout(legend_title="Kategori Cluster")
            st.plotly_chart(fig_map, use_container_width=True)
            st.caption(f"Menampilkan {len(df_map)} pos hujan dari {len(df_tampil)} data terfilter.")

# ─────────────────────────────────────
# TAB 4 — DATA
# ─────────────────────────────────────

with tab4:

    st.subheader("📋 Tabel Data Hasil Clustering")

    kolom_tampil = [
        'Nama Pos Hujan', 'Nama Desa', 'Nama Kecamatan',
        'Nama Kabupaten/Kota', 'Curah Hujan (mm)',
        'Dasarian', 'Bulan', 'Tahun', 'Kategori Cluster',
    ]
    st.dataframe(
        df_tampil[kolom_tampil].reset_index(drop=True),
        use_container_width=True,
        height=450,
    )

    col_dl1, col_dl2 = st.columns(2)

    with col_dl1:
        csv = df_tampil.to_csv(index=False)
        st.download_button(
            "⬇️ Download Data Terfilter (.csv)",
            csv,
            "hasil_clustering_filtered.csv",
            "text/csv",
        )

    with col_dl2:
        csv_all = df_all.to_csv(index=False)
        st.download_button(
            "⬇️ Download Semua Data (.csv)",
            csv_all,
            "hasil_clustering_semua.csv",
            "text/csv",
        )

# ─────────────────────────────────────
# TAB 5 — INSIGHT
# ─────────────────────────────────────

with tab5:

    if df_tampil.empty:
        st.warning("Tidak ada data untuk filter yang dipilih.")
    else:
        tertinggi = df_tampil.loc[df_tampil['Curah Hujan (mm)'].idxmax()]
        terendah  = df_tampil.loc[df_tampil['Curah Hujan (mm)'].idxmin()]

        st.success(
            f"🔴 **Curah hujan tertinggi** — {tertinggi['Nama Pos Hujan']} "
            f"({tertinggi['Nama Kabupaten/Kota']}): "
            f"**{tertinggi['Curah Hujan (mm)']} mm** "
            f"[{tertinggi['Dasarian']}]"
        )
        st.info(
            f"🔵 **Curah hujan terendah** — {terendah['Nama Pos Hujan']} "
            f"({terendah['Nama Kabupaten/Kota']}): "
            f"**{terendah['Curah Hujan (mm)']} mm** "
            f"[{terendah['Dasarian']}]"
        )

        # Ringkasan per kabupaten
        st.subheader("🏙️ Ringkasan per Kabupaten/Kota")
        ringkasan = (
            df_tampil.groupby('Nama Kabupaten/Kota')
            .agg(
                Jumlah_Pos=('Nama Pos Hujan', 'count'),
                Rata_rata=('Curah Hujan (mm)', 'mean'),
                Maksimum=('Curah Hujan (mm)', 'max'),
                Minimum=('Curah Hujan (mm)', 'min'),
            )
            .round(2)
            .reset_index()
            .rename(columns={'Nama Kabupaten/Kota': 'Kabupaten/Kota'})
            .sort_values('Rata_rata', ascending=False)
        )
        st.dataframe(ringkasan, use_container_width=True)

        # Distribusi cluster per kabupaten
        st.subheader("📊 Distribusi Cluster per Kabupaten/Kota")
        cluster_kab = (
            df_tampil.groupby(['Nama Kabupaten/Kota', 'Kategori Cluster'])
            .size()
            .reset_index(name='Jumlah')
        )
        fig_stack = px.bar(
            cluster_kab,
            x='Nama Kabupaten/Kota',
            y='Jumlah',
            color='Kategori Cluster',
            color_discrete_map=COLOR_MAP,
            barmode='stack',
            title='Distribusi Kategori Cluster per Kabupaten/Kota',
            category_orders={'Kategori Cluster': ['Rendah', 'Menengah', 'Tinggi']},
        )
        fig_stack.update_layout(xaxis_tickangle=-30)
        st.plotly_chart(fig_stack, use_container_width=True)

        # Kesimpulan
        n_rendah   = len(df_tampil[df_tampil['Kategori Cluster'] == 'Rendah'])
        n_menengah = len(df_tampil[df_tampil['Kategori Cluster'] == 'Menengah'])
        n_tinggi   = len(df_tampil[df_tampil['Kategori Cluster'] == 'Tinggi'])

        st.markdown(f"""
---
## 📝 Kesimpulan

| Parameter | Nilai |
|---|---|
| Jumlah Data | **{len(df_tampil)}** |
| Jumlah Cluster | **3** |
| Rata-rata Curah Hujan | **{df_tampil['Curah Hujan (mm)'].mean():.2f} mm** |
| Curah Hujan Maksimum | **{df_tampil['Curah Hujan (mm)'].max():.2f} mm** |
| Curah Hujan Minimum | **{df_tampil['Curah Hujan (mm)'].min():.2f} mm** |

### Hasil Clustering K-Means (K=3)

| Cluster | Jumlah Pos | Keterangan |
|---|---|---|
| 🔵 Rendah | **{n_rendah}** | Intensitas curah hujan rendah |
| 🟠 Menengah | **{n_menengah}** | Intensitas curah hujan sedang |
| 🔴 Tinggi | **{n_tinggi}** | Intensitas curah hujan tinggi |

Metode K-Means berhasil mengelompokkan data curah hujan berdasarkan tingkat intensitas.
Penentuan jumlah cluster optimal (K=3) dilakukan menggunakan **Elbow Method**.
Hasil clustering ini dapat membantu identifikasi wilayah dengan curah hujan rendah,
sedang, dan tinggi di Provinsi Nusa Tenggara Barat, sehingga berguna untuk
perencanaan tata kelola air dan mitigasi bencana hidrometeorologi.
""")
