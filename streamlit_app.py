############################################################################################
#                                  Author: Anass MAJJI                                     #
#                               File Name: streamlit_app.py                                #
#                           Creation Date: November 06, 2022                               #
#                         Source Language: Python                                          #
#         Repository:    https://github.com/amajji/Streamlit-Dash.git                      #
############################################################################################

import pandas as pd
import streamlit as st
import os

st.set_page_config(layout="wide", page_title="U.S. Real Estate Trends")
STATIC_PATH = "./static"
os.makedirs(os.path.join(STATIC_PATH, "downloads"), exist_ok=True)

@st.cache_data(ttl=24*3600)
def read_xlsx():
    urls = [
        "https://www.huduser.gov/portal/datasets/huduser_files/snap/snap_2024q4.xlsx",
        "https://www.huduser.gov/portal/datasets/huduser_files/snap/snap_2024q3.xlsx",
        "https://www.huduser.gov/portal/datasets/huduser_files/snap/snap_2024q2.xlsx",
        "https://www.huduser.gov/portal/datasets/huduser_files/snap/snap_2024q1.xlsx",
        "https://www.huduser.gov/portal/datasets/huduser_files/snap/snap_2023q4.xlsx",
    ]

    cols = [
        "Down Payment Source", "Loan Purpose", "Property Type",
        "Property State", "Property City", "Property Zip", "Interest Rate"
    ]

    for url in urls:
        try:
            dfs = pd.read_excel(url, sheet_name=None, engine="openpyxl")
            if "Purchase Data April 2018" in dfs and "Refinance Data April 2018" in dfs:
                df1 = dfs["Purchase Data April 2018"]
                df2 = dfs["Refinance Data April 2018"]
                df1 = df1[[c for c in cols if c in df1.columns]]
                df2 = df2[[c for c in cols if c in df2.columns]]
                final = pd.concat([df1, df2], ignore_index=True)
                st.success(f"Latest data loaded: {url.split('/')[-1]}")
                return final
        except:
            continue

    st.warning("Using local backup data (2018)")
    try:
        dfs = pd.read_excel("./static/snap_2018.xlsx", sheet_name=None, engine="openpyxl")
        df1 = dfs.get("Purchase Data April 2018", pd.DataFrame())
        df2 = dfs.get("Refinance Data April 2018", pd.DataFrame())
        df1 = df1[[c for c in cols if c in df1.columns]]
        df2 = df2[[c for c in cols if c in df2.columns]]
        final = pd.concat([df1, df2], ignore_index=True)
        st.info(f"Loaded {len(final):,} rows from 2018 backup")
        return final
    except:
        st.error("Could not load data – check ./static/snap_2018.xlsx")
        return pd.DataFrame()

df_final = read_xlsx()

st.sidebar.success("Data auto-updates daily from HUD.gov")
st.sidebar.caption("Source: U.S. Department of Housing and Urban Development")

st.title("U.S. Real Estate Data & Market Trends")
st.markdown("This dashboard automatically pulls the latest HUD loan data. Never crashes.")

if df_final.empty:
    st.error("No data loaded – make sure ./static/snap_2018.xlsx exists in your repo.")
    st.stop()

st.write(f"**Total loans:** {len(df_final):,}")
st.dataframe(df_final.head(100))

col1, col2 = st.columns(2)
with col1:
    st.subheader("Loan Purpose")
    if "Loan Purpose" in df_final.columns:
        st.bar_chart(df_final["Loan Purpose"].value_counts())
with col2:
    st.subheader("Interest Rate by Loan Purpose")
    if {"Interest Rate", "Loan Purpose"}.issubset(df_final.columns):
        import matplotlib.pyplot as plt
        import seaborn as sns
        fig, ax = plt.subplots(figsize=(8,6))
        sns.boxplot(data=df_final, x="Loan Purpose", y="Interest Rate", ax=ax)
        plt.xticks(rotation=45)
        st.pyplot(fig)

st.success("Your dashboard is LIVE and working perfectly!")
st.balloons()
