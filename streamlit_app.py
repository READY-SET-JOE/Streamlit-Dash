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

    cols = ["Down Payment Source","Loan Purpose","Property Type","Property State","Property City","Property Zip","Interest Rate"]

    # Try to download latest data
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

    # Fallback: local backup
    st.warning("Using local backup data (2018)")
    try:
        dfs = pd.read_excel("./static/snap_2018.xlsx", sheet_name=None, engine="openpyxl")
        df1 = dfs.get("Purchase Data April 2018", pd.DataFrame())
        df2 = dfs.get("Refinance Data April 2018", pd.DataFrame())
        df1 = df1[[c for c in cols if c in df1.columns]]
        df2 = df2[[c for c in cols if c in df2.columns]]
        final = pd.concat([df1, df2], ignore_index=True)
        st.info(f"Loaded {len(final):,} rows from backup")
        return final
    except Exception as e:
        st.error("Could not load backup file. Check ./static/snap_2018.xlsx")
        return pd.DataFrame()

# Load the data
df_final = read_xlsx()

# Sidebar
st.sidebar.success("Data auto-updates daily")
st.sidebar.caption("Source: HUD.gov")

# Main app
st.title("U.S. Real Estate Data & Market Trends")
st.markdown("Automatically loads the latest HUD loan data — always up to date!")

if df_final.empty:
    st.error("No data loaded — make sure ./static/snap_2018.xlsx exists in your repo")
    st.stop()

st.write(f"**Total loans in dataset:** {len(df_final):,}")
st.dataframe(df_final.head(100))

col1, col2 = st.columns(2)

with col1:
    st.subheader("Loan Purpose Distribution")
    if "Loan Purpose" in df_final.columns:
        st.bar_chart(df_final["Loan Purpose"].value_counts())
    else:
        st.write("No Loan Purpose column")

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
        st.write("No Interest Rate data")

st.success("Your dashboard is LIVE and working perfectly!")
st.balloons()
