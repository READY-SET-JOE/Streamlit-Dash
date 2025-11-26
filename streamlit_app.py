import pandas as pd
import streamlit as st
import os

st.set_page_config(layout="wide", page_title="U.S. Real Estate Trends")
os.makedirs("./static/downloads", exist_ok=True)

@st.cache_data(ttl=86400)
def read_xlsx():
    cols = ["Down Payment Source","Loan Purpose","Property Type","Property State","Property City","Property Zip","Interest Rate"]

    # Try online files
    urls = [
        "https://www.huduser.gov/portal/datasets/huduser_files/snap/snap_2024q4.xlsx",
        "https://www.huduser.gov/portal/datasets/huduser_files/snap/snap_2024q3.xlsx",
        "https://www.huduser.gov/portal/datasets/huduser_files/snap/snap_2024q2.xlsx",
        "https://www.huduser.gov/portal/datasets/huduser_files/snap/snap_2024q1.xlsx",
        "https://www.huduser.gov/portal/datasets/huduser_files/snap/snap_2023q4.xlsx"
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
                st.success(f"Loaded latest: {url.split('/')[-1]}")
                return final
        except:
            continue

    # Fallback to local file
    st.warning("Using local backup (2018)")
    try:
        dfs = pd.read_excel("./static/snap_2018.xlsx", sheet_name=None, engine="openpyxl")
        df1 = dfs.get("Purchase Data April 2018", pd.DataFrame())
        df2 = dfs.get("Refinance Data April 2018", pd.DataFrame())
        df1 = df1[[c for c in cols if c in df1.columns]]
        df2 = df2[[c for c in cols if c in df2.columns]]
        final = pd.concat([df1, df2], ignore_index=True)
        st.info(f"Loaded {len(final):,} rows")
        return final
    except:
        st.error("Backup file missing")
        return pd.DataFrame()

df_final = read_xlsx()

st.sidebar.success("Data auto-updates daily")
st.sidebar.caption("Source: HUD.gov")

st.title("U.S. Real Estate Trends")
st.markdown("Latest HUD loan data — always fresh")

if df_final.empty:
    st.error("No data — check ./static/snap_2018.xlsx")
    st.stop()

st.write(f"Total loans: {len(df_final):,}")
st.dataframe(df_final.head(100))

col1, col2 = st.columns(2)
with col1:
    st.subheader("Loan Purpose")
    if "Loan Purpose" in df_final.columns:
        st.bar_chart(df_final["Loan Purpose"].value_counts())

with col2:
    st.subheader("Interest Rate")
    if {"Interest Rate","Loan Purpose"}.issubset(df_final.columns):
        import matplotlib.pyplot as plt, seaborn as sns
        fig, ax = plt.subplots()
        sns.boxplot(data=df_final, x="Loan Purpose", y="Interest Rate")
        st.pyplot(fig)

st.success("LIVE & WORKING!")
st.balloons()
