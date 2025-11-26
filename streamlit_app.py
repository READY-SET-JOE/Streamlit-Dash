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
import streamlit as st
import os
import requests

# ============================= CONFIG =============================
st.set_page_config(layout="wide", page_title="U.S. Real Estate Trends")
STATIC_PATH = "./static"
os.makedirs(os.path.join(STATIC_PATH, "downloads"), exist_ok=True)

# ============================= AUTO-DOWNLOAD LATEST DATA =============================
@st.cache_data(ttl=24*3600)  # Refreshes once per day
def read_xlsx():
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

    # Try downloading latest data from HUD
    for url in urls:
        try:
            dfs = pd.read_excel(url, sheet_name=None, engine="openpyxl")
            purchase_sheet = "Purchase Data April 2018"
            refinance_sheet = "Refinance Data April 2018"

            if purchase_sheet in dfs and refinance_sheet in dfs:
                df1 = dfs[purchase_sheet]
                df2 = dfs[refinance_sheet]

                # Safely select only columns that exist
                df1 = df1[[c for c in columns_needed if c in df1.columns]]
                df2 = df2[[c for c in columns_needed if c in df2.columns]]

                final_df = pd.concat([df1, df2], ignore_index=True)
                st.success(f"Latest data loaded: {url.split('/')[-1]}")
                return final_df
        except Exception as e:
            continue  # Try next URL

    # Fallback: Use local 2018 file
    st.warning("Using local backup data (2018)")
    try:
        dfs = pd.read_excel("./static/snap_2018.xlsx", sheet_name=None, engine="openpyxl")
        df1 = dfs.get("Purchase
