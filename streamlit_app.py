import streamlit as st
from snowflake.snowpark.functions import col
import requests
import pandas as pd

# App Title
st.title("🥤 Customize Your Smoothie! 🥤")
st.write("Choose the fruits you want in your custom smoothie!")

# User Input
name_on_order = st.text_input("Name on the Order")
st.write(f"The name on your Smoothie will be: **{name_on_order}**")

# Snowflake Connection
cnx = st.connection("snowflake")
session = cnx.session()

# Fetch fruit options
try:
    my_dataframe = session.sql("SELECT FRUIT_NAME, SEARCH_ON FROM smoothies.public.fruit_options").collect()
    pd_df = pd.DataFrame(my_dataframe)  # Convert to Pandas DataFrame safely
except Exception as e:
    st.error(f"❌ Failed to fetch data from Snowflake: {e}")
    st.stop()

# Ensure data was retrieved
if pd_df.empty:
    st.warning("⚠️ No fruit options found in the database.")
    st.stop()

# Multi-select input
ingredients_list = st.multiselect("Choose up to 5 ingredients:", pd_df["FRUIT_NAME"], max_selections=5)

# Process selections
if ingredients_list:
    ingredients_string = ", ".join(ingred
