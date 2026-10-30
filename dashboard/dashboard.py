import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# Konfigurasi Halaman Streamlit
st.set_page_config(
    page_title="Air Quality Dashboard - Nongzhanguan",
    page_icon="🌤️",
    layout="wide"
)

# Set tema seaborn
sns.set_theme(style="whitegrid")

# Fungsi kategorisasi kecepatan angin (WSPM)
def categorize_wspm(speed):
    if speed <= 1.5:
        return 'Rendah (<= 1.5 m/s)'
    elif speed <= 3.0:
        return 'Sedang (1.5 - 3.0 m/s)'
    else:
        return 'Tinggi (> 3.0 m/s)'

# Memuat data yang sudah dibersihkan (main_data.csv)
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/nurafitriyana/proyek-analisis-data/main/dashboard/main_data.csv"
    df = pd.read_csv(url)
    
    # Memastikan kolom datetime berformat datetime64
    df['datetime'] = pd.to_datetime(df['datetime'])
    
    # Menambahkan kolom kategori WSPM jika belum ada
    if 'WSPM_category' not in df.columns and 'WSPM' in df.columns:
        df['WSPM_category'] = df['WSPM'].apply(categorize_wspm)
        
    return df

df = load_data()

# Sidebar: Filter Rentang Waktu
st.sidebar.header("📍 Filter Data")
min_date = df['datetime'].dt.date.min()
max_date = df['datetime'].dt.date.max()

# Mengambil input rentang tanggal dari pengguna
date_range = st.sidebar.date_input(
    label="Pilih Rentang Tanggal:",
    min_value=min_date,
    max_value=max_date,
    value=[min_date, max_date]
)

# Penanganan unpacking tuple tanggal agar tidak error saat memilih 1 tanggal
if len(date_range) == 2:
    start_date, end_date = date_range
elif len(date_range) == 1:
    start_date = date_range[0]
    end_date = max_date
else:
    start_date = min_date
    end_date = max_date

# Filter dataframe berdasarkan tanggal yang dipilih
filtered_df = df[
    (df['datetime'].dt.date >= start_date) & 
    (df['datetime'].dt.date <= end_date)
].copy()

# Header Dashboard
st.title("🌤️ Air Quality Analytics Dashboard")
st.subheader("Stasiun Nongzhanguan (2013 - 2017)")
st.markdown("---")

# Key Metrics (KPIs)
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

# ==============================================================================
# BAGIAN 1: PERTANYAAN BISNIS 1
# Tren Bulanan PM2.5 & PM10 serta Penentuan Puncak Polusi Musiman
# ==============================================================================
st.header("📌 Pertanyaan 1: Tren Bulanan & Titik Puncak Polusi (PM2.5 dan PM10)")

if not filtered_df.empty:
    col_q1_1, col_q1_2 = st.columns(2)

    # 1.1 Tren Bulanan Sepanjang Periode
    with col_q1_1:
        st.subheader("📈 Tren Konsentrasi Bulanan (2013 - 2017)")
        monthly_df = filtered_df.groupby(['year', 'month'])[['PM2.5', 'PM10']].mean().reset_index()
        monthly_df['year_month'] = monthly_df['year'].astype(str) + '-' + monthly_df['month'].astype(str).str.zfill(2)

        fig1, ax1 = plt.subplots(figsize=(8, 5))
        ax1.plot(monthly_df['year_month'], monthly_df['PM2.5'], marker='o', linewidth=2, color='skyblue', label='PM2.5')
        ax1.plot(monthly_df['year_month'], monthly_df['PM10'], marker='s', linewidth=2, color='salmon', label='PM10')
        ax1.axhline(y=35, color='red', linestyle='--', alpha=0.7, label='Batas Aman PM2.5 (35 µg/m³)')

        ax1.set_xlabel("Tahun-Bulan", fontsize=9)
        ax1.set_ylabel("Konsentrasi (µg/m³)", fontsize=9)
        ax1.tick_params(axis='x', rotation=90, labelsize=7)
        ax1.legend(loc='upper right')
        ax1.grid(True, linestyle=':', alpha=0.6)
        st.pyplot(fig1)

    # 1.2 Rata-Rata Berdasarkan Bulan (Mencari Puncak Polusi Musiman)
    with col_q1_2:
        st.subheader("📊 Rata-Rata Konsentrasi per Bulan (Musiman)")
        monthly_seasonality = filtered_df.groupby('month')[['PM2.5', 'PM10']].mean().reset_index()

        fig2, ax2 = plt.subplots(figsize=(8, 5))
        x = np.arange(len(monthly_seasonality['month']))
        width = 0.35

        ax2.bar(x - width/2, monthly_seasonality['PM2.5'], width, label='PM2.5', color='skyblue')
        ax2.bar(x + width/2, monthly_seasonality['PM10'], width, label='PM10', color='salmon')

        ax2.set_xlabel("Bulan", fontsize=9)
        ax2.set_ylabel("Konsentrasi (µg/m³)", fontsize=9)
        ax2.set_xticks(x)
        ax2.set_xticklabels([f'Bulan {m}' for m in monthly_seasonality['month']], fontsize=8)
        ax2.legend(loc='upper right')
        ax2.grid(axis='y', linestyle=':', alpha=0.6)
        st.pyplot(fig2)

    with st.expander("💡 Insight Pertanyaan 1"):
        st.write(
            "1. **Tren Bulanan:** Konsentrasi PM2.5 dan PM10 secara konsisten berada di atas batas aman yang ditetapkan.\n"
            "2. **Puncak Polusi Musiman:** Tingkat polusi tertinggi secara konsisten tercatat pada **bulan-bulan musim dingin (Desember–Januari)** "
            "akibat penggunaan pemanas lokal dan kondisi inversi suhu atmosphere."
        )
