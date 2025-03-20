import streamlit as st
from snowflake.snowpark.functions import col
import requests

# App Title
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom smoothie!")

# User Input
name_on_order = st.text_input("Name on the Order")
st.write("The name on your Smoothie will be:", name_on_order)

# Snowflake Connection
cnx = st.connection("snowflake")
session = cnx.session()

# Fetch fruit options
my_dataframe = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME"), col("SEARCH_ON")).to_pandas()

# Extract lists for selection
fruit_list = my_dataframe["FRUIT_NAME"].tolist()

# Multi-select for ingredients
ingredients_list = st.multiselect("Choose up to 5 ingredients:", fruit_list, max_selections=5)

if ingredients_list:
    ingredients_string = " ".join(ingredients_list)

    for fruit_chosen in ingredients_list:
        # Get the corresponding search term
        search_on = my_dataframe.loc[my_dataframe["FRUIT_NAME"] == fruit_chosen, "SEARCH_ON"].iloc[0]

        st.subheader(f"{fruit_chosen} Nutrition Information")

        # Fetch API data
        smoothiefroot_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on}")

        if smoothiefroot_response.status_code == 200:
            st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
        else:
            st.error(f"Could not fetch data for {fruit_chosen}")

# Submit Order
time_to_insert = st.button("Submit Order")

if time_to_insert:
    session.sql(
        "INSERT INTO smoothies.public.orders (ingredients, name_on_order) VALUES (%s, %s)"
    ).bind((ingredients_string.strip(), name_on_order)).collect()

    st.success("Your Smoothie is ordered!", icon="✅")
