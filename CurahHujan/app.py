import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sklearn.cluster import KMeans

try:
    from groq import Groq
except:
    Groq = None

# ==================================================
# CONFIG
# ==================================================

st.set_page_config(
    page_title="Dashboard Curah Hujan NTB",
    page_icon="🌧️",
    layout="wide"
)

st.title("🌧️ Dashboard Curah Hujan NTB")
st.caption("Data Mining STT-NF 2026")

# ==================================================
# LOAD DATA
# ==================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "curah_hujan_ntb.csv")

@st.cache_data
def load_data():
    df = pd.read_csv(CSV_PATH)

    if "Latitude" in df.columns:
        swap = df["Latitude"] > 0
        df.loc[swap, ["Latitude", "Longitude"]] = \
            df.loc[swap, ["Longitude", "Latitude"]].values

    return df

df = load_data()

# ==================================================
# KMEANS
# ==================================================

X = df[["Curah Hujan (mm)"]]

kmeans = KMeans(
    n_clusters=3,
    random_state=42,
    n_init=10
)

df["Cluster"] = kmeans.fit_predict(X)

cluster_mean = (
    df.groupby("Cluster")["Curah Hujan (mm)"]
    .mean()
    .sort_values()
)

mapping = {
    cluster_mean.index[0]: "Rendah",
    cluster_mean.index[1]: "Menengah",
    cluster_mean.index[2]: "Tinggi"
}

df["Kategori Cluster"] = df["Cluster"].map(mapping)

# ==================================================
# ELBOW
# ==================================================

wcss = []

for i in range(1, 11):
    km = KMeans(
        n_clusters=i,
        random_state=42,
        n_init=10
    )
    km.fit(X)
    wcss.append(km.inertia_)

# ==================================================
# GROQ
# ==================================================

client = None

try:
    if Groq:
        client = Groq(
            api_key=st.secrets["GROQ_API_KEY"]
        )
except:
    pass

# ==================================================
# SIDEBAR
# ==================================================

df_all = df.copy()

with st.sidebar:

    st.header("🌧️ Prediksi Curah Hujan")

    kabupaten_list = sorted(
        df_all["Nama Kabupaten/Kota"].unique()
    )

    # Satu selectbox untuk prediksi sekaligus filter dashboard
    pilih_kab = st.selectbox(
        "Kabupaten / Kota",
        ["Semua"] + kabupaten_list
    )

    # Alias agar kode prediksi & filter tetap berjalan
    pilih_kab_prediksi = pilih_kab if pilih_kab != "Semua" else kabupaten_list[0]
    pilih_kab_filter   = pilih_kab

    pos_list = sorted(
        df_all[
            df_all["Nama Kabupaten/Kota"]
            == pilih_kab_prediksi
        ]["Nama Pos Hujan"].unique()
    )

    pilih_pos = st.selectbox(
        "Pos Hujan",
        pos_list
    )

    input_hujan = st.number_input(
        "Curah Hujan (mm)",
        min_value=0.0,
        value=100.0,
        step=1.0
    )

    prediksi_btn = st.button(
        "🔍 Tampilkan Hasil",
        use_container_width=True
    )

# ===========================
# HASIL PREDIKSI
# ===========================

if prediksi_btn:

    hasil_cluster = kmeans.predict(
        [[input_hujan]]
    )[0]

    hasil_label = mapping[
        hasil_cluster
    ]

    st.sidebar.success(
        f"Kategori : {hasil_label}"
    )

    st.sidebar.write(
        f"""
        Pos Hujan : {pilih_pos}

        Kabupaten : {pilih_kab_prediksi}

        Curah Hujan : {input_hujan:.1f} mm
        """
    )

    if hasil_label == "Rendah":

        st.sidebar.info(
            "Curah hujan rendah."
        )

    elif hasil_label == "Menengah":

        st.sidebar.warning(
            "Curah hujan menengah."
        )

    else:

        st.sidebar.error(
            "Curah hujan tinggi, perlu kewaspadaan banjir."
        )

# ===========================
# FILTER DASHBOARD
# ===========================

if pilih_kab_filter != "Semua":

    df = df_all[
        df_all["Nama Kabupaten/Kota"]
        == pilih_kab_filter
    ]

else:

    df = df_all.copy()

# ==================================================
# TAB DASHBOARD
# ==================================================

tab1, tab2, tab3, tab4 = st.tabs(
    ["📊 Dashboard", "📈 Analisis", "🗃️ Data", "💡 Insight"]
)

