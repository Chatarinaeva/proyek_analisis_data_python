import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# 🔹 Konfigurasi tampilan Streamlit
st.set_page_config(page_title="Bike Sharing Dashboard", layout="wide")
sns.set_style("darkgrid")

# 🔹 **Judul Dashboard**
st.title("📊 Bike Sharing Dashboard: Analisis Penyewaan Sepeda")

# === Load dataset dengan caching untuk efisiensi ===
@st.cache_data
def load_bike_data():
    try:
        bike_data = pd.read_csv("main_data.csv")  # Pastikan file ada di folder "dashboard"
        bike_data["dteday"] = pd.to_datetime(bike_data["dteday"])  # Konversi dteday ke datetime
        return bike_data
    except FileNotFoundError:
        st.error("⚠️ File 'main_data.csv' tidak ditemukan. Pastikan sudah diekspor dengan benar.")
        return None

# 🔹 Memuat data
bike_df = load_bike_data()

if bike_df is not None:
    # 🔹 Sidebar untuk filter tanggal
    st.sidebar.header("📅 Filter Data")
    min_date = bike_df["dteday"].min()
    max_date = bike_df["dteday"].max()

    start_date, end_date = st.sidebar.date_input(
        label="Pilih Rentang Tanggal",
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

    # 🔹 Sidebar untuk filter musim
    season_mapping = {1: "Semi", 2: "Panas", 3: "Gugur", 4: "Dingin"}
    bike_df["season_text"] = bike_df["season"].map(season_mapping).astype(str)

    selected_seasons = st.sidebar.multiselect(
        label="Pilih Musim",
        options=list(season_mapping.values()),  
        default=list(season_mapping.values())  
    )

    # ✅ Konversi `start_date` dan `end_date` ke datetime sebelum filtering
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    # ✅ Filter Data Berdasarkan Sidebar
    filtered_df = bike_df[
        (bike_df["dteday"] >= start_date) & (bike_df["dteday"] <= end_date) &
        (bike_df["season_text"].isin(selected_seasons))
    ].copy()

    # ✅ Hitung ulang kategori demand setelah filtering
    filtered_df["demand_category"] = filtered_df["cnt"].apply(
        lambda cnt: "Low Demand" if cnt <= 300 else ("Medium Demand" if cnt <= 600 else "High Demand")
    )

    # ✅ Hitung ulang kategori musim setelah filtering
    season_avg = filtered_df.groupby("season")["cnt"].mean().sort_values()
    if len(season_avg) >= 3:
        low_season = season_avg.index[0]
        medium_season = season_avg.index[1]
        high_season = season_avg.index[2]

        def categorize_season(season):
            if season == low_season:
                return "Low Season"
            elif season == medium_season:
                return "Medium Season"
            else:
                return "High Season"

        filtered_df["season_category"] = filtered_df["season"].apply(categorize_season)

    # 🔹 **Tampilkan Statistik Sebelum dan Sesudah Filtering**
    st.subheader("📊 Statistik Data Sebelum dan Sesudah Filtering")
    col1, col2 = st.columns(2)
    with col1:
        st.write("📊 **Statistik Sebelum Filtering**")
        st.write(bike_df["cnt"].describe())

    with col2:
        st.write("📊 **Statistik Setelah Filtering**")
        st.write(filtered_df["cnt"].describe())

    # 🔹 **Tampilkan 5 Baris Data Setelah Filtering**
    st.subheader("📋 5 Baris Pertama Data yang Ditampilkan")
    st.dataframe(filtered_df.head())

    # 🔹 **1️⃣ Perbedaan Jumlah Penyewaan: Hari Kerja vs Akhir Pekan**
    st.subheader("🚴‍♂️ Jumlah Penyewaan Sepeda: Hari Kerja vs Akhir Pekan")

    if "workingday" in filtered_df.columns:
        day_type_df = filtered_df.groupby("workingday")["cnt"].sum().reset_index()
        day_type_df["workingday"] = day_type_df["workingday"].map({0: "Akhir Pekan", 1: "Hari Kerja"})

        fig, ax = plt.subplots(figsize=(9, 5))
        bars = sns.barplot(x="workingday", y="cnt", data=day_type_df, palette=["#B1D0F0", "#FFA07A"], ax=ax)
        ax.set_xlabel("Hari")
        ax.set_ylabel("Jumlah Penyewaan")
        ax.set_title("Jumlah Penyewaan Sepeda: Hari Kerja vs Akhir Pekan")
        #Tambahkan anotasi di atas batang
        for bar in bars.patches:
            ax.annotate(f"{bar.get_height():,.0f}", 
                        (bar.get_x() + bar.get_width() / 2, bar.get_height()), 
                        ha='center', va='bottom', fontsize=8, color='gray')
            
        st.pyplot(fig)

    # 🔹 **2️⃣ Jumlah Penyewaan Sepeda Berdasarkan Musim**
    st.subheader("🌦️ Jumlah Penyewaan Sepeda Berdasarkan Musim")

    if "season" in filtered_df.columns:
        season_df = filtered_df.groupby("season")["cnt"].sum().reset_index()
        season_df["season"] = season_df["season"].map(season_mapping)

        #Menentukan musim dengan jumlah penyewaan tertinggi
        max_season = season_df.loc[season_df["cnt"].idxmax(), "season"]

        #Menentukan warna: Soroti musim dengan penyewaan tertinggi (merah), lainnya abu-abu
        colors = ["#FF9999" if season != max_season else "#CC0000" for season in season_df["season"]]

        fig, ax = plt.subplots(figsize=(8, 5))
        bars = sns.barplot(x="season", y="cnt", data=season_df, palette=colors, ax=ax)

        ax.set_xlabel("Musim")
        ax.set_ylabel("Jumlah Penyewaan")
        ax.set_title("Jumlah Penyewaan Sepeda Berdasarkan Musim")

        #Tambahkan anotasi di atas batang
        for bar, season in zip(bars.patches, season_df["season"]):
            ax.annotate(f"{bar.get_height():,.0f}", 
                        (bar.get_x() + bar.get_width() / 2, bar.get_height()), 
                        ha='center', va='bottom', fontsize=8, 
                        color='black' if season == max_season else 'gray')

        st.pyplot(fig)


    # 🔹 **3️⃣ Pola Penyewaan Sepeda: Kasual vs Terdaftar**
    st.subheader("👥 Pola Penyewaan Sepeda: Kasual vs Terdaftar")

    if {"workingday", "casual", "registered"}.issubset(filtered_df.columns):
        casual_registered_df = filtered_df.groupby("workingday")[["casual", "registered"]].sum().reset_index()
        casual_registered_df["workingday"] = casual_registered_df["workingday"].map({0: "Akhir Pekan", 1: "Hari Kerja"})

        fig, ax = plt.subplots(figsize=(8, 5))
        casual_registered_df.set_index("workingday").plot(kind="bar", stacked=True, colormap="viridis", ax=ax)
        ax.set_xlabel("Hari")
        ax.set_ylabel("Jumlah Penyewaan")
        ax.set_title("Pola Penyewaan Sepeda Berdasarkan Hari Kerja vs Akhir Pekan")
        plt.legend(["Casual", "Registered"])
        st.pyplot(fig)

    # 🔹 **4️⃣ Distribusi Kategori Demand**
    st.subheader("📊 Distribusi Kategori Demand")
    demand_distribution = filtered_df["demand_category"].value_counts()

    fig, ax = plt.subplots(figsize=(6, 4))
    sns.barplot(x=demand_distribution.index, y=demand_distribution.values, palette="coolwarm", ax=ax)
    ax.set_xlabel("Kategori Demand")
    ax.set_ylabel("Jumlah Hari")
    ax.set_title("Distribusi Kategori Demand")
    st.pyplot(fig)

    # 🔹 **5️⃣ Distribusi Demand Berdasarkan Musim**
    if "season_category" in filtered_df.columns:
        season_demand = filtered_df.groupby("season_category")["demand_category"].value_counts().unstack()

        fig, ax = plt.subplots(figsize=(8, 5))
        season_demand.plot(kind="bar", stacked=True, colormap="magma", ax=ax)
        ax.set_xlabel("Kategori Musim")
        ax.set_ylabel("Jumlah Hari")
        ax.set_title("Permintaan Sepeda Berdasarkan Musim")
        plt.legend(title="Demand Category")
        st.pyplot(fig)

    # **Footer Dashboard**
    st.caption("📌 Bike Sharing Dashboard | Dataset by [Kaggle - Bike Sharing Dataset](https://www.kaggle.com/datasets/lakshmi25npathi/bike-sharing-dataset)")
