import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Config halaman Streamlit
st.set_page_config(page_title="Air Quality Dashboard - Nongzhanguan", layout="wide")

# Load & Prep Data
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/nurafitriyana/proyek-analisis-data/refs/heads/main/PRSA_Data_Nongzhanguan_20130301-20170228.csv"
    df = pd.read_csv(url)
    numeric_cols = ['PM2.5', 'PM10', 'SO2', 'NO2', 'CO', 'O3', 'TEMP', 'PRES', 'DEWP', 'RAIN', 'WSPM']
    df[numeric_cols] = df[numeric_cols].interpolate(method='linear').bfill().ffill()
    df['datetime'] = pd.to_datetime(df[['year', 'month', 'day', 'hour']])
    
    # Binning Kecepatan Angin
    bins_wspm = [-float('inf'), 1.5, 3.0, float('inf')]
    labels_wspm = ['Rendah (<= 1.5 m/s)', 'Sedang (1.5 - 3.0 m/s)', 'Tinggi (> 3.0 m/s)']
    df['WSPM_category'] = pd.cut(df['WSPM'], bins=bins_wspm, labels=labels_wspm)
    return df

df = load_data()

# --- SIDEBAR FILTER RENTANG TANGGAL ---
st.sidebar.header("Filter Data")
min_date = df['datetime'].dt.date.min()
max_date = df['datetime'].dt.date.max()

date_range = st.sidebar.date_input(
    "Pilih Rentang Tanggal",
    value=[min_date, max_date],
    min_value=min_date,
    max_value=max_date
)

# Penanganan jika user baru memilih 1 tanggal
if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date = end_date = date_range[0] if isinstance(date_range, (list, tuple)) else date_range

# Filter Dataframe
filtered_df = df[(df['datetime'].dt.date >= start_date) & (df['datetime'].dt.date <= end_date)]

st.title("Air Quality Analysis Dashboard (Stasiun Nongzhanguan)")

# --- TAB NAVIGATION ---
tab1, tab2 = st.tabs(["Pertanyaan 1: Tren Bulanan & Puncak Polusi", "Pertanyaan 2: Pengaruh Angin & Pola Diurnal"])

# ==========================================
# TAB 1
# ==========================================
with tab1:
    st.header("Tren Konsentrasi Bulanan PM2.5 dan PM10")
    
    if filtered_df.empty:
        st.warning("⚠️ Tidak ada data pada rentang tanggal yang dipilih.")
    else:
        # Agregasi Bulanan Dinamis
        filtered_df_copy = filtered_df.copy()
        filtered_df_copy['year_month'] = filtered_df_copy['datetime'].dt.to_period('M').astype(str)
        monthly_df = filtered_df_copy.groupby('year_month')[['PM2.5', 'PM10']].mean().reset_index()
        
        # Hitung Nilai Puncak Dinamis dari Filter
        peak_pm10_row = monthly_df.loc[monthly_df['PM10'].idxmax()]
        peak_pm25_row = monthly_df.loc[monthly_df['PM2.5'].idxmax()]
        
        # Plot Grafik Tren Bulanan
        fig, ax = plt.subplots(figsize=(12, 5))
        ax.plot(monthly_df['year_month'], monthly_df['PM10'], label='PM10', color='#ff7f0e', marker='o')
        ax.plot(monthly_df['year_month'], monthly_df['PM2.5'], label='PM2.5', color='#1f77b4', marker='o')
        
        # Garis Ambang Batas WHO 2021 (Rata-rata 24-jam PM2.5 = 15 µg/m³)
        ax.axhline(15, color='red', linestyle='--', label='Batas Aman PM2.5 WHO 2021 (15 µg/m³)')
        
        plt.xticks(rotation=45, fontsize=9)
        ax.set_ylabel("Konsentrasi (µg/m³)")
        ax.set_xlabel("Bulan (CST / UTC+8)")
        ax.legend()
        st.pyplot(fig)
        
        # Teks Insight Dinamis
        st.info(f"""
        **Insight Tren Bulanan (Berdasarkan Filter Data):**
        - Puncak polusi **PM10** tertinggi terjadi pada bulan **{peak_pm10_row['year_month']}** dengan rata-rata **{peak_pm10_row['PM10']:.2f} µg/m³**.
        - Puncak polusi **PM2.5** tertinggi terjadi pada bulan **{peak_pm25_row['year_month']}** dengan rata-rata **{peak_pm25_row['PM2.5']:.2f} µg/m³**.
        """)

