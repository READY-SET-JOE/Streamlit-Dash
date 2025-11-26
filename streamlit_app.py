import streamlit as st
import pandas as pd

st.set_page_config(page_title="Georgia 50% ARV Deal Finder", layout="wide")
st.title("Your Private 50% ARV Deal Finder")
st.markdown("**Upload your PropStream, foreclosure, probate, or tax CSV → See only the 40–60% ARV deals instantly.**")

# File uploader
uploaded_file = st.file_uploader("Drop your leads CSV here (PropStream, county list, etc.)", type=["csv"])

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        st.success(f"Loaded {len(df):,} leads")

        # Required columns - adjust these if your CSV uses different names
        price_col = None
        arv_col = None

        # Auto-detect common column names
        for col in df.columns:
            lower = col.lower()
            if "price" in lower or "ask" in lower or "list" in lower:
                price_col = col
            if "arv" in lower or "repair" in lower or "value" in lower:
                arv_col = col

        # Let user pick if auto-detect fails
        if not price_col:
            price_col = st.selectbox("Select column with Asking/Offer Price", df.columns)
        if not arv_col:
            arv_col = st.selectbox("Select column with After Repair Value (ARV)", df.columns)

        # Convert to numbers
        df[price_col] = pd.to_numeric(df[price_col].replace('[\$,]', '', regex=True), errors='coerce')
        df[arv_col] = pd.to_numeric(df[arv_col].replace('[\$,]', '', regex=True), errors='coerce')

        # Calculate discount
        df['% of ARV'] = (df[price_col] / df[arv_col]) * 100
        df['% of ARV'] = df['% of ARV'].round(1)

        # Show only the money deals
        deals = df[df['% of ARV'] <= 60].copy()
        deals = deals.sort_values('% of ARV')

        st.subheader(f"Found {len(deals)} Screaming Deals ≤60% of ARV")
        if len(deals) > 0:
            st.dataframe(deals, use_container_width=True, height=600)
            st.download_button("Download These Deals", deals.to_csv(index=False), "50percent_arv_deals.csv")
        else:
            st.info("No deals under 60% ARV yet — keep uploading fresh lists!")

    except Exception as e:
        st.error(f"Error: {e}")
else:
    st.info("Upload a CSV to start finding 50% ARV deals in Georgia right now.")
    st.markdown("**Works perfectly with PropStream, BatchLeads, foreclosure lists, probate exports, tax sales — any CSV with price + ARV.**")
