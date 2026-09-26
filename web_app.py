import pandas as pd
import os
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

DB_URL = os.getenv("DB_URL")

if not DB_URL:
    raise ValueError("DB_URL is not set in the environment variables.")

engine = create_engine(DB_URL)

query = "SELECT * FROM netflix_titles;"
st.set_page_config(page_title="EDS2 Project")

st.title("EDS2 Project")
st.write("This is a sample Streamlit application.")

df = pd.read_sql(query, con=engine)

st.subheader("My first DataFrame")
st.dataframe(df, width="stretch", hide_index=True)