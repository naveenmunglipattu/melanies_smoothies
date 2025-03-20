import streamlit as st

from snowflake.snowpark.context import get_active_session

from snowflake.snowpark.functions import col,when_matched
 
# Title with emoji

st.title("🥤 Pending Smoothie Orders! 🥤")

st.write("Orders that need to be filled.")
 
# Get active Snowflake session

session = get_active_session()
 
# Fetch pending orders (where ORDER_FILLED is False or NULL)

my_dataframe = (

    session.table("smoothies.public.orders")

    .filter(col("ORDER_FILLED") == False)  # Fetch only unfilled orders

    .select( col("order_uid"),col("INGREDIENTS"), col("NAME_ON_ORDER"), col("ORDER_FILLED"),col("order_ts"))

    .to_pandas()  # Convert to Pandas for Streamlit

)
 
# Editable table (users can check the ORDER_FILLED box)

editable_df = st.data_editor(my_dataframe)
 
# Show the updated dataframe (optional)

#st.write("✅ Updated Order Status:")

#st.dataframe(editable_df)
 
#to add a submit button

submitted=st.button('submit')
 
 
if submitted:

    og_dataset = session.table("smoothies.public.orders")

    edited_dataset = session.create_dataframe(editable_df)
 
    try: 

        og_dataset.merge(

        edited_dataset,

        (og_dataset['ORDER_UID'] == edited_dataset['ORDER_UID']),

        [when_matched().update({'ORDER_FILLED': edited_dataset['ORDER_FILLED']})]

     )

        st.success("Order's updated", icon="👍")
 
    except Exception as e:

        st.write("Something went wrong:", e)
 
