import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# 1. Konfigurasi Halaman Streamlit
st.set_page_config(
    page_title="Air Quality Dashboard - Nongzhanguan",
    page_icon="🌤️",
    layout="wide"
)

# Set tema seaborn
sns.set_theme(style="whitegrid")

# 2. Memuat data yang sudah dibersihkan (main_data.csv)
@st.cache_data
def load_data():
    try:
        # Pemuatan lokal (folder dashboard)
        df = pd.read_csv("dashboard/main_data.csv")
    except Exception:
        # Fallback URL jika dijalankan via repository root
        url = "https://raw.githubusercontent.com/nurafitriyana/proyek-analisis-data/main/dashboard/main_data.csv"
        df = pd.read_csv(url)
    
    df['datetime'] = pd.to_datetime(df['datetime'])
    return df

df = load_data()

# 3. Sidebar: Filter Rentang Waktu
st.sidebar.header("📍 Filter Data")
min_date = df['datetime'].dt.date.min()
max_date = df['datetime'].dt.date.max()

date_range = st.sidebar.date_input(
    label="Pilih Rentang Tanggal:",
    min_value=min_date,
    max_value=max_date,
    value=[min_date, max_date]
)

if len(date_range) == 2:
    start_date, end_date = date_range
elif len(date_range) == 1:
    start_date = date_range[0]
    end_date = max_date
else:
    start_date = min_date
    end_date = max_date

filtered_df = df[
    (df['datetime'].dt.date >= start_date) & 
    (df['datetime'].dt.date <= end_date)
].copy()

# 4. Header Dashboard
st.title("🌤️ Air Quality Analytics Dashboard")
st.caption("Stasiun Nongzhanguan (Maret 2013 - Februari 2017)")
st.markdown("---")

# 5. Key Metrics (KPIs)
col1, col2, col3, col4 = st.columns(4)

avg_pm25 = filtered_df['PM2.5'].mean() if not filtered_df.empty else 0
avg_pm10 = filtered_df['PM10'].mean() if not filtered_df.empty else 0
avg_wspm = filtered_df['WSPM'].mean() if not filtered_df.empty else 0
total_records = len(filtered_df)

with col1:
    st.metric("Rata-Rata PM2.5", f"{avg_pm25:.2f} µg/m³")

with col2:
    st.metric("Rata-Rata PM10", f"{avg_pm10:.2f} µg/m³")

with col3:
    st.metric("Rata-Rata Kecepatan Angin", f"{avg_wspm:.2f} m/s")

with col4:
    st.metric("Total Observasi Jam", f"{total_records:,}")

st.markdown("---")

# ------------------------------------------------------------------------------
# PERTANYAAN 1: Tren Bulanan PM2.5 dan PM10
# ------------------------------------------------------------------------------
st.subheader("📈 1. Tren Bulanan Konsentrasi PM2.5 dan PM10")

if not filtered_df.empty:
    monthly_df = filtered_df.groupby(['year', 'month'])[['PM2.5', 'PM10']].mean().reset_index()
    monthly_df['year_month'] = monthly_df['year'].astype(str) + '-' + monthly_df['month'].astype(str).str.zfill(2)

    fig1, ax1 = plt.subplots(figsize=(12, 5))
    ax1.plot(monthly_df['year_month'], monthly_df['PM2.5'], marker='o', linewidth=2, color='#d95f02', label='PM2.5')
    ax1.plot(monthly_df['year_month'], monthly_df['PM10'], marker='s', linewidth=2, color='#7570b3', label='PM10')
    ax1.axhline(y=35, color='red', linestyle='--', alpha=0.7, label='Batas Aman PM2.5 WHO (35 µg/m³)')

    ax1.set_xlabel("Tahun-Bulan", fontsize=10)
    ax1.set_ylabel("Konsentrasi (µg/m³)", fontsize=10)
    ax1.tick_params(axis='x', rotation=60, labelsize=8)
    ax1.legend(loc='upper right')
    ax1.grid(True, linestyle=':', alpha=0.6)

    st.pyplot(fig1)

    with st.expander("💡 Insight Tren Bulanan"):
        st.write(
            "Konsentrasi PM2.5 dan PM10 menunjukkan pola musiman yang konsisten, memuncak pada musim dingin "
            "(Desember–Januari) dan berada pada level terendah pada musim panas. "
            "Puncak polusi tertinggi PM2.5 terjadi pada **Desember 2015 (161.37 µg/m³)** dan PM10 pada **Maret 2013 (205.80 µg/m³)**."
        )
