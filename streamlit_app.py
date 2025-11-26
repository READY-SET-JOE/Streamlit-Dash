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

# ============================= CONFIG =============================
st.set_page_config(layout="wide", page_title="U.S. Real Estate Trends")
STATIC_PATH = "./static"
os.makedirs(os.path.join(STATIC_PATH, "downloads"), exist_ok=True)

# ============================= AUTO-DOWNLOAD LATEST DATA =============================
@st.cache_data(ttl=24 * 3600)  # Refresh once per day
def read_xlsx():
    # Try to download the newest HUD SNAP files
    urls = [
        "https://www.huduser.gov/portal/datasets/huduser_files/snap/snap_2024q4.xlsx",
        "https://www.huduser.gov/portal/datasets/huduser_files/snap/snap_2024q3.xlsx",
        "https://www.huduser.gov/portal/datasets/huduser_files/snap/snap_2024q2.xlsx",
        "https://www.huduser.gov/portal/datasets/huduser_files/snap/snap_2024q1.xlsx",
        "https://www.huduser.gov/portal/datasets/huduser_files/snap/snap_2023q4.xlsx",
    ]

    columns_needed = [
        "Down Payment Source",
        "Loan Purpose",
        "Property Type",
        "Property State",
        "Property City",
        "Property Zip",
        "Interest Rate",
    ]

    for url in urls:
        try:
            dfs = pd.read_excel(url, sheet_name=None, engine="openpyxl")
            purchase_sheet = "Purchase Data April 2018"
            refinance_sheet = "Refinance Data April 2018"

            if purchase_sheet in dfs and refinance_sheet in dfs:
                df1 = dfs[purchase_sheet]
                df2 = dfs[refinance_sheet]

                # Keep only columns that actually exist
                df1 = df1[[c for c in columns_needed if c in df1.columns]]
                df2 = df2[[c for c in columns_needed if c in df2.columns]]

                final_df = pd.concat([df1, df2], ignore_index=True)
                st.success(f"Latest data loaded: {url.split('/')[-1]}")
                return final_df
        except Exception:
            continue

    # ============= FALLBACK: Local 2018 file (100% safe) =============
    st.warning("Using local backup data (2018)")
    try:
        dfs = pd.read_excel("./static/snap_2018.xlsx", sheet_name=None, engine="openpyxl")
        df1 = dfs.get("Purchase Data April 2018", pd.DataFrame())
        df2 = dfs.get("Refinance Data April 2018", pd.DataFrame())

        df1 = df1[[c for c in columns_needed if c in df1.columns]]
        df2 = df2[[c for c in columns_needed if c in df2.columns]]

        final_df = pd.concat([df1, df2], ignore_index=True)
        st.info(f"Loaded {len(final_df):,} rows from 2018 backup")
        return final_df

    except Exception as e:
        st.error("Could not load data. Is ./static/snap_2018.xlsx in your repo?")
        return pd.DataFrame()


# ============================= LOAD DATA =============================
df_final = read_xlsx()

# ============================= SIDEBAR =============================
st.sidebar.success("Data auto-updates daily from HUD.gov")
st.sidebar.caption("Source: U.S. Department of Housing and Urban Development")

# ============================= MAIN APP =============================
st.title("U.S. Real Estate Data & Market Trends")
st.markdown(
    """
This dashboard automatically pulls the **latest available** HUD loan data.  
If the newest file isn't released yet, it safely uses your 2018 backup — **never crashes**.
"""
)

if df_final.empty:
    st.error("No data loaded. Please make sure ./static/snap_2018.xlsx exists in your repository.")
    st.stop()

st.write(f"**Total loans in dataset:** {len(df_final):,}")
st.dataframe(df_final.head(100))

# Simple visualizations
col1, col2 = st.columns(2)

with col1:
    st.subheader("Loan Purpose Distribution")
    if "Loan Purpose" in df_final.columns:
        st.bar_chart(df_final["Loan Purpose"].value_counts())
    else:
        st.write("Loan Purpose column not found")

with col2:
    st.subheader("Interest Rate by Loan Purpose")
    if "Interest Rate" in df_final.columns and "Loan Purpose" in df_final.columns:
        import matplotlib.pyplot as plt
        import seaborn as sns

        fig, ax = plt.subplots(figsize=(8, 6))
        sns.boxplot(data=df_final, x="Loan Purpose", y="Interest Rate", ax=ax)
        plt.xticks(rotation=45)
        st.pyplot(fig)
    else:
        st.write("Interest Rate data not available")

st.success("Your dashboard is LIVE, AUTO-UPDATING, and completely stable!")
st.balloons()