else:
    st.warning("Tidak ada data pada rentang tanggal yang dipilih.")

st.markdown("---")

# ==============================================================================
# BAGIAN 2: PERTANYAAN BISNIS 2
# Hubungan Kecepatan Angin (WSPM) vs PM10 dan Pola Diurnal PM2.5
# ==============================================================================
st.header("📌 Pertanyaan 2: Pengaruh Kecepatan Angin (WSPM) & Variasi Harian (Diurnal)")

if not filtered_df.empty:
    col_q2_1, col_q2_2, col_q2_3 = st.columns(3)

    # 2.1 Regression Plot WSPM vs PM10
    with col_q2_1:
        st.subheader("📉 Hubungan WSPM vs PM10")
        fig3, ax3 = plt.subplots(figsize=(6, 5))
        sns.regplot(
            x='WSPM', 
            y='PM10', 
            data=filtered_df, 
            ax=ax3,
            scatter_kws={'alpha': 0.1, 's': 10, 'color': 'steelblue'}, 
            line_kws={'color': 'red', 'linewidth': 2}
        )
        ax3.set_xlabel("Kecepatan Angin / WSPM (m/s)", fontsize=9)
        ax3.set_ylabel("PM10 (µg/m³)", fontsize=9)
        st.pyplot(fig3)

    # 2.2 Boxplot PM10 berdasarkan Kategori Kecepatan Angin
    with col_q2_2:
        st.subheader("📦 PM10 per Kategori Angin")
        fig4, ax4 = plt.subplots(figsize=(6, 5))
        sns.boxplot(
            x='WSPM_category', 
            y='PM10', 
            data=filtered_df, 
            order=['Rendah (<= 1.5 m/s)', 'Sedang (1.5 - 3.0 m/s)', 'Tinggi (> 3.0 m/s)'],
            palette='Set2',
            ax=ax4
        )
        ax4.set_xlabel("Kategori Kecepatan Angin", fontsize=9)
        ax4.set_ylabel("PM10 (µg/m³)", fontsize=9)
        ax4.tick_params(axis='x', rotation=20, labelsize=8)
        st.pyplot(fig4)

    # 2.3 Line Plot Variasi Diurnal PM2.5 Per Jam
    with col_q2_3:
        st.subheader("⏰ Variasi Harian (Diurnal) PM2.5")
        hourly_df = filtered_df.groupby('hour')['PM2.5'].mean().reset_index()

        fig5, ax5 = plt.subplots(figsize=(6, 5))
        sns.lineplot(
            data=hourly_df, 
            x='hour', 
            y='PM2.5', 
            marker='o', 
            color='purple', 
            linewidth=2, 
            ax=ax5
        )
        ax5.set_xlabel("Jam (00.00 - 23.00)", fontsize=9)
        ax5.set_ylabel("Rata-Rata PM2.5 (µg/m³)", fontsize=9)
        ax5.set_xticks(range(0, 24, 4))
        ax5.grid(True, linestyle=':', alpha=0.6)
        st.pyplot(fig5)

    with st.expander("💡 Insight Pertanyaan 2"):
        st.write(
            "1. **Pengaruh Kecepatan Angin:** Terdapat hubungan korelasi negatif antara kecepatan angin (WSPM) dan tingkat PM10. "
            "Kategori angin kencang (> 3.0 m/s) secara signifikan menurunkan akumulasi PM10 melalui proses dispersi udara.\n"
            "2. **Variasi Diurnal:** Konsentrasi PM2.5 berada pada tingkat terendah saat siang-sore hari (13.00–16.00) dan mengalami peningkatan pada malam hari hingga dini hari."
        )

st.markdown("---")
st.caption("Copyright © Dicoding Data Science Project 2026 - Stasiun Nongzhanguan")
