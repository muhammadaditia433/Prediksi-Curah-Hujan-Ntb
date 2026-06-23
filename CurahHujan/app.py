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
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================================================
# CUSTOM CSS - Modern Dark Theme
# ==================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');

/* Root & Base */
:root {
    --bg-primary: #0a0e1a;
    --bg-card: #111827;
    --bg-card-hover: #1a2235;
    --accent-blue: #3b82f6;
    --accent-cyan: #06b6d4;
    --accent-green: #10b981;
    --accent-orange: #f59e0b;
    --accent-red: #ef4444;
    --text-primary: #f1f5f9;
    --text-secondary: #94a3b8;
    --border: #1e2d45;
}

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: var(--bg-primary);
    color: var(--text-primary);
}

/* Hide default streamlit elements */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Main container */
.main .block-container {
    padding: 1.5rem 2rem;
    max-width: 1400px;
}

/* Header */
.dashboard-header {
    background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 50%, #0f172a 100%);
    border: 1px solid #1e3a5f;
    border-radius: 16px;
    padding: 2rem 2.5rem;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
}
.dashboard-header::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -10%;
    width: 300px;
    height: 300px;
    background: radial-gradient(circle, rgba(59,130,246,0.15) 0%, transparent 70%);
    border-radius: 50%;
}
.dashboard-header h1 {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 2rem;
    font-weight: 700;
    color: #f1f5f9;
    margin: 0;
    letter-spacing: -0.5px;
}
.dashboard-header p {
    color: #64748b;
    margin: 0.25rem 0 0 0;
    font-size: 0.875rem;
}
.header-badge {
    display: inline-block;
    background: rgba(59,130,246,0.15);
    border: 1px solid rgba(59,130,246,0.3);
    color: #3b82f6;
    padding: 0.25rem 0.75rem;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 500;
    margin-bottom: 0.75rem;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}

/* Metric cards */
.metric-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    transition: all 0.2s ease;
}
.metric-card:hover {
    border-color: #3b82f6;
    transform: translateY(-2px);
}
.metric-label {
    font-size: 0.75rem;
    font-weight: 500;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 0.5rem;
}
.metric-value {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.75rem;
    font-weight: 700;
    color: var(--text-primary);
    line-height: 1;
}
.metric-sub {
    font-size: 0.75rem;
    color: var(--text-secondary);
    margin-top: 0.35rem;
}
.metric-dot {
    display: inline-block;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    margin-right: 6px;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #080d18 !important;
    border-right: 1px solid #1e2d45;
}
section[data-testid="stSidebar"] .block-container {
    padding: 1.5rem 1rem;
}

/* Sidebar header */
.sidebar-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1rem;
    font-weight: 600;
    color: #f1f5f9;
    margin-bottom: 1rem;
    padding-bottom: 0.75rem;
    border-bottom: 1px solid #1e2d45;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: transparent;
    border-bottom: 1px solid #1e2d45;
    gap: 0;
}
.stTabs [data-baseweb="tab"] {
    background: transparent;
    color: #64748b;
    font-weight: 500;
    font-size: 0.875rem;
    padding: 0.75rem 1.25rem;
    border-bottom: 2px solid transparent;
}
.stTabs [aria-selected="true"] {
    background: transparent !important;
    color: #3b82f6 !important;
    border-bottom: 2px solid #3b82f6 !important;
}

/* Charts */
.chart-container {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.25rem;
    margin-bottom: 1rem;
}
.chart-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.9rem;
    font-weight: 600;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 1rem;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #2563eb, #1d4ed8) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
    font-size: 0.875rem !important;
    padding: 0.6rem 1.25rem !important;
    transition: all 0.2s !important;
    width: 100% !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #3b82f6, #2563eb) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 12px rgba(59,130,246,0.3) !important;
}

/* Selectbox & inputs */
.stSelectbox > div > div,
.stNumberInput > div > div {
    background: #111827 !important;
    border: 1px solid #1e2d45 !important;
    border-radius: 8px !important;
    color: #f1f5f9 !important;
}

/* Divider */
hr {
    border-color: #1e2d45 !important;
}

