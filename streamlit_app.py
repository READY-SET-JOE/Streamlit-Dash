import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="Georgia 50% ARV Deal Finder", layout="wide")
st.title("Your Private Georgia 50% ARV Deal Finder")
st.markdown("Upload any PropStream, foreclosure, probate, or tax CSV → instantly see only the deals ≤60% of ARV")

uploaded_file = st.file_uploader("Drop your CSV here", type=["csv"])

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)

        # Auto-detect price and ARV columns
        price_col = None
        arv_col = None

        for col in df.columns:
            c = col.lower()
            if price_col is None and ("price" in c or "ask" in c or "list" in c or "offer" in c):
                price_col = col
            if arv_col is None and ("arv" in c or "repair" in c or "value" in c or "after" in c):
                arv_col = col

        # Manual selection if auto-detect misses
        price_col = st.selectbox("Price / Asking column", df.columns, index=df.columns.get_loc(price_col) if price_col else 0)
        arv_col = st.selectbox("ARV column", df.columns, index=df.columns.get_loc(arv_col) if arv_col else 0)

        # Clean and convert to numbers
        df[price_col] = df[price_col].astype(str).str.replace(r"[$,]", "", regex=True)
        df[arv] = df[arv].astype(str).str.replace(r"[$,]", "", regex=True)

        df[price_col] = pd.to_numeric(df[price_col], errors='coerce')
        df[arv] = pd.to_numeric(df[arv], errors='coerce')

        # Calculate % of ARV
        df["% of ARV"] = (df[price_col] / df[arv]) * 100
        df["% of ARV"] = df["% of ARV"].round(1)

        # Show only the deep-discount deals
        deals = df[df["% of ARV"] <= 60].sort_values("% of ARV").copy()

        st.write("---")
        st.subheader(f"Found {len(deals)} deals ≤60% of ARV")
        
        if len(deals) > 0:
            st.dataframe(deals, use_container_width=True, height=700)
            csv = deals.to_csv(index=False).encode()
            st.download_button("Download These Deals", csv, "georgia_50percent_deals.csv", "text/csv")
        else:
            st.info("No deals ≤60% ARV in this file yet — try a fresh PropStream export!")

    except Exception as e:
        st.error(f"Error: {e}")

else:
    st.info("Upload your first CSV to start finding 50% ARV deals today!")
    st.balloons()