with tab1:

    st.subheader("Distribusi Curah Hujan")

    fig_bar = px.bar(
        df.sort_values(
            "Curah Hujan (mm)",
            ascending=False
        ),
        x="Nama Pos Hujan",
        y="Curah Hujan (mm)",
        color="Kategori Cluster"
    )

    st.plotly_chart(
        fig_bar,
        use_container_width=True
    )

    st.subheader("Peta Sebaran")

    fig_map = px.scatter_mapbox(
        df,
        lat="Latitude",
        lon="Longitude",
        color="Kategori Cluster",
        size="Curah Hujan (mm)",
        zoom=7,
        center={
            "lat": -8.6,
            "lon": 117.5
        },
        mapbox_style="carto-darkmatter"
    )

    st.plotly_chart(
        fig_map,
        use_container_width=True
    )

# ==================================================
# TAB ANALISIS
# ==================================================

with tab2:

    col_a, col_b = st.columns(2)

    with col_a:

        st.subheader("Elbow Method")

        fig_elbow = go.Figure()

        fig_elbow.add_trace(
            go.Scatter(
                x=list(range(1,11)),
                y=wcss,
                mode="lines+markers"
            )
        )

        st.plotly_chart(
            fig_elbow,
            use_container_width=True
        )

    with col_b:

        st.subheader("Boxplot Cluster")

        fig_box = px.box(
            df,
            x="Kategori Cluster",
            y="Curah Hujan (mm)",
            color="Kategori Cluster"
        )

        st.plotly_chart(
            fig_box,
            use_container_width=True
        )

    st.subheader("Top 10 Curah Hujan")

    top10 = df.nlargest(
        10,
        "Curah Hujan (mm)"
    )

    st.dataframe(
        top10[
            [
                "Nama Pos Hujan",
                "Nama Kabupaten/Kota",
                "Curah Hujan (mm)",
                "Kategori Cluster"
            ]
        ],
        use_container_width=True
    )

# ==================================================
# TAB DATA
# ==================================================

with tab3:

    st.subheader("Data Hasil Clustering")

    st.dataframe(
        df,
        use_container_width=True,
        height=500
    )

    st.download_button(
        "⬇️ Download CSV",
        data=df.to_csv(index=False),
        file_name="hasil_clustering.csv",
        mime="text/csv"
    )

# ==================================================
# TAB INSIGHT
# ==================================================

with tab4:

    st.subheader("Insight Otomatis")

    tertinggi = df.loc[
        df["Curah Hujan (mm)"].idxmax()
    ]

    terendah = df.loc[
        df["Curah Hujan (mm)"].idxmin()
    ]

    st.success(
        f"""
        Curah hujan tertinggi berada di
        {tertinggi['Nama Pos Hujan']}
        ({tertinggi['Nama Kabupaten/Kota']})
        sebesar
        {tertinggi['Curah Hujan (mm)']} mm
        """
    )

    st.info(
        f"""
        Curah hujan terendah berada di
        {terendah['Nama Pos Hujan']}
        ({terendah['Nama Kabupaten/Kota']})
        sebesar
        {terendah['Curah Hujan (mm)']} mm
        """
    )

    st.write("### Ringkasan Cluster")

    st.write(
        f"""
        - Rendah : {len(df[df['Kategori Cluster']=='Rendah'])}
        - Menengah : {len(df[df['Kategori Cluster']=='Menengah'])}
        - Tinggi : {len(df[df['Kategori Cluster']=='Tinggi'])}
        """
    )

    st.divider()

    st.subheader("🤖 Analisis AI Groq")

    if client is None:

        st.warning(
            "Tambahkan GROQ_API_KEY pada Secrets Streamlit."
        )

    else:

        if st.button("Generate Analisis AI"):

            with st.spinner("AI sedang menganalisis..."):

                prompt = f"""
                Analisis data curah hujan NTB.

                Jumlah cluster rendah:
                {len(df[df['Kategori Cluster']=='Rendah'])}

                Jumlah cluster menengah:
                {len(df[df['Kategori Cluster']=='Menengah'])}

                Jumlah cluster tinggi:
                {len(df[df['Kategori Cluster']=='Tinggi'])}

                Rata-rata curah hujan:
                {df['Curah Hujan (mm)'].mean():.2f}

                Berikan insight singkat,
                risiko banjir,
                dan rekomendasi.
                """

                response = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[
                        {
                            "role":"user",
                            "content":prompt
                        }
                    ]
                )

                st.markdown(
                    response.choices[0].message.content
                )

# ==================================================
# FOOTER
# ==================================================

st.divider()

st.caption(
    "Data Mining STT-NF 2026 | K-Means Clustering | Streamlit Cloud"
)