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

# Fetch fruit options from Snowflake
try:
    my_dataframe = session.sql("SELECT FRUIT_NAME, SEARCH_ON FROM smoothies.public.fruit_options").collect()
    pd_df = pd.DataFrame(my_dataframe)  # Convert to Pandas DataFrame
except Exception as e:
    st.error(f"❌ Failed to fetch data from Snowflake: {e}")
    st.stop()

# Ensure data is retrieved
if pd_df.empty:
    st.warning("⚠️ No fruit options found in the database.")
    st.stop()

# Multi-select input
ingredients_list = st.multiselect("Choose up to 5 ingredients:", pd_df["FRUIT_NAME"], max_selections=5)

# Initialize the ingredients string
ingredients_string = ""

# Process selections
if ingredients_list:
    ingredients_string = ", ".join(ingredients_list)  # ✅ Corrected `join()` usage
    
    for fruit_chosen in ingredients_list:
        search_on = pd_df.loc[pd_df["FRUIT_NAME"] == fruit_chosen, "SEARCH_ON"].iloc[0]
        st.subheader(f"{fruit_chosen} Nutrition Information")

        # Fetch nutrition info
        try:
            response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on}")
            if response.status_code == 200:
                st.dataframe(data=response.json(), use_container_width=True)
            else:
                st.warning(f"⚠️ Unable to fetch nutrition details for {fruit_chosen}.")
        except Exception as e:
            st.error(f"❌ API request failed: {e}")

# Submit Order Button
if st.button("Submit Order"):
    if not ingredients_string or not name_on_order.strip():
        st.error("❌ Please enter your name and select at least one ingredient.")
    else:
        try:
            session.sql(
                "INSERT INTO smoothies.public.orders (ingredients, name_on_order) VALUES (?, ?)"
            ).bind((ingredients_string, name_on_order.strip())).collect()
            st.success("✅ Your Smoothie is ordered!", icon="✅")
        except Exception as e:
            st.error(f"❌ Order submission failed: {e}")
