# Air Quality Analytics Dashboard - Nongzhanguan ✨

## Deskripsi
Proyek ini merupakan analisis data kualitas udara di Stasiun Nongzhanguan periode 2013–2017. Analisis ini bertujuan untuk memahami tren bulanan konsentrasi polutan PM2.5 dan PM10 serta pola harian (diurnal) PM2.5.

## Link Dashboard Streamlit
Aplikasi interaktif dapat diakses melalui tautan berikut:  
👉 **[Air Quality Analytics Dashboard](https://vs899sp5cvk3odivzhsssu.streamlit.app/)**

## Setup Environment - Anaconda

```
conda create --name main-ds python=3.9
conda activate main-ds
pip install -r requirements.txt
```

## Setup Environment - Shell/Terminal

```
mkdir proyek_analisis_data
cd proyek_analisis_data
pipenv install
pipenv shell
pip install -r requirements.txt
```

## Run Streamlit App

```
streamlit run dashboard/dashboard.py
```

## Struktur Repositori

```
.
├── dashboard/
│   ├── dashboard.py
│   └── main_data.csv
├── PRSA_Data_Nongzhanguan_20130301-20170228.csv
├── Proyek_Analisis_Data_Nongzhanguan.ipynb
├── README.md
└── requirements.txt
```
