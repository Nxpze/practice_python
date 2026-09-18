import pandas as pd
import streamlit as st


st.set_page_config(page_title="EDS2 Project")

st.title("EDS2 Project")
st.write("This is a sample Streamlit application.")

df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})

st.subheader("My first DataFrame")
st.dataframe(df, width="stretch", hide_index=True)