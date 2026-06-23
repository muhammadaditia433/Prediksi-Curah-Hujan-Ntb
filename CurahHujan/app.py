import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sklearn.cluster import KMeans

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────

st.set_page_config(
    page_title="Curah Hujan NTB · Dashboard",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# GLOBAL CSS — Dark Meteorologi Theme
# ─────────────────────────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

/* ── Root & Background ── */
html, body, [data-testid="stAppViewContainer"],
[data-testid="stMain"], .main {
    background: #07111f !important;
    color: #e8f0fe !important;
    font-family: 'Inter', sans-serif !important;
}

[data-testid="stSidebar"] {
    background: #0d1e33 !important;
    border-right: 1px solid #1e3a5f !important;
}

[data-testid="stSidebar"] * { color: #c8d8f0 !important; }

/* ── Hide default header ── */
[data-testid="stHeader"] { background: transparent !important; }
header { visibility: hidden; }

/* ── Hero banner ── */
.hero-banner {
    background: linear-gradient(135deg, #0d2444 0%, #0a3d62 50%, #0d2444 100%);
    border: 1px solid #1e4976;
    border-radius: 16px;
    padding: 2.5rem 2rem 2rem 2rem;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
}
.hero-banner::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, #00d4ff, #00e676, #ffd700, #ff5252);
    border-radius: 16px 16px 0 0;
}
.hero-title {
    font-size: 2rem;
    font-weight: 800;
    color: #ffffff;
    letter-spacing: -0.03em;
    margin: 0 0 0.3rem 0;
}
.hero-title span { color: #00d4ff; }
.hero-sub {
    font-size: 0.9rem;
    color: #7fa8d0;
    font-weight: 400;
    margin: 0;
}
.rain-icon {
    position: absolute;
    right: 2rem;
    top: 50%;
    transform: translateY(-50%);
    font-size: 4rem;
    opacity: 0.15;
}

/* ── Metric cards ── */
.metric-card {
    background: #0d1e33;
    border: 1px solid #1e3a5f;
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
    position: relative;
    overflow: hidden;
    transition: border-color .2s;
}
.metric-card:hover { border-color: #00d4ff44; }
.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
}
.metric-card.blue::before  { background: #00d4ff; }
.metric-card.green::before { background: #00e676; }
.metric-card.amber::before { background: #ffb300; }
.metric-card.red::before   { background: #ff5252; }
.metric-card.purple::before{ background: #b388ff; }
.metric-label {
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: .08em;
    text-transform: uppercase;
    color: #5a8ab0;
    margin-bottom: .4rem;
}
.metric-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.9rem;
    font-weight: 600;
    color: #ffffff;
    line-height: 1;
}
.metric-unit {
    font-size: 0.75rem;
    color: #5a8ab0;
    margin-top: .3rem;
    font-family: 'Inter', sans-serif;
}

/* ── Section header ── */
.section-header {
    display: flex;
    align-items: center;
    gap: .6rem;
    margin: 1.5rem 0 .8rem 0;
}
.section-header .icon { font-size: 1.1rem; }
.section-header h3 {
    font-size: 1rem;
    font-weight: 700;
    color: #c8d8f0;
    margin: 0;
    letter-spacing: -.01em;
}
.section-divider {
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, #1e3a5f, transparent);
    margin-left: .6rem;
}

/* ── Submit / CTA button ── */
div[data-testid="stButton"] > button {
    background: linear-gradient(135deg, #0057b8, #00a8e8) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.9rem !important;
    font-weight: 700 !important;
    letter-spacing: .04em !important;
    padding: .7rem 2rem !important;
    width: 100% !important;
    cursor: pointer !important;
    transition: opacity .2s !important;
    box-shadow: 0 4px 16px #00a8e840 !important;
}
div[data-testid="stButton"] > button:hover {
    opacity: .88 !important;
}

/* ── Sidebar select / input ── */
[data-testid="stSidebar"] .stSelectbox > div,
[data-testid="stSidebar"] .stTextInput > div > div {
    background: #0a1628 !important;
    border: 1px solid #1e3a5f !important;
    border-radius: 8px !important;
    color: #e8f0fe !important;
}

/* ── Tab styling ── */
[data-testid="stTabs"] [role="tablist"] {
    background: #0d1e33;
    border-radius: 10px;
    padding: 4px;
    gap: 2px;
    border: 1px solid #1e3a5f;
}
[data-testid="stTabs"] button[role="tab"] {
    background: transparent !important;
    color: #5a8ab0 !important;
    border-radius: 7px !important;
    font-size: 0.82rem !important;
    font-weight: 600 !important;
    padding: .4rem .9rem !important;
    border: none !important;
    transition: all .15s !important;
}
[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
    background: #00d4ff22 !important;
    color: #00d4ff !important;
    box-shadow: none !important;
}

/* ── Dataframe ── */
[data-testid="stDataFrame"] {
    border: 1px solid #1e3a5f !important;
    border-radius: 10px !important;
    overflow: hidden;
}

/* ── Alert / success / info ── */
[data-testid="stAlert"] {
    background: #0d1e33 !important;
    border-radius: 10px !important;
    border-left-width: 3px !important;
}

/* ── Divider ── */
hr { border-color: #1e3a5f !important; }

/* ── Sidebar label ── */
[data-testid="stSidebar"] label {
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    letter-spacing: .06em !important;
    text-transform: uppercase !important;
    color: #4a7a9b !important;
}

/* ── Cluster badge ── */
.badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: .72rem;
    font-weight: 700;
    letter-spacing: .06em;
    text-transform: uppercase;
}
.badge-rendah   { background: #00d4ff22; color: #00d4ff; border: 1px solid #00d4ff55; }
.badge-menengah { background: #ffb30022; color: #ffb300; border: 1px solid #ffb30055; }
.badge-tinggi   { background: #ff525222; color: #ff5252; border: 1px solid #ff525255; }

/* ── Result fade-in ── */
@keyframes fadeSlideIn {
    from { opacity: 0; transform: translateY(16px); }
    to   { opacity: 1; transform: translateY(0); }
}
.result-container {
    animation: fadeSlideIn .4s ease;
}

/* ── Sidebar logo/brand ── */
.sidebar-brand {
    background: linear-gradient(135deg, #0a3d62, #0d2444);
    border-radius: 10px;
    padding: 1rem;
    margin-bottom: 1.2rem;
    border: 1px solid #1e4976;
    text-align: center;
}
.sidebar-brand h2 {
    font-size: 1.1rem;
    font-weight: 800;
    color: #00d4ff;
    margin: 0;
    letter-spacing: -.01em;
}
.sidebar-brand p {
    font-size: .72rem;
    color: #5a8ab0;
    margin: .3rem 0 0 0;
}

</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# LOAD & PROCESS DATA
# ─────────────────────────────────────────────

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "curah_hujan_ntb.csv")

BULAN_MAP = {6: "Juni", 7: "Juli", 8: "Agustus", 9: "September",
             10: "Oktober", 11: "November", 12: "Desember",
             1: "Januari", 2: "Februari", 3: "Maret", 4: "April", 5: "Mei"}

COLOR_MAP = {"Rendah": "#00d4ff", "Menengah": "#ffb300", "Tinggi": "#ff5252"}

@st.cache_data
def load_data():
    df = pd.read_csv(CSV_PATH)
    # Fix swapped lat/lon (NTB lat harusnya negatif)
    swap = df['Latitude'] > 0
    df.loc[swap, ['Latitude', 'Longitude']] = df.loc[swap, ['Longitude', 'Latitude']].values
    df['Nama Bulan'] = df['Bulan'].map(BULAN_MAP)
    df['Periode'] = df['Dasarian'] + " · " + df['Nama Bulan'] + " " + df['Tahun'].astype(str)
    return df

@st.cache_data
def run_kmeans(data_hash):
    df = load_data()
    X = df[['Curah Hujan (mm)']]
    km = KMeans(n_clusters=3, random_state=42, n_init=10)
    df['Cluster'] = km.fit_predict(X)
    cm = df.groupby('Cluster')['Curah Hujan (mm)'].mean().sort_values()
    mapping = {cm.index[0]: "Rendah", cm.index[1]: "Menengah", cm.index[2]: "Tinggi"}
    df['Kategori Cluster'] = df['Cluster'].map(mapping)
    # Elbow
    wcss = []
    for i in range(1, 11):
        k = KMeans(n_clusters=i, random_state=42, n_init=10)
        k.fit(X)
        wcss.append(k.inertia_)
    return df, wcss, mapping, km.cluster_centers_

df_all, wcss, cluster_mapping, centroids = run_kmeans(0)

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────

with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
        <h2> BMKG · NTB</h2>
        <p>Dashboard Curah Hujan</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("**FILTER DATA**")

    periode_opts = ["Semua Periode"] + sorted(df_all['Periode'].unique().tolist())
    sel_periode = st.selectbox("Periode", periode_opts)

    kab_opts = ["Semua Wilayah"] + sorted(df_all['Nama Kabupaten/Kota'].unique().tolist())
    sel_kab = st.selectbox("Kabupaten / Kota", kab_opts)

    cluster_opts = ["Semua Cluster", "Rendah", "Menengah", "Tinggi"]
    sel_cluster = st.selectbox("Kategori Cluster", cluster_opts)

    sel_search = st.text_input("Cari Pos Hujan", placeholder="Ketik nama pos…")

    st.markdown("<br>", unsafe_allow_html=True)
    submitted = st.button("🔍  Tampilkan Hasil", use_container_width=True)

    st.markdown("---")
    st.markdown("""
    <div style="font-size:.72rem;color:#4a7a9b;line-height:1.8;">
        <b style="color:#5a8ab0;">Metode:</b> K-Means Clustering (K=3)<br>
        <b style="color:#5a8ab0;">Sumber:</b> Data Pos Hujan NTB<br>
        <b style="color:#5a8ab0;">Tahun:</b> 2025
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# HERO
# ─────────────────────────────────────────────

st.markdown("""
<div class="hero-banner">
    <div class="rain-icon">🌧️</div>
    <p class="hero-title">Dashboard <span>Curah Hujan</span> NTB</p>
    <p class="hero-sub">
        Penerapan K-Means Clustering · Intensitas Curah Hujan Nusa Tenggara Barat · 2025
    </p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# FILTER DATA
# ─────────────────────────────────────────────

def apply_filter(df):
    d = df.copy()
    if sel_periode != "Semua Periode":
        d = d[d['Periode'] == sel_periode]
    if sel_kab != "Semua Wilayah":
        d = d[d['Nama Kabupaten/Kota'] == sel_kab]
    if sel_cluster != "Semua Cluster":
        d = d[d['Kategori Cluster'] == sel_cluster]
    if sel_search:
        d = d[d['Nama Pos Hujan'].str.contains(sel_search, case=False, na=False)]
    return d

# Session state untuk kontrol submit
if 'show_result' not in st.session_state:
    st.session_state.show_result = True  # default tampil semua

if submitted:
    st.session_state.show_result = True

df = apply_filter(df_all)

# ─────────────────────────────────────────────
# KPI CARDS
# ─────────────────────────────────────────────

def metric_card(color, label, value, unit=""):
    return f"""
    <div class="metric-card {color}">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-unit">{unit}</div>
    </div>"""

avg_val  = f"{df['Curah Hujan (mm)'].mean():.1f}" if not df.empty else "—"
max_val  = f"{df['Curah Hujan (mm)'].max():.0f}"  if not df.empty else "—"
min_val  = f"{df['Curah Hujan (mm)'].min():.0f}"  if not df.empty else "—"
n_tinggi = len(df[df['Kategori Cluster']=='Tinggi']) if not df.empty else 0

c1, c2, c3, c4, c5 = st.columns(5)
with c1: st.markdown(metric_card("blue",   "Total Pos Hujan", len(df), f"dari {len(df_all)} data"), unsafe_allow_html=True)
with c2: st.markdown(metric_card("green",  "Rata-rata",       avg_val, "mm / dasarian"), unsafe_allow_html=True)
with c3: st.markdown(metric_card("amber",  "Tertinggi",       max_val, "mm"), unsafe_allow_html=True)
with c4: st.markdown(metric_card("purple", "Terendah",        min_val, "mm"), unsafe_allow_html=True)
with c5: st.markdown(metric_card("red",    "Cluster Tinggi",  n_tinggi, "pos waspada"), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "  📊  Dashboard  ",
    "  📈  Analisis  ",
    "  🗺️  Peta  ",
    "  📋  Data  ",
    "  💡  Insight  ",
])

# Plotly dark template
PTMPL = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(13,30,51,0.6)",
    font=dict(family="Inter", color="#c8d8f0"),
    margin=dict(t=40, b=20, l=10, r=10),
)

def sec(icon, title):
    st.markdown(f"""
    <div class="section-header">
        <span class="icon">{icon}</span>
        <h3>{title}</h3>
        <div class="section-divider"></div>
    </div>""", unsafe_allow_html=True)

# ──────────────── TAB 1 ─ DASHBOARD ────────────────

with tab1:
    st.markdown('<div class="result-container">', unsafe_allow_html=True)

    if df.empty:
        st.warning("⚠️ Tidak ada data untuk filter yang dipilih.")
    else:
        sec("📊", "Distribusi Curah Hujan per Pos Hujan")
        fig_bar = px.bar(
            df.sort_values('Curah Hujan (mm)', ascending=False),
            x='Nama Pos Hujan', y='Curah Hujan (mm)',
            color='Kategori Cluster', color_discrete_map=COLOR_MAP,
            hover_data=['Nama Kabupaten/Kota', 'Dasarian', 'Kategori Cluster'],
            category_orders={'Kategori Cluster': ['Tinggi', 'Menengah', 'Rendah']},
        )
        fig_bar.update_layout(**PTMPL, height=380,
            xaxis=dict(tickangle=-40, tickfont=dict(size=9), showgrid=False),
            yaxis=dict(gridcolor="#1e3a5f", title="Curah Hujan (mm)"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )
        fig_bar.update_traces(marker_line_width=0)
        st.plotly_chart(fig_bar, use_container_width=True)

        col_a, col_b = st.columns(2)

        with col_a:
            sec("🥧", "Proporsi Cluster")
            fig_pie = px.pie(
                df, names='Kategori Cluster',
                color='Kategori Cluster', color_discrete_map=COLOR_MAP,
                hole=0.55,
            )
            fig_pie.update_layout(**PTMPL, height=300,
                legend=dict(orientation="h", yanchor="bottom", y=-0.15))
            fig_pie.update_traces(
                textinfo='percent+label',
                textfont=dict(size=12, family='JetBrains Mono'),
                marker=dict(line=dict(color='#07111f', width=2)),
            )
            st.plotly_chart(fig_pie, use_container_width=True)

        with col_b:
            sec("🏙️", "Rata-rata per Kabupaten/Kota")
            avg_kab = (
                df.groupby('Nama Kabupaten/Kota')['Curah Hujan (mm)']
                .mean().reset_index()
                .sort_values('Curah Hujan (mm)', ascending=True)
            )
            fig_kab = px.bar(
                avg_kab, x='Curah Hujan (mm)', y='Nama Kabupaten/Kota',
                orientation='h',
                color='Curah Hujan (mm)',
                color_continuous_scale=[[0,'#00d4ff'],[0.5,'#ffb300'],[1,'#ff5252']],
            )
            fig_kab.update_layout(**PTMPL, height=300,
                coloraxis_showscale=False,
                xaxis=dict(gridcolor="#1e3a5f", title="Rata-rata (mm)"),
                yaxis=dict(title="", tickfont=dict(size=10)),
            )
            fig_kab.update_traces(marker_line_width=0)
            st.plotly_chart(fig_kab, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ──────────────── TAB 2 ─ ANALISIS ────────────────

with tab2:

    if df.empty:
        st.warning("⚠️ Tidak ada data untuk filter yang dipilih.")
    else:
        col_a, col_b = st.columns(2)

        with col_a:
            sec("📉", "Elbow Method — Penentuan K Optimal")
            fig_elbow = go.Figure()
            fig_elbow.add_trace(go.Scatter(
                x=list(range(1, 11)), y=wcss,
                mode='lines+markers',
                line=dict(color='#00d4ff', width=2.5),
                marker=dict(size=7, color='#00d4ff',
                            line=dict(color='#07111f', width=1.5)),
                fill='tozeroy', fillcolor='rgba(0,212,255,0.06)',
            ))
            fig_elbow.add_vline(x=3, line_dash="dot", line_color="#ffb300",
                                annotation_text=" K = 3",
                                annotation_font=dict(color="#ffb300", size=11))
            fig_elbow.update_layout(**PTMPL, height=300,
                xaxis=dict(tickvals=list(range(1,11)), title="Jumlah Cluster (K)",
                           gridcolor="#1e3a5f", dtick=1),
                yaxis=dict(title="WCSS", gridcolor="#1e3a5f"),
            )
            st.plotly_chart(fig_elbow, use_container_width=True)

        with col_b:
            sec("📦", "Sebaran Nilai per Cluster")
            fig_box = px.box(
                df, x='Kategori Cluster', y='Curah Hujan (mm)',
                color='Kategori Cluster', color_discrete_map=COLOR_MAP,
                category_orders={'Kategori Cluster': ['Rendah','Menengah','Tinggi']},
                points='outliers',
            )
            fig_box.update_layout(**PTMPL, height=300,
                xaxis=dict(title=""), yaxis=dict(title="Curah Hujan (mm)", gridcolor="#1e3a5f"),
                showlegend=False,
            )
            st.plotly_chart(fig_box, use_container_width=True)

        sec("🕒", "Tren Curah Hujan per Periode")
        tren = (
            df.groupby(['Periode', 'Kategori Cluster'])['Curah Hujan (mm)']
            .mean().reset_index()
        )
        fig_line = px.line(
            tren, x='Periode', y='Curah Hujan (mm)',
            color='Kategori Cluster', color_discrete_map=COLOR_MAP,
            markers=True,
            category_orders={'Kategori Cluster': ['Rendah','Menengah','Tinggi']},
        )
        fig_line.update_layout(**PTMPL, height=280,
            xaxis=dict(title="", gridcolor="#1e3a5f", tickangle=-20),
            yaxis=dict(title="Rata-rata (mm)", gridcolor="#1e3a5f"),
            legend=dict(orientation="h", y=1.1),
        )
        fig_line.update_traces(line_width=2.5, marker_size=7)
        st.plotly_chart(fig_line, use_container_width=True)

        col_c, col_d = st.columns(2)

        with col_c:
            sec("🏆", "Top 10 Pos Hujan Tertinggi")
            top10 = df.nlargest(10, 'Curah Hujan (mm)')[
                ['Nama Pos Hujan','Nama Kabupaten/Kota','Curah Hujan (mm)','Kategori Cluster','Dasarian']
            ].reset_index(drop=True)
            st.dataframe(top10, use_container_width=True, height=300)

        with col_d:
            sec("📊", "Statistik per Cluster")
            stats = (
                df.groupby('Kategori Cluster')['Curah Hujan (mm)']
                .describe().round(2)
            )
            st.dataframe(stats, use_container_width=True, height=300)

# ──────────────── TAB 3 ─ PETA ────────────────

with tab3:

    sec("🗺️", "Sebaran Spasial Pos Hujan NTB")

    if df.empty:
        st.warning("⚠️ Tidak ada data untuk filter yang dipilih.")
    else:
        df_map = df.dropna(subset=['Latitude','Longitude'])
        df_map = df_map[
            df_map['Latitude'].between(-10, 0) &
            df_map['Longitude'].between(114, 121)
        ]

        if df_map.empty:
            st.warning("Koordinat tidak valid untuk data ini.")
        else:
            fig_map = px.scatter_mapbox(
                df_map,
                lat="Latitude", lon="Longitude",
                color="Kategori Cluster", color_discrete_map=COLOR_MAP,
                size="Curah Hujan (mm)", size_max=22,
                hover_name="Nama Pos Hujan",
                hover_data={
                    'Nama Kabupaten/Kota': True,
                    'Curah Hujan (mm)': True,
                    'Dasarian': True,
                    'Kategori Cluster': True,
                    'Latitude': False, 'Longitude': False,
                },
                zoom=7.2,
                center={"lat": -8.65, "lon": 117.5},
                mapbox_style="carto-darkmatter",
                opacity=0.9,
                height=560,
            )
            fig_map.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                margin=dict(t=10, b=10, l=0, r=0),
                legend=dict(
                    bgcolor="#0d1e33", bordercolor="#1e3a5f", borderwidth=1,
                    font=dict(color="#c8d8f0"), title=dict(text="Cluster"),
                    orientation="v",
                ),
            )
            st.plotly_chart(fig_map, use_container_width=True)
            st.caption(f"🔵 {len(df_map[df_map['Kategori Cluster']=='Rendah'])} Rendah  "
                       f"🟠 {len(df_map[df_map['Kategori Cluster']=='Menengah'])} Menengah  "
                       f"🔴 {len(df_map[df_map['Kategori Cluster']=='Tinggi'])} Tinggi  · "
                       f"Total {len(df_map)} pos hujan ditampilkan")

# ──────────────── TAB 4 ─ DATA ────────────────

with tab4:

    sec("📋", "Tabel Data Hasil Clustering")

    kolom = ['Nama Pos Hujan','Nama Desa','Nama Kecamatan',
             'Nama Kabupaten/Kota','Curah Hujan (mm)',
             'Dasarian','Bulan','Tahun','Kategori Cluster']

    st.dataframe(
        df[kolom].reset_index(drop=True),
        use_container_width=True, height=420,
    )

    col_d1, col_d2 = st.columns(2)
    with col_d1:
        st.download_button(
            "⬇️  Download Data Terfilter (.csv)",
            df.to_csv(index=False),
            "curah_hujan_filtered.csv", "text/csv",
            use_container_width=True,
        )
    with col_d2:
        st.download_button(
            "⬇️  Download Semua Data (.csv)",
            df_all.to_csv(index=False),
            "curah_hujan_semua.csv", "text/csv",
            use_container_width=True,
        )

# ──────────────── TAB 5 ─ INSIGHT ────────────────

with tab5:

    if df.empty:
        st.warning("⚠️ Tidak ada data untuk filter yang dipilih.")
    else:
        tertinggi = df.loc[df['Curah Hujan (mm)'].idxmax()]
        terendah  = df.loc[df['Curah Hujan (mm)'].idxmin()]
        n_rendah   = len(df[df['Kategori Cluster']=='Rendah'])
        n_menengah = len(df[df['Kategori Cluster']=='Menengah'])
        n_tinggi   = len(df[df['Kategori Cluster']=='Tinggi'])

        col_i1, col_i2 = st.columns(2)
        with col_i1:
            st.success(f"📈 **Tertinggi:** {tertinggi['Nama Pos Hujan']} "
                       f"({tertinggi['Nama Kabupaten/Kota']}) — "
                       f"**{tertinggi['Curah Hujan (mm)']} mm**")
        with col_i2:
            st.info(f"📉 **Terendah:** {terendah['Nama Pos Hujan']} "
                    f"({terendah['Nama Kabupaten/Kota']}) — "
                    f"**{terendah['Curah Hujan (mm)']} mm**")

        sec("📊", "Distribusi Cluster per Kabupaten/Kota")
        ck = (
            df.groupby(['Nama Kabupaten/Kota','Kategori Cluster'])
            .size().reset_index(name='Jumlah')
        )
        fig_stack = px.bar(
            ck, x='Nama Kabupaten/Kota', y='Jumlah',
            color='Kategori Cluster', color_discrete_map=COLOR_MAP,
            barmode='stack',
            category_orders={'Kategori Cluster': ['Rendah','Menengah','Tinggi']},
        )
        fig_stack.update_layout(**PTMPL, height=320,
            xaxis=dict(tickangle=-30, title="", showgrid=False),
            yaxis=dict(title="Jumlah Pos", gridcolor="#1e3a5f"),
            legend=dict(orientation="h", y=1.1),
        )
        fig_stack.update_traces(marker_line_width=0)
        st.plotly_chart(fig_stack, use_container_width=True)

        sec("🏙️", "Ringkasan per Kabupaten/Kota")
        ringkasan = (
            df.groupby('Nama Kabupaten/Kota')
            .agg(
                Pos=('Nama Pos Hujan','count'),
                Rata_rata=('Curah Hujan (mm)','mean'),
                Maks=('Curah Hujan (mm)','max'),
                Min=('Curah Hujan (mm)','min'),
            ).round(1).reset_index()
            .rename(columns={'Nama Kabupaten/Kota':'Wilayah','Rata_rata':'Rata-rata (mm)',
                             'Maks':'Maks (mm)','Min':'Min (mm)'})
            .sort_values('Rata-rata (mm)', ascending=False)
        )
        st.dataframe(ringkasan, use_container_width=True)

        st.markdown(f"""
---
<div style="background:#0d1e33;border:1px solid #1e3a5f;border-radius:12px;padding:1.5rem 2rem;margin-top:1rem;">
<h3 style="color:#00d4ff;font-size:1rem;font-weight:700;letter-spacing:-.01em;margin:0 0 1rem 0;">
📝 Kesimpulan Analisis K-Means Clustering
</h3>
<table style="width:100%;border-collapse:collapse;font-size:.85rem;">
<tr style="border-bottom:1px solid #1e3a5f;">
  <td style="padding:.5rem 1rem .5rem 0;color:#5a8ab0;">Total Data</td>
  <td style="color:#fff;font-family:'JetBrains Mono',monospace;font-weight:600;">{len(df)} pos hujan</td>
</tr>
<tr style="border-bottom:1px solid #1e3a5f;">
  <td style="padding:.5rem 1rem .5rem 0;color:#5a8ab0;">Rata-rata</td>
  <td style="color:#fff;font-family:'JetBrains Mono',monospace;font-weight:600;">{df['Curah Hujan (mm)'].mean():.2f} mm</td>
</tr>
<tr style="border-bottom:1px solid #1e3a5f;">
  <td style="padding:.5rem 1rem .5rem 0;color:#5a8ab0;">🔵 Cluster Rendah</td>
  <td style="color:#00d4ff;font-family:'JetBrains Mono',monospace;font-weight:600;">{n_rendah} pos · 0–18 mm</td>
</tr>
<tr style="border-bottom:1px solid #1e3a5f;">
  <td style="padding:.5rem 1rem .5rem 0;color:#5a8ab0;">🟠 Cluster Menengah</td>
  <td style="color:#ffb300;font-family:'JetBrains Mono',monospace;font-weight:600;">{n_menengah} pos · 19–61 mm</td>
</tr>
<tr>
  <td style="padding:.5rem 1rem .5rem 0;color:#5a8ab0;">🔴 Cluster Tinggi</td>
  <td style="color:#ff5252;font-family:'JetBrains Mono',monospace;font-weight:600;">{n_tinggi} pos · ≥65 mm</td>
</tr>
</table>
<p style="color:#5a8ab0;font-size:.78rem;margin:1rem 0 0 0;line-height:1.7;">
Metode K-Means (K=3) berhasil mengelompokkan intensitas curah hujan di NTB.
Jumlah cluster optimal ditentukan menggunakan <b style="color:#7fa8d0">Elbow Method</b>.
Hasil ini dapat digunakan untuk perencanaan tata kelola air dan
mitigasi bencana hidrometeorologi di Provinsi Nusa Tenggara Barat.
</p>
</div>
""", unsafe_allow_html=True)
