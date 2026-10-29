import pandas as pd
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

# Memuat dan membersihkan data langsung dari URL repositori GitHub Anda
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/nurafitriyana/proyek-analisis-data/main/PRSA_Data_Nongzhanguan_20130301-20170228.csv"
    df = pd.read_csv(url)
    
    # Pembersihan missing values
    numeric_cols = ['PM2.5', 'PM10', 'SO2', 'NO2', 'CO', 'O3', 'TEMP', 'PRES', 'DEWP', 'RAIN', 'WSPM']
    df[numeric_cols] = df[numeric_cols].interpolate(method='linear')
    df.bfill(inplace=True)
    df.ffill(inplace=True)
    
    # Format datetime
    df['datetime'] = pd.to_datetime(df[['year', 'month', 'day', 'hour']])
    return df

df = load_data()

# Sidebar: Filter Rentang Waktu
st.sidebar.header("📍 Filter Data")
min_date = df['datetime'].dt.date.min()
max_date = df['datetime'].dt.date.max()

start_date, end_date = st.sidebar.date_input(
    label="Pilih Rentang Tanggal:",
    min_value=min_date,
    max_value=max_date,
    value=[min_date, max_date]
)

# Filter dataframe berdasarkan tanggal
filtered_df = df[
    (df['datetime'].dt.date >= start_date) & 
    (df['datetime'].dt.date <= end_date)
]

# Header Dashboard
st.title("🌤️ Air Quality Analytics Dashboard")
st.subheader("Stasiun Nongzhanguan (2013 - 2017)")
st.markdown("---")

# Key Metrics (KPIs)
col1, col2, col3, col4 = st.columns(4)

avg_pm25 = filtered_df['PM2.5'].mean()
avg_pm10 = filtered_df['PM10'].mean()
max_pm25 = filtered_df['PM2.5'].max()
total_records = len(filtered_df)

with col1:
    st.metric("Rata-Rata PM2.5", f"{avg_pm25:.2f} µg/m³")

with col2:
    st.metric("Rata-Rata PM10", f"{avg_pm10:.2f} µg/m³")

with col3:
    st.metric("PM2.5 Tertinggi", f"{max_pm25:.1f} µg/m³")

with col4:
    st.metric("Total Observasi Jam", f"{total_records:,}")

st.markdown("---")

# Visualisasi 1: Tren Bulanan
st.subheader("📈 1. Tren Bulanan Konsentrasi PM2.5 dan PM10")

monthly_df = filtered_df.groupby(['year', 'month'])[['PM2.5', 'PM10']].mean().reset_index()
monthly_df['year_month'] = monthly_df['year'].astype(str) + '-' + monthly_df['month'].astype(str).str.zfill(2)

fig1, ax1 = plt.subplots(figsize=(12, 5))
ax1.plot(monthly_df['year_month'], monthly_df['PM2.5'], marker='o', linewidth=2, color='#d95f02', label='PM2.5')
ax1.plot(monthly_df['year_month'], monthly_df['PM10'], marker='s', linewidth=2, color='#7570b3', label='PM10')
ax1.axhline(y=35, color='red', linestyle='--', alpha=0.7, label='Batas Aman PM2.5 (35 µg/m³)')

ax1.set_xlabel("Tahun-Bulan", fontsize=10)
ax1.set_ylabel("Konsentrasi (µg/m³)", fontsize=10)
ax1.tick_params(axis='x', rotation=60, labelsize=8)
ax1.legend(loc='upper right')
ax1.grid(True, linestyle=':', alpha=0.6)

st.pyplot(fig1)

with st.expander("💡 Insight Tren Bulanan"):
    st.write(
        "Kualitas udara menunjukkan pola musiman berulang. Polusi puncak ($PM_{2.5} > 120\\,\\mu\\text{g/m}^3$) "
        "konsisten terjadi pada musim dingin (Desember–Januari), sedangkan kualitas udara relatif lebih baik "
        "pada musim panas (Mei–Agustus)."
    )

st.markdown("---")

# Visualisasi 2: Pola Diurnal
st.subheader("⏰ 2. Pola Distribusi Diurnal PM2.5 Per Jam (00.00 - 23.00)")

hourly_df = filtered_df.groupby('hour')['PM2.5'].mean().reset_index()

fig2, ax2 = plt.subplots(figsize=(10, 4.5))
sns.lineplot(data=hourly_df, x='hour', y='PM2.5', marker='o', color='#1b9e77', linewidth=2.5, ax=ax2)

max_h = hourly_df.loc[hourly_df['PM2.5'].idxmax()]
min_h = hourly_df.loc[hourly_df['PM2.5'].idxmin()]

ax2.scatter(max_h['hour'], max_h['PM2.5'], color='red', s=90, zorder=5, label=f"Puncak: Jam {int(max_h['hour'])} ({max_h['PM2.5']:.1f} µg/m³)")
ax2.scatter(min_h['hour'], min_h['PM2.5'], color='blue', s=90, zorder=5, label=f"Terendah: Jam {int(min_h['hour'])} ({min_h['PM2.5']:.1f} µg/m³)")

ax2.set_xlabel("Jam dalam Sehari", fontsize=10)
ax2.set_ylabel("Rata-Rata PM2.5 (µg/m³)", fontsize=10)
ax2.set_xticks(range(0, 24))
ax2.legend(loc='upper right')
ax2.grid(True, linestyle=':', alpha=0.6)

st.pyplot(fig2)

with st.expander("💡 Insight Pola Diurnal"):
    st.write(
        "Paparan polusi terendah terjadi di siang-sore hari (13.00–16.00) karena bantuan dispersi konveksi udara hangat. "
        "Sebaliknya, akumulasi polutan meningkat tajam pada malam hari hingga tengah malam (21.00–02.00)."
    )

st.markdown("---")
st.caption("Copyright © Dicoding Data Science Project 2026 - Stasiun Nongzhanguan")