else:
    st.warning("Tidak ada data pada rentang tanggal yang dipilih.")

st.markdown("---")

# ------------------------------------------------------------------------------
# PERTANYAAN 2: Pengaruh Kecepatan Angin & Pola Diurnal
# ------------------------------------------------------------------------------
st.subheader("💨 2. Analisis Kecepatan Angin (WSPM) & Pola Diurnal PM2.5")

if not filtered_df.empty:
    tab1, tab2 = st.tabs(["Pengaruh Angin (WSPM) terhadap PM10", "Pola Diurnal Harian PM2.5"])

    # TAB 1: Pengaruh Kecepatan Angin terhadap PM10
    with tab1:
        bins = [-np.inf, 1.5, 3.0, np.inf]
        labels = ['Rendah (<= 1.5 m/s)', 'Sedang (1.5 - 3.0 m/s)', 'Tinggi (> 3.0 m/s)']
        filtered_df['WSPM_category'] = pd.cut(filtered_df['WSPM'], bins=bins, labels=labels)
        
        wspm_summary = filtered_df.groupby('WSPM_category', observed=False)['PM10'].mean().reset_index()

        fig2, ax2 = plt.subplots(figsize=(8, 4.5))
        sns.barplot(data=wspm_summary, x='WSPM_category', y='PM10', palette='Blues_d', ax=ax2)
        
        ax2.set_title("Rata-rata Konsentrasi PM10 Berdasarkan Kategori Kecepatan Angin", fontsize=12, pad=10)
        ax2.set_xlabel("Kategori Kecepatan Angin (WSPM)", fontsize=10)
        ax2.set_ylabel("Rata-rata PM10 (µg/m³)", fontsize=10)

        for p in ax2.patches:
            ax2.annotate(f"{p.get_height():.2f}", 
                        (p.get_x() + p.get_width() / 2., p.get_height()), 
                        ha='center', va='center', xytext=(0, 5), textcoords='offset points')

        st.pyplot(fig2)
        st.info(
            "💡 **Insight Angin & PM10:** Terdapat korelasi negatif antara kecepatan angin dan PM10. "
            "Semakin kencang hembusan angin (> 3.0 m/s), konsentrasi PM10 turun signifikan hingga 61.40 µg/m³ karena efek dispersi partikel."
        )

    # TAB 2: Pola Diurnal PM2.5
    with tab2:
        hourly_df = filtered_df.groupby('hour')['PM2.5'].mean().reset_index()

        fig3, ax3 = plt.subplots(figsize=(10, 4.5))
        sns.lineplot(data=hourly_df, x='hour', y='PM2.5', marker='o', color='#1b9e77', linewidth=2.5, ax=ax3)

        max_h = hourly_df.loc[hourly_df['PM2.5'].idxmax()]
        min_h = hourly_df.loc[hourly_df['PM2.5'].idxmin()]

        ax3.scatter(max_h['hour'], max_h['PM2.5'], color='red', s=90, zorder=5, label=f"Puncak: Jam {int(max_h['hour'])} ({max_h['PM2.5']:.1f} µg/m³)")
        ax3.scatter(min_h['hour'], min_h['PM2.5'], color='blue', s=90, zorder=5, label=f"Terendah: Jam {int(min_h['hour'])} ({min_h['PM2.5']:.1f} µg/m³)")

        ax3.set_xlabel("Jam dalam Sehari (Beijing Time / CST)", fontsize=10)
        ax3.set_ylabel("Rata-Rata PM2.5 (µg/m³)", fontsize=10)
        ax3.set_xticks(range(0, 24))
        ax3.legend(loc='upper right')
        ax3.grid(True, linestyle=':', alpha=0.6)

        st.pyplot(fig3)
        st.info(
            "💡 **Insight Diurnal:** Paparan polusi PM2.5 terendah terjadi di siang-sore hari (13.00–16.00 CST), "
            "sedangkan akumulasi polutan meningkat tajam pada malam hari hingga tengah malam (21.00–02.00 CST)."
        )

st.markdown("---")
st.caption("Copyright © Dicoding Data Science Project 2026 - Stasiun Nongzhanguan")
