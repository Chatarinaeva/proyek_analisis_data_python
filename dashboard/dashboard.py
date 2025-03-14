import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

#Konfigurasi tampilan Streamlit
st.set_page_config(page_title="Bike Sharing Dashboard", layout="wide")
sns.set_style("darkgrid")

#Judul Dashboard
st.title("📊 Bike Sharing Dashboard: Analisis Penyewaan Sepeda")

# Load dataset
@st.cache_data
def load_bike_data():
    try:
        bike_data = pd.read_csv("dashboard/main_data.csv")
        bike_data["dteday"] = pd.to_datetime(bike_data["dteday"])
        return bike_data
    except FileNotFoundError:
        st.error("⚠️ File 'main_data.csv' tidak ditemukan. Pastikan sudah diekspor dengan benar.")
        return None

bike_df = load_bike_data()

if bike_df is not None:
    #Sidebar untuk filter tanggal dan musim
    st.sidebar.header("📅 Filter Data")
    min_date = bike_df["dteday"].min()
    max_date = bike_df["dteday"].max()

    start_date, end_date = st.sidebar.date_input(
        label="Pilih Rentang Tanggal",
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

    selected_seasons = st.sidebar.multiselect(
        label="Pilih Musim",
        options=bike_df["season_label"].unique().tolist(),  
        default=bike_df["season_label"].unique().tolist()
    )

    # Konversi start_date dan end_date ke datetime sebelum filtering
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    # Filter Data
    filtered_df = bike_df[
        (bike_df["dteday"] >= start_date) & (bike_df["dteday"] <= end_date) &
        (bike_df["season_label"].isin(selected_seasons))
    ].copy()

    # 1️⃣ Perbedaan Jumlah Penyewaan: Hari Kerja vs Akhir Pekan
    st.subheader("🚴‍♂️ Jumlah Penyewaan Sepeda: Hari Kerja vs Akhir Pekan")
    day_type_df = filtered_df.groupby("workingday")["cnt"].sum().reset_index()
    day_type_df["workingday"] = day_type_df["workingday"].map({0: "Akhir Pekan", 1: "Hari Kerja"})

    fig, ax = plt.subplots(figsize=(9, 5))
    sns.barplot(x="workingday", y="cnt", data=day_type_df, ax=ax)
    ax.set_xlabel("Kategori Hari")
    ax.set_ylabel("Total Penyewaan Sepeda")
    ax.set_title("Jumlah Penyewaan Sepeda: Hari Kerja vs Akhir Pekan")
    st.pyplot(fig)

    # Pie Chart: Proporsi Penyewaan Sepeda Hari Kerja vs Akhir Pekan
    st.subheader("📊 Proporsi Penyewaan Sepeda: Hari Kerja vs Akhir Pekan")

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(
        day_type_df["cnt"],
        labels=day_type_df["workingday"],
        autopct="%1.1f%%",
        colors=["#72BCD4", "#FFA07A"],
        startangle=140
    )
    ax.set_title("Proporsi Penyewaan Sepeda: Hari Kerja vs Akhir Pekan")
    st.pyplot(fig)


    # 2️⃣ Jumlah Penyewaan Berdasarkan Musim
    st.subheader("🌦️ Jumlah Penyewaan Sepeda Berdasarkan Musim (Season)")

    # Mengelompokkan data berdasarkan musim dan menghitung total penyewaan
    season_df = filtered_df.groupby("season_label", observed=False)["cnt"].sum().reset_index()

    # Menentukan urutan musim yang benar 
    season_order = ["Winter", "Spring", "Summer", "Fall"]
    season_df["season_label"] = pd.Categorical(season_df["season_label"], categories=season_order, ordered=True)
    season_df = season_df.sort_values("season_label")

    # Penentuan warna
    highlight_color = "#D62728"  
    base_color = "#FFA07A"  

    max_season = season_df.loc[season_df["cnt"].idxmax(), "season_label"]
    colors = [highlight_color if season == max_season else base_color for season in season_df["season_label"]]

    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(
        data=season_df,
        x="season_label",
        y="cnt",
        palette=colors,
        ax=ax
    )

    ax.set_xlabel("Season", fontsize=12)
    ax.set_ylabel("Jumlah Penyewaan", fontsize=12)
    ax.set_title("Jumlah Penyewaan Sepeda Berdasarkan Musim (Season)", fontsize=16)

    st.pyplot(fig)


    # 3️⃣ Pola Penyewaan Sepeda: Kasual vs Terdaftar
    st.subheader("👥 Pola Penyewaan Sepeda: Kasual vs Terdaftar Berdasarkan Hari Kerja vs Akhir Pekan")

    # Kelompokkan data berdasarkan hari kerja vs akhir pekan
    casual_registered_df = filtered_df.groupby("workingday", observed=True)[["casual", "registered"]].sum().reset_index()

    # Ganti angka workingday dengan label yang lebih jelas
    casual_registered_df["workingday"] = casual_registered_df["workingday"].map({0: "Akhir Pekan", 1: "Hari Kerja"})

    # Plot stacked bar chart
    fig, ax = plt.subplots(figsize=(8, 5))
    casual_registered_df.set_index("workingday").plot(kind="bar", stacked=True, colormap="viridis", ax=ax)

    ax.set_xlabel("Kategori Hari")
    ax.set_ylabel("Jumlah Penyewaan")
    ax.set_title("Pola Penyewaan Sepeda Berdasarkan Hari Kerja vs Akhir Pekan")


    plt.legend(["Casual", "Registered"])
    plt.xticks(rotation=0)

    st.pyplot(fig)


    #Analisis lanjutan
    st.subheader("🔍 Analisis Clustering: Pola Penggunaan Sepeda Berdasarkan Kategori Permintaan dan Musim")
    # 4️⃣ Clustering: Distribusi Kategori Demand
    st.subheader("📊 Distribusi Kategori Demand")

    # Mengubah demand_distribution menjadi DataFrame agar kompatibel dengan Seaborn
    demand_distribution_df = filtered_df["demand_category"].value_counts().reset_index()
    demand_distribution_df.columns = ["demand_category", "count"]  # Ubah nama kolom agar sesuai

    fig, ax = plt.subplots(figsize=(6, 4))
    sns.barplot(
        data=demand_distribution_df,
        x="demand_category",
        y="count",
        hue="demand_category",
        legend=False,
        palette={"Low Demand": "#72BCD4", "Medium Demand": "#FFA07A", "High Demand": "#D72638"},
        ax=ax
    )

    ax.set_title("Distribusi Kategori Demand")
    ax.set_xlabel("Kategori Demand")
    ax.set_ylabel("Jumlah Jam")

    st.pyplot(fig)

    # 5️⃣ Clustering: Distribusi Kategori Musim
    st.subheader("🌦️ Distribusi Kategori Musim")

    # Mengubah season_distribution menjadi DataFrame agar kompatibel dengan Seaborn
    season_distribution_df = filtered_df["season_category"].value_counts().reset_index()
    season_distribution_df.columns = ["season_category", "count"]  # Ubah nama kolom agar sesuai

    fig, ax = plt.subplots(figsize=(6, 4))
    sns.barplot(
        data=season_distribution_df,
        x="season_category",
        y="count",
        hue="season_category",
        legend=False,
        palette={"Low Season": "#3A7D44", "Medium Season": "#EFCB68", "High Season": "#D72638"},
        ax=ax
    )

    ax.set_title("Distribusi Kategori Musim")
    ax.set_xlabel("Kategori Musim")
    ax.set_ylabel("Jumlah Jam")

    st.pyplot(fig)


    # 6️⃣ Permintaan Sepeda Berdasarkan Musim
    st.subheader("🔍 Permintaan Sepeda Berdasarkan Musim")

    # Pastikan 'season_category' dan 'demand_category' ada di data sebelum visualisasi
    if "season_category" in filtered_df.columns and "demand_category" in filtered_df.columns:
        season_demand = filtered_df.groupby("season_category")["demand_category"].value_counts().unstack()

        fig, ax = plt.subplots(figsize=(8, 5))
        season_demand.plot(kind="bar", stacked=True, colormap="viridis", ax=ax)

        ax.set_title("Permintaan Sepeda Berdasarkan Musim")
        ax.set_xlabel("Kategori Musim")
        ax.set_ylabel("Jumlah Jam")
        ax.legend(title="Demand Category")
        ax.set_xticklabels(ax.get_xticklabels(), rotation=0)

        st.pyplot(fig)


    #Footer Dashboard
    st.caption("📌 Bike Sharing Dashboard | Dataset by [Kaggle - Bike Sharing Dataset](https://www.kaggle.com/datasets/lakshmi25npathi/bike-sharing-dataset)")