/* Dataframe */
.stDataFrame {
    border-radius: 10px;
    overflow: hidden;
    border: 1px solid #1e2d45;
}

/* Alert boxes */
.stSuccess, .stInfo, .stWarning, .stError {
    border-radius: 10px !important;
}

/* Insight cards */
.insight-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 0.75rem;
}
.insight-card.success { border-left: 3px solid #10b981; }
.insight-card.info { border-left: 3px solid #3b82f6; }
.insight-card.warning { border-left: 3px solid #f59e0b; }
.insight-card.danger { border-left: 3px solid #ef4444; }

.cluster-pill {
    display: inline-flex;
    align-items: center;
    padding: 0.2rem 0.75rem;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 600;
    margin: 0.2rem;
}
.pill-rendah { background: rgba(16,185,129,0.15); color: #10b981; border: 1px solid rgba(16,185,129,0.3); }
.pill-menengah { background: rgba(245,158,11,0.15); color: #f59e0b; border: 1px solid rgba(245,158,11,0.3); }
.pill-tinggi { background: rgba(239,68,68,0.15); color: #ef4444; border: 1px solid rgba(239,68,68,0.3); }
</style>
""", unsafe_allow_html=True)

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
kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
df["Cluster"] = kmeans.fit_predict(X)

cluster_mean = df.groupby("Cluster")["Curah Hujan (mm)"].mean().sort_values()
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
    km = KMeans(n_clusters=i, random_state=42, n_init=10)
    km.fit(X)
    wcss.append(km.inertia_)

# ==================================================
# GROQ
# ==================================================

client = None
groq_api_key = None

try:
    groq_api_key = st.secrets["GROQ_API_KEY"]
except Exception:
    pass

if not groq_api_key:
    groq_api_key = os.environ.get("GROQ_API_KEY", "")

if Groq and groq_api_key:
    try:
        client = Groq(api_key=groq_api_key)
    except Exception:
        pass

# ==================================================
# SIDEBAR
# ==================================================

df_all = df.copy()

with st.sidebar:
    st.markdown('<div class="sidebar-title">🌧️ Prediksi Curah Hujan</div>', unsafe_allow_html=True)

    kabupaten_list = sorted(df_all["Nama Kabupaten/Kota"].unique())

    pilih_kab = st.selectbox("Kabupaten / Kota", ["Semua"] + kabupaten_list)
    pilih_kab_prediksi = pilih_kab if pilih_kab != "Semua" else kabupaten_list[0]
    pilih_kab_filter = pilih_kab

    pos_list = sorted(
        df_all[df_all["Nama Kabupaten/Kota"] == pilih_kab_prediksi]["Nama Pos Hujan"].unique()
    )
    pilih_pos = st.selectbox("Pos Hujan", pos_list)

    input_hujan = st.number_input("Curah Hujan (mm)", min_value=0.0, value=100.0, step=1.0)

    prediksi_btn = st.button("🔍 Tampilkan Hasil", use_container_width=True)

# ==================================================
# HASIL PREDIKSI
# ==================================================

if prediksi_btn:
    hasil_cluster = kmeans.predict([[input_hujan]])[0]
    hasil_label = mapping[hasil_cluster]

    color_map = {"Rendah": "success", "Menengah": "warning", "Tinggi": "error"}
    getattr(st.sidebar, color_map[hasil_label])(f"Kategori : **{hasil_label}**")

    st.sidebar.markdown(f"""
    <div style="background:#111827;border:1px solid #1e2d45;border-radius:10px;padding:1rem;margin-top:0.5rem;font-size:0.85rem;color:#94a3b8;">
    <b style="color:#f1f5f9">📍 {pilih_pos}</b><br>
    🏙️ {pilih_kab_prediksi}<br>
    💧 {input_hujan:.1f} mm
    </div>
    """, unsafe_allow_html=True)

    if hasil_label == "Rendah":
        st.sidebar.info("☀️ Curah hujan rendah, kondisi normal.")
    elif hasil_label == "Menengah":
        st.sidebar.warning("🌦️ Curah hujan menengah, waspadai genangan.")
    else:
        st.sidebar.error("⛈️ Curah hujan tinggi, risiko banjir!")

# ==================================================
# FILTER
# ==================================================

if pilih_kab_filter != "Semua":
    df = df_all[df_all["Nama Kabupaten/Kota"] == pilih_kab_filter]
else:
    df = df_all.copy()

# ==================================================
# HEADER
# ==================================================

st.markdown("""
<div class="dashboard-header">
    <div class="header-badge">Data Mining · STT-NF 2026</div>
    <h1>🌧️ Dashboard Curah Hujan NTB</h1>
    <p>K-Means Clustering · Analisis Distribusi Curah Hujan Nusa Tenggara Barat</p>
</div>
""", unsafe_allow_html=True)

# ==================================================
# METRIC CARDS
# ==================================================

n_rendah  = len(df[df["Kategori Cluster"] == "Rendah"])
n_menengah = len(df[df["Kategori Cluster"] == "Menengah"])
n_tinggi  = len(df[df["Kategori Cluster"] == "Tinggi"])
rata_rata = df["Curah Hujan (mm)"].mean()
maks      = df["Curah Hujan (mm)"].max()
total     = len(df)

c1, c2, c3, c4, c5 = st.columns(5)

with c1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Total Pos Hujan</div>
        <div class="metric-value">{total}</div>
        <div class="metric-sub">📍 stasiun aktif</div>
    </div>""", unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Rata-rata</div>
        <div class="metric-value">{rata_rata:.0f}</div>
        <div class="metric-sub">💧 mm curah hujan</div>
    </div>""", unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label"><span class="metric-dot" style="background:#10b981"></span>Cluster Rendah</div>
        <div class="metric-value" style="color:#10b981">{n_rendah}</div>
        <div class="metric-sub">pos hujan</div>
    </div>""", unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label"><span class="metric-dot" style="background:#f59e0b"></span>Cluster Menengah</div>
        <div class="metric-value" style="color:#f59e0b">{n_menengah}</div>
        <div class="metric-sub">pos hujan</div>
    </div>""", unsafe_allow_html=True)

with c5:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label"><span class="metric-dot" style="background:#ef4444"></span>Cluster Tinggi</div>
        <div class="metric-value" style="color:#ef4444">{n_tinggi}</div>
        <div class="metric-sub">pos hujan</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ==================================================
# COLOR MAP
# ==================================================

COLOR_MAP = {
    "Rendah": "#10b981",
    "Menengah": "#f59e0b",
    "Tinggi": "#ef4444"
}

PLOTLY_TEMPLATE = dict(
    layout=dict(
        paper_bgcolor="#111827",
        plot_bgcolor="#111827",
        font=dict(color="#94a3b8", family="Inter"),
        xaxis=dict(gridcolor="#1e2d45", linecolor="#1e2d45"),
        yaxis=dict(gridcolor="#1e2d45", linecolor="#1e2d45"),
        legend=dict(bgcolor="#111827", bordercolor="#1e2d45"),
        margin=dict(t=30, b=40, l=40, r=20),
    )
)

# ==================================================
# TABS
# ==================================================

tab1, tab2, tab3, tab4 = st.tabs(
    ["📊 Dashboard", "📈 Analisis", "🗃️ Data", "💡 Insight"]
)

# ── TAB 1 ──────────────────────────────────────────
with tab1:

    col_l, col_r = st.columns([3, 2])

    with col_l:
        st.markdown('<div class="chart-title">Distribusi Curah Hujan per Pos</div>', unsafe_allow_html=True)
        fig_bar = px.bar(
            df.sort_values("Curah Hujan (mm)", ascending=False),
            x="Nama Pos Hujan",
            y="Curah Hujan (mm)",
            color="Kategori Cluster",
            color_discrete_map=COLOR_MAP,
            template="plotly_dark",
        )
        fig_bar.update_layout(**PLOTLY_TEMPLATE["layout"])
        fig_bar.update_traces(marker_line_width=0)
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_r:
        st.markdown('<div class="chart-title">Proporsi Cluster</div>', unsafe_allow_html=True)
        cluster_count = df["Kategori Cluster"].value_counts().reset_index()
        cluster_count.columns = ["Kategori", "Jumlah"]
        fig_pie = px.pie(
            cluster_count,
            names="Kategori",
            values="Jumlah",
            color="Kategori",
            color_discrete_map=COLOR_MAP,
            hole=0.6,
        )
        fig_pie.update_layout(**PLOTLY_TEMPLATE["layout"])
        fig_pie.update_traces(textfont_color="white")
        st.plotly_chart(fig_pie, use_container_width=True)

    st.markdown('<div class="chart-title">Peta Sebaran Curah Hujan NTB</div>', unsafe_allow_html=True)
    fig_map = px.scatter_mapbox(
        df,
        lat="Latitude",
        lon="Longitude",
        color="Kategori Cluster",
        size="Curah Hujan (mm)",
        color_discrete_map=COLOR_MAP,
        zoom=7,
        center={"lat": -8.6, "lon": 117.5},
        mapbox_style="carto-darkmatter",
        hover_name="Nama Pos Hujan",
        hover_data={"Nama Kabupaten/Kota": True, "Curah Hujan (mm)": True},
        size_max=20,
    )
    fig_map.update_layout(paper_bgcolor="#111827", margin=dict(t=0, b=0, l=0, r=0), height=420)
    st.plotly_chart(fig_map, use_container_width=True)

# ── TAB 2 ──────────────────────────────────────────
with tab2:

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown('<div class="chart-title">Elbow Method — Optimal K</div>', unsafe_allow_html=True)
        fig_elbow = go.Figure()
        fig_elbow.add_trace(go.Scatter(
            x=list(range(1, 11)), y=wcss,
            mode="lines+markers",
            line=dict(color="#3b82f6", width=2),
            marker=dict(color="#3b82f6", size=8, line=dict(color="#93c5fd", width=1)),
        ))
        fig_elbow.add_vline(x=3, line_dash="dash", line_color="#f59e0b", opacity=0.6,
                            annotation_text="K=3", annotation_font_color="#f59e0b")
        fig_elbow.update_layout(**PLOTLY_TEMPLATE["layout"],
                                 xaxis_title="Jumlah Cluster (K)",
                                 yaxis_title="WCSS")
        st.plotly_chart(fig_elbow, use_container_width=True)

    with col_b:
        st.markdown('<div class="chart-title">Distribusi per Cluster</div>', unsafe_allow_html=True)
        fig_box = px.box(
            df,
            x="Kategori Cluster",
            y="Curah Hujan (mm)",
            color="Kategori Cluster",
            color_discrete_map=COLOR_MAP,
            category_orders={"Kategori Cluster": ["Rendah", "Menengah", "Tinggi"]},
        )
        fig_box.update_layout(**PLOTLY_TEMPLATE["layout"])
        st.plotly_chart(fig_box, use_container_width=True)

    st.markdown('<div class="chart-title">Top 10 Curah Hujan Tertinggi</div>', unsafe_allow_html=True)
    top10 = df.nlargest(10, "Curah Hujan (mm)")
    fig_top = px.bar(
        top10,
        x="Curah Hujan (mm)",
        y="Nama Pos Hujan",
        color="Kategori Cluster",
        color_discrete_map=COLOR_MAP,
        orientation="h",
        text="Curah Hujan (mm)",
    )
    fig_top.update_layout(**PLOTLY_TEMPLATE["layout"])
    fig_top.update_traces(texttemplate="%{text:.0f} mm", textposition="outside")
    st.plotly_chart(fig_top, use_container_width=True)

# ── TAB 3 ──────────────────────────────────────────
with tab3:
    st.markdown('<div class="chart-title">Data Hasil Clustering</div>', unsafe_allow_html=True)

    search = st.text_input("🔍 Cari pos hujan atau kabupaten...", placeholder="Ketik nama...")
    df_show = df.copy()
    if search:
        mask = df_show.apply(lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1)
        df_show = df_show[mask]

    st.dataframe(df_show, use_container_width=True, height=450)

    col_dl1, col_dl2 = st.columns([1, 3])
    with col_dl1:
        st.download_button(
            "⬇️ Download CSV",
            data=df.to_csv(index=False),
            file_name="hasil_clustering.csv",
            mime="text/csv",
        )

# ── TAB 4 ──────────────────────────────────────────
with tab4:

    tertinggi = df.loc[df["Curah Hujan (mm)"].idxmax()]
    terendah  = df.loc[df["Curah Hujan (mm)"].idxmin()]

    col_i1, col_i2 = st.columns(2)

    with col_i1:
        st.markdown(f"""
        <div class="insight-card success">
            <div style="font-size:0.75rem;color:#10b981;font-weight:600;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:0.5rem">⬆ Tertinggi</div>
            <div style="font-size:1.1rem;font-weight:700;color:#f1f5f9">{tertinggi['Nama Pos Hujan']}</div>
            <div style="color:#64748b;font-size:0.85rem">{tertinggi['Nama Kabupaten/Kota']}</div>
            <div style="font-size:1.5rem;font-weight:700;color:#10b981;margin-top:0.5rem">{tertinggi['Curah Hujan (mm)']} mm</div>
        </div>
        """, unsafe_allow_html=True)

    with col_i2:
        st.markdown(f"""
        <div class="insight-card info">
            <div style="font-size:0.75rem;color:#3b82f6;font-weight:600;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:0.5rem">⬇ Terendah</div>
            <div style="font-size:1.1rem;font-weight:700;color:#f1f5f9">{terendah['Nama Pos Hujan']}</div>
            <div style="color:#64748b;font-size:0.85rem">{terendah['Nama Kabupaten/Kota']}</div>
            <div style="font-size:1.5rem;font-weight:700;color:#3b82f6;margin-top:0.5rem">{terendah['Curah Hujan (mm)']} mm</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="chart-title">Ringkasan Cluster</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div style="display:flex;gap:0.75rem;flex-wrap:wrap;margin-bottom:1.5rem;">
        <span class="cluster-pill pill-rendah">🟢 Rendah &nbsp; {n_rendah} pos</span>
        <span class="cluster-pill pill-menengah">🟡 Menengah &nbsp; {n_menengah} pos</span>
        <span class="cluster-pill pill-tinggi">🔴 Tinggi &nbsp; {n_tinggi} pos</span>
    </div>
    """, unsafe_allow_html=True)

    st.divider()
    st.markdown('<div class="chart-title">🤖 Analisis AI Groq</div>', unsafe_allow_html=True)

    if client is None:
        st.markdown("""
        <div style="background:rgba(245,158,11,0.1);border:1px solid rgba(245,158,11,0.3);border-radius:10px;padding:1rem 1.25rem;color:#f59e0b;font-size:0.875rem;">
        ⚠️ Tambahkan <code>GROQ_API_KEY</code> pada Secrets Streamlit untuk mengaktifkan fitur ini.
        </div>
        """, unsafe_allow_html=True)
    else:
        if st.button("✨ Generate Analisis AI"):
            with st.spinner("AI sedang menganalisis data..."):
                prompt = f"""
                Analisis data curah hujan NTB berikut dan berikan insight dalam Bahasa Indonesia.

                Jumlah cluster rendah: {n_rendah}
                Jumlah cluster menengah: {n_menengah}
                Jumlah cluster tinggi: {n_tinggi}
                Rata-rata curah hujan: {rata_rata:.2f} mm
                Curah hujan tertinggi: {maks} mm di {tertinggi['Nama Pos Hujan']}

                Berikan:
                1. Insight singkat kondisi curah hujan NTB
                2. Risiko banjir dan daerah yang perlu diwaspadai
                3. Rekomendasi tindakan mitigasi
                Format ringkas dan informatif.
                """
                response = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[{"role": "user", "content": prompt}]
                )
                st.markdown(f"""
                <div style="background:#111827;border:1px solid #1e2d45;border-radius:12px;padding:1.5rem;margin-top:1rem;">
                {response.choices[0].message.content}
                </div>
                """, unsafe_allow_html=True)

# ==================================================
# FOOTER
# ==================================================

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align:center;color:#334155;font-size:0.75rem;padding:1rem;border-top:1px solid #1e2d45;">
    Data Mining STT-NF 2026 &nbsp;·&nbsp; K-Means Clustering &nbsp;·&nbsp; Streamlit Cloud
</div>
""", unsafe_allow_html=True)