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

.main {
    padding-top: 1rem;
}

.metric-container{
    background-color:#f8f9fa;
    padding:10px;
    border-radius:10px;
}

</style>
""", unsafe_allow_html=True)

# =====================================
# LOAD DATA
# =====================================

df = pd.read_csv("curah_hujan_ntb.csv")

# =====================================
# K-MEANS
# =====================================

X = df[['Curah Hujan (mm)']]

kmeans = KMeans(
    n_clusters=3,
    random_state=42,
    n_init=10
)

df['Cluster'] = kmeans.fit_predict(X)

# Label Cluster

cluster_mean = (
    df.groupby('Cluster')['Curah Hujan (mm)']
    .mean()
    .sort_values()
)

mapping = {
    cluster_mean.index[0]: "Rendah",
    cluster_mean.index[1]: "Menengah",
    cluster_mean.index[2]: "Tinggi"
}

df['Kategori Cluster'] = df['Cluster'].map(mapping)

# =====================================
# ELBOW METHOD
# =====================================

wcss = []

for i in range(1, 11):

    km = KMeans(
        n_clusters=i,
        random_state=42,
        n_init=10
    )

    km.fit(X)

    wcss.append(km.inertia_)

# =====================================
# HEADER
# =====================================

st.title("🌧️ Dashboard Curah Hujan NTB")

st.markdown("""
### Penerapan Metode Clustering untuk Pengelompokan Intensitas Curah Hujan di Nusa Tenggara Barat
""")

# =====================================
# SIDEBAR
# =====================================

st.sidebar.header("⚙️ Filter Data")

search = st.sidebar.text_input(
    "🔍 Cari Kabupaten"
)

cluster_filter = st.sidebar.selectbox(
    "Kategori Cluster",
    ["Semua", "Rendah", "Menengah", "Tinggi"]
)

df_tampil = df.copy()

if search:

    df_tampil = df_tampil[
        df_tampil['Nama Kabupaten/Kota']
        .str.contains(search, case=False, na=False)
    ]

if cluster_filter != "Semua":

    df_tampil = df_tampil[
        df_tampil['Kategori Cluster']
        == cluster_filter
    ]

# =====================================
# KPI
# =====================================

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Jumlah Data",
        len(df_tampil)
    )

with col2:
    st.metric(
        "Jumlah Cluster",
        3
    )

with col3:
    st.metric(
        "Rata-rata Curah Hujan",
        round(
            df_tampil['Curah Hujan (mm)'].mean(),
            2
        )
    )

with col4:
    st.metric(
        "Curah Hujan Maks",
        round(
            df_tampil['Curah Hujan (mm)'].max(),
            2
        )
    )

st.divider()

# =====================================
# TABS
# =====================================

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Dashboard",
    "📈 Analisis",
    "🗺️ Peta",
    "📋 Data",
    "💡 Insight"
])

# =====================================
# DASHBOARD
# =====================================

with tab1:

    st.subheader("Distribusi Curah Hujan")

    fig_bar = px.bar(
        df_tampil,
        x='Nama Kabupaten/Kota',
        y='Curah Hujan (mm)',
        color='Kategori Cluster',
        title='Distribusi Curah Hujan NTB'
    )

    st.plotly_chart(
        fig_bar,
        use_container_width=True
    )

    st.subheader("Persentase Cluster")

    fig_pie = px.pie(
        df_tampil,
        names='Kategori Cluster',
        title='Persentase Cluster'
    )

    st.plotly_chart(
        fig_pie,
        use_container_width=True
    )

# =====================================
# ANALISIS
# =====================================

with tab2:

    st.subheader("📉 Elbow Method")

    fig_elbow = go.Figure()

    fig_elbow.add_trace(
        go.Scatter(
            x=list(range(1,11)),
            y=wcss,
            mode='lines+markers'
        )
    )

    fig_elbow.update_layout(
        title='Elbow Method',
        xaxis_title='Jumlah Cluster',
        yaxis_title='WCSS'
    )

    st.plotly_chart(
        fig_elbow,
        use_container_width=True
    )

    st.subheader("🏆 Top 10 Curah Hujan Tertinggi")

    top10 = df_tampil.nlargest(
        10,
        'Curah Hujan (mm)'
    )

    st.dataframe(
        top10[
            [
                'Nama Kabupaten/Kota',
                'Curah Hujan (mm)',
                'Kategori Cluster'
            ]
        ],
        use_container_width=True
    )

    st.subheader("📊 Statistik Deskriptif")

    st.dataframe(
        df_tampil[
            ['Curah Hujan (mm)']
        ].describe(),
        use_container_width=True
    )

# =====================================
# PETA
# =====================================

with tab3:

    if 'Latitude' in df.columns and 'Longitude' in df.columns:

        fig_map = px.scatter_map(
            df_tampil,
            lat="Latitude",
            lon="Longitude",
            color="Kategori Cluster",
            size="Curah Hujan (mm)",
            hover_name="Nama Kabupaten/Kota",
            zoom=7
        )

        st.plotly_chart(
            fig_map,
            use_container_width=True
        )

    else:

        st.warning(
            "Kolom Latitude dan Longitude tidak ditemukan."
        )

# =====================================
# DATA
# =====================================

with tab4:

    st.dataframe(
        df_tampil[
            [
                'Nama Kabupaten/Kota',
                'Curah Hujan (mm)',
                'Kategori Cluster'
            ]
        ],
        use_container_width=True
    )

    csv = df_tampil.to_csv(
        index=False
    )

    st.download_button(
        "⬇ Download Hasil Clustering",
        csv,
        "hasil_clustering.csv",
        "text/csv"
    )

# =====================================
# INSIGHT
# =====================================

with tab5:

    tertinggi = df_tampil.loc[
        df_tampil['Curah Hujan (mm)'].idxmax()
    ]

    terendah = df_tampil.loc[
        df_tampil['Curah Hujan (mm)'].idxmin()
    ]

    st.success(
        f"Curah hujan tertinggi berada di "
        f"{tertinggi['Nama Kabupaten/Kota']} "
        f"({tertinggi['Curah Hujan (mm)']} mm)"
    )

    st.info(
        f"Curah hujan terendah berada di "
        f"{terendah['Nama Kabupaten/Kota']} "
        f"({terendah['Curah Hujan (mm)']} mm)"
    )

    st.markdown(f"""
## Kesimpulan

- Jumlah Data : **{len(df_tampil)}**
- Jumlah Cluster : **3**
- Curah Hujan Rata-rata : **{round(df_tampil['Curah Hujan (mm)'].mean(),2)} mm**
- Curah Hujan Maksimum : **{round(df_tampil['Curah Hujan (mm)'].max(),2)} mm**
- Curah Hujan Minimum : **{round(df_tampil['Curah Hujan (mm)'].min(),2)} mm**

### Hasil Clustering

- Cluster Rendah
- Cluster Menengah
- Cluster Tinggi

Metode K-Means berhasil mengelompokkan data curah hujan berdasarkan tingkat intensitas sehingga dapat membantu identifikasi wilayah dengan curah hujan rendah, sedang, dan tinggi di Provinsi Nusa Tenggara Barat.
""")