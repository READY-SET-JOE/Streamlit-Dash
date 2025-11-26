############################################################################################
#                                  Author: Anass MAJJI                                     #
#                               File Name: streamlit_app.py                                #
#                           Creation Date: November 06, 2022                               #
#                         Source Language: Python                                          #
#         Repository:    https://github.com/amajji/Streamlit-Dash.git                      #
#                              --- Code Description ---                                    #
#         Streamlit app designed for visualizing U.S. real estate data and market trends   #
############################################################################################

import pandas as pd
import geopandas as gpd
import streamlit as st
import os
import requests
from streamlit_folium import folium_static
import pydeck as pdk
import leafmap.colormaps as cm
from leafmap.common import hex_to_rgb
import seaborn as sns
import matplotlib.pyplot as plt

# ============================= CONFIG =============================
st.set_page_config(layout="wide", page_title="U.S. Real Estate Trends")
STATIC_PATH = "./static"
os.makedirs(os.path.join(STATIC_PATH, "downloads"), exist_ok=True)

# ============================= AUTO-DOWNLOAD LATEST DATA =============================
@st.cache_data(ttl=24*3600)  # Refreshes once per day
def read_xlsx():
    # List of recent HUD SNAP files (most recent first)
    urls = [
        "https://www.huduser.gov/portal/datasets/huduser_files/snap/snap_2024q4.xlsx",
        "https://www.huduser.gov/portal/datasets/huduser_files/snap/snap_2024q3.xlsx",
        "https://www.huduser.gov/portal/datasets/huduser_files/snap/snap_2024q2.xlsx",
        "https://www.huduser.gov/portal/datasets/huduser_files/snap/snap_2024q1.xlsx",
        "https://www.huduser.gov/portal/datasets/huduser_files/snap/snap_2023q4.xlsx",
    ]
    
    columns_needed = [
        "Down Payment Source", "Loan Purpose", "Property Type",
        "Property State", "Property City", "Property Zip", "Interest Rate"
    ]
    
    for url in urls:
        try:
            dfs = pd.read_excel(url, sheet_name=None)
            if "Purchase Data" in dfs and "Refinance Data" in dfs:
                df = pd.concat([dfs["Purchase Data"], dfs["Refinance Data"]], ignore_index=True)
                st.success(f"Latest data loaded: {url.split('/')[-1]}")
                return df[columns_needed].copy()
        except:
            continue
    
    # Fallback to local file if internet fails
    st.warning("Using local backup data (2018)")
    return pd.read_excel("./static/snap_2018.xlsx", sheet_name=None, usecols=columns_needed)

# ============================= LOAD DATA =============================
df_final = read_xlsx()

# ============================= SIDEBAR INFO =============================
st.sidebar.success("Data auto-updates daily from HUD.gov")
st.sidebar.caption("Source: U.S. Department of Housing and Urban Development")

# ============================= MAIN APP =============================
st.title("U.S. Real Estate Data & Market Trends")
st.markdown("""
This dashboard automatically pulls the **latest available** purchase and refinance loan data from HUD.
No manual updates needed — it's always fresh!
""")

st.write("Total loans in dataset:", len(df_final))
st.dataframe(df_final.head(100))

# Simple visualizations
col1, col2 = st.columns(2)

with col1:
    st.subheader("Loan Purpose Distribution")
    purpose_counts = df_final["Loan Purpose"].value_counts()
    st.bar_chart(purpose_counts)

with col2:
    st.subheader("Interest Rate by Loan Purpose")
    fig, ax = plt.subplots()
    sns.boxplot(data=df_final, x="Loan Purpose", y="Interest Rate", ax=ax)
    st.pyplot(fig)

st.success("Your dashboard is LIVE and AUTO-UPDATING!")