# ==========================================
# TAB 2
# ==========================================
with tab2:
    st.header("Analisis Kecepatan Angin & Pola Diurnal PM2.5")
    
    if filtered_df.empty:
        st.warning("⚠️ Tidak ada data pada rentang tanggal yang dipilih.")
    else:
        col1, col2 = st.columns(2)
        
        # 1. Bar Chart Kecepatan Angin vs PM10
        with col1:
            wspm_summary = filtered_df.groupby('WSPM_category', observed=False)['PM10'].mean().reset_index()
            
            fig1, ax1 = plt.subplots(figsize=(6, 4))
            sns.barplot(data=wspm_summary, x='WSPM_category', y='PM10', palette='Blues_d', ax=ax1)
            ax1.set_ylabel("Rata-rata PM10 (µg/m³)")
            ax1.set_xlabel("Kategori Kecepatan Angin")
            ax1.set_ylim(bottom=0) # Sumbu Y mulai dari nol
            
            # Annotations angka pada bar chart
            for p in ax1.patches:
                ax1.annotate(f"{p.get_height():.2f}", (p.get_x() + p.get_width() / 2., p.get_height()),
                             ha='center', va='center', xytext=(0, 5), textcoords='offset points')
            
            fig1.tight_layout()
            st.pyplot(fig1)
            
            # Nilai dinamis
            val_low = wspm_summary.loc[wspm_summary['WSPM_category']=='Rendah (<= 1.5 m/s)', 'PM10'].values[0] if len(wspm_summary) > 0 else 0
            val_med = wspm_summary.loc[wspm_summary['WSPM_category']=='Sedang (1.5 - 3.0 m/s)', 'PM10'].values[0] if len(wspm_summary) > 0 else 0
            val_high = wspm_summary.loc[wspm_summary['WSPM_category']=='Tinggi (> 3.0 m/s)', 'PM10'].values[0] if len(wspm_summary) > 0 else 0
            
            st.write(f"""
            **Rata-rata PM10 per Kecepatan Angin:**
            - **Rendah (<=1.5 m/s):** {val_low:.2f} µg/m³
            - **Sedang (1.5-3.0 m/s):** {val_med:.2f} µg/m³
            - **Tinggi (>3.0 m/s):** {val_high:.2f} µg/m³
            """)

        # 2. Line Chart Pola Diurnal PM2.5
        with col2:
            hourly_pm25 = filtered_df.groupby('hour')['PM2.5'].mean().reset_index()
            peak_hour = hourly_pm25.loc[hourly_pm25['PM2.5'].idxmax()]
            min_hour = hourly_pm25.loc[hourly_pm25['PM2.5'].idxmin()]
            
            fig2, ax2 = plt.subplots(figsize=(6, 4))
            ax2.plot(hourly_pm25['hour'], hourly_pm25['PM2.5'], marker='o', color='crimson')
            ax2.set_xlabel("Jam (CST / UTC+8)")
            ax2.set_ylabel("Rata-rata PM2.5 (µg/m³)")
            ax2.set_xticks(range(0, 24, 2))
            ax2.set_ylim(bottom=0) # Sumbu Y WAJIB dimulai dari Nol
            
            fig2.tight_layout()
            st.pyplot(fig2)
            
            st.write(f"""
            **Pola Diurnal PM2.5:**
            - **Puncak Tertinggi:** Jam **{int(peak_hour['hour']):02d}:00 CST** ({peak_hour['PM2.5']:.2f} µg/m³)
            - **Titik Terendah:** Jam **{int(min_hour['hour']):02d}:00 CST** ({min_hour['PM2.5']:.2f} µg/m³)
            """)
