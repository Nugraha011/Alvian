app_code = """import streamlit as st
import pandas as pd
import plotly.express as px

# Set page configuration
st.set_page_config(
    page_title="Asia Fuel Prices Dashboard",
    page_icon="⛽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv('asia_fuel_prices_detailed.csv')
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Gagal memuat data: {e}. Pastikan file 'asia_fuel_prices_detailed.csv' berada di folder yang sama.")
    st.stop()

# Sidebar title & filters
st.sidebar.header("⚙️ Filter Pencarian")

# Filter sub-region
sub_regions = ['Semua'] + list(df['sub_region'].unique())
selected_sub_region = st.sidebar.selectbox("Pilih Sub-Region:", sub_regions)

# Filter subsidy status
subsidy_options = ['Semua', 'Aktif (True)', 'Tidak Aktif (False)']
selected_subsidy = st.sidebar.selectbox("Status Subsidi Bahan Bakar:", subsidy_options)

# Apply filters
filtered_df = df.copy()
if selected_sub_region != 'Semua':
    filtered_df = filtered_df[filtered_df['sub_region'] == selected_sub_region]

if selected_subsidy == 'Aktif (True)':
    filtered_df = filtered_df[filtered_df['fuel_subsidy_active'] == True]
elif selected_subsidy == 'Tidak Aktif (False)':
    filtered_df = filtered_df[filtered_df['fuel_subsidy_active'] == False]

# Main Dashboard Title
st.title("⛽ Analisis Harga Bahan Bakar di Asia")
st.markdown("Dashboard interaktif untuk mengeksplorasi harga bensin, diesel, LPG, tingkat keterjangkauan, dan adopsi EV di berbagai negara Asia.")

# Key Metrics Row
st.subheader("📊 Metrik Utama (Berdasarkan Filter)")
col1, col2, col3, col4 = st.columns(4)

if not filtered_df.empty:
    max_gas = filtered_df.loc[filtered_df['gasoline_usd_per_liter'].idxmax()]
    min_gas = filtered_df.loc[filtered_df['gasoline_usd_per_liter'].idxmin()]
    avg_income = filtered_df['avg_monthly_income_usd'].mean()
    active_sub_count = filtered_df['fuel_subsidy_active'].sum()
    
    col1.metric("Harga Bensin Tertinggi", f"${max_gas['gasoline_usd_per_liter']:.2f}/L", max_gas['country'])
    col2.metric("Harga Bensin Terendah", f"${min_gas['gasoline_usd_per_liter']:.2f}/L", min_gas['country'])
    col3.metric("Rata-rata Pendapatan", f"${avg_income:.2f}/bulan")
    col4.metric("Negara Subsidi Aktif", f"{active_sub_count} dari {len(filtered_df)}")
else:
    st.warning("Tidak ada data yang cocok dengan filter saat ini.")

st.markdown("---")

# Tabs for layout
tab1, tab2, tab3 = st.tabs(["📈 Visualisasi & Analisis", "🔍 Tabel Data", "ℹ️ Tentang Data"])

with tab1:
    if not filtered_df.empty:
        c1, c2 = st.columns(2)
        
        with c1:
            st.write("### 💵 Perbandingan Harga Bahan Bakar")
            price_type = st.radio("Pilih Jenis Bahan Bakar:", ["Bensin (Gasoline)", "Diesel", "LPG"])
            
            if price_type == "Bensin (Gasoline)":
                y_col = "gasoline_usd_per_liter"
                title = "Harga Bensin (USD per Liter)"
            elif price_type == "Diesel":
                y_col = "diesel_usd_per_liter"
                title = "Harga Diesel (USD per Liter)"
            else:
                y_col = "lpg_usd_per_kg"
                title = "Harga LPG (USD per Kg)"
                
            sorted_df = filtered_df.sort_values(by=y_col, ascending=False)
            fig_bar = px.bar(sorted_df, x='country', y=y_col, color='sub_region',
                             title=title, labels={y_col: 'Harga (USD)', 'country': 'Negara'},
                             text_auto='.2f')
            st.plotly_chart(fig_bar, use_container_width=True)
            
        with c2:
            st.write("### 📈 Hubungan Keterjangkauan & Pendapatan")
            fig_scatter = px.scatter(filtered_df, x='avg_monthly_income_usd', y='fuel_affordability_index',
                                     size='gasoline_usd_per_liter', color='sub_region', hover_name='country',
                                     title='Pendapatan Bulanan vs Indeks Keterjangkauan',
                                     labels={'avg_monthly_income_usd': 'Pendapatan Bulanan (USD)', 'fuel_affordability_index': 'Indeks Keterjangkauan (Makin Tinggi Makin Terjangkau)'})
            st.plotly_chart(fig_scatter, use_container_width=True)
            
        st.markdown("---")
        
        c3, c4 = st.columns(2)
        with c3:
            st.write("### 🔌 Adopsi EV vs Ketergantungan Impor Minyak")
            fig_ev = px.scatter(filtered_df, x='oil_import_dependency_pct', y='ev_adoption_pct',
                                size='refinery_capacity_kbpd', color='country',
                                title='Adopsi EV (%) vs Ketergantungan Impor Minyak (%)',
                                labels={'oil_import_dependency_pct': 'Ketergantungan Impor Minyak (%)', 'ev_adoption_pct': 'Adopsi EV (%)'})
            st.plotly_chart(fig_ev, use_container_width=True)
            
        with c4:
            st.write("### ⚖️ Beban Harga Bensin terhadap Upah Harian")
            sorted_wage_df = filtered_df.sort_values(by='gasoline_pct_daily_wage', ascending=False)
            fig_wage = px.bar(sorted_wage_df, x='country', y='gasoline_pct_daily_wage', color='fuel_subsidy_active',
                              title='Harga Bensin (% dari Upah Harian)',
                              labels={'gasoline_pct_daily_wage': '% dari Upah Harian', 'country': 'Negara', 'fuel_subsidy_active': 'Subsidi Aktif'})
            st.plotly_chart(fig_wage, use_container_width=True)
            
with tab2:
    st.write("### 📋 Dataset Lengkap")
    st.dataframe(filtered_df, use_container_width=True)
    
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Unduh Data Terfilter sebagai CSV",
        data=csv,
        file_name='asia_fuel_prices_filtered.csv',
        mime='text/csv',
    )

with tab3:
    st.write("### ℹ️ Keterangan Kolom Data")
    st.markdown('''
    - **country**: Nama Negara.
    - **sub_region**: Sub-wilayah di Asia (misal: South Asia, East Asia, Southeast Asia).
    - **iso3**: Kode 3-huruf negara.
    - **gasoline_usd_per_liter**: Harga bensin dalam USD per liter.
    - **diesel_usd_per_liter**: Harga diesel dalam USD per liter.
    - **lpg_usd_per_kg**: Harga LPG dalam USD per kilogram.
    - **avg_monthly_income_usd**: Pendapatan bulanan rata-rata penduduk dalam USD.
    - **fuel_affordability_index**: Indeks Keterjangkauan Bahan Bakar (makin tinggi berarti makin terjangkau).
    - **oil_import_dependency_pct**: Persentase ketergantungan impor minyak.
    - **refinery_capacity_kbpd**: Kapasitas kilang minyak dalam ribuan barel per hari (kbpd).
    - **ev_adoption_pct**: Persentase tingkat adopsi kendaraan listrik (EV).
    - **fuel_subsidy_active**: Status apakah negara memberikan subsidi bahan bakar aktif (True/False).
    - **subsidy_cost_bn_usd**: Biaya subsidi dalam miliar USD.
    - **co2_transport_mt**: Emisi CO2 dari sektor transportasi dalam juta ton (MT).
    - **price_date**: Tanggal pengambilan data harga.
    - **gasoline_pct_daily_wage**: Persentase harga bensin terhadap upah harian rata-rata.
    ''')
"""

requirements_code = """streamlit
pandas
plotly
"""

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(app_code)

with open('requirements.txt', 'w', encoding='utf-8') as f:
    f.write(requirements_code)

print("Files created successfully.")