import streamlit as st
import datetime
import certifi
import os
from dotenv import load_dotenv
from pymongo import MongoClient
import pandas as pd
import plotly.express as px

import sys


# Load environment variables
load_dotenv()

# MongoDB connection
mongodb_uri = os.getenv("MONGODB_URI")
client = MongoClient(mongodb_uri, tlsCAFile=certifi.where())
db = client["inld"]

survey= db["survey"]
st.set_page_config(layout="wide",page_title="Dashboard",page_icon="./INLD_logo.webp")
# Date input widget
selected_date=None
# print(selected_date)
# Define the required keys
required_keys = [ "parliamentry", "halka"]
def retrieve_data(selected_date,other_fields=None):
    # Set start and end timestamps for the selected date
    # Define start_timestamp and end_timestamp
     start_timestamp = datetime.datetime.combine(selected_date, datetime.time.min)
     end_timestamp = datetime.datetime.combine(selected_date, datetime.time.max)
    

     # Convert start_timestamp and end_timestamp to Unix timestamps
     start_unix_timestamp = int(start_timestamp.timestamp())
     end_unix_timestamp = int(end_timestamp.timestamp())
    #  print(start_unix_timestamp,end_unix_timestamp)

    #  print(start_unix_timestamp, end_unix_timestamp)
     if other_fields is None:
      query = {
         "$and": [
        {"body." + key: {"$exists": True} for key in required_keys},
        {'timestamp': {'$gte': start_unix_timestamp, '$lt': end_unix_timestamp}}
         ]
            }
     else:
          query = {
    "$and": [
        
        {'timestamp': {'$gte': start_unix_timestamp, '$lt': end_unix_timestamp}}
    ]
    
}
    # Query MongoDB for documents with timestamp within the selected date range
     data=list(survey.find(query))

     return data
if "filter_date" not in st.session_state:
    st.session_state["filter_date"] = False

# Check if button is clicked to filter data by date
if not st.session_state["filter_date"] :
 if st.button('Filter Data by date'):
    st.session_state["filter_date"] = True
    st.experimental_rerun()
if  st.session_state["filter_date"] :
   if st.button("Remove Date Filter"):
       st.session_state["filter_date"] = False
       st.experimental_rerun()
# Check if filter by date is enabled
if st.session_state["filter_date"]:
    # If a date is selected, store it in session state
    selected_date = st.date_input('Select a date')
    st.session_state["selected_date"] = selected_date

    # Call the retrieve_data function with the selected date
    retrieved_data = retrieve_data(selected_date)

    if len(retrieved_data) == 0:
        st.header("No Data Available for date: " + f"{selected_date}")
        sys.exit()  # Stop execution if no data is available
    else:
        data_from_db = retrieved_data
else:
    # MongoDB query to find documents where the "body" object contains at least one of the required keys
    query = {"body." + key: {"$exists": True} for key in required_keys}
    data_from_db = list(survey.find(query))


data_to_display = [{"Number": d["sender"], **d["body"]} for d in data_from_db]

df= pd.DataFrame(data_to_display,columns=["Number","name","parliamentry","halka","village","ideological_support","morcha_membership","personal_message","support_again","joined_before","comeback_effort","party_leenage"])
# st.write(df)
df.columns = [col.title() for col in df.columns]
df['Ideological_Support'] = df['Ideological_Support'].replace("ideological_support_yes", "Yes")
df['Ideological_Support'] = df['Ideological_Support'].replace("ideological_support_no", "No")
df['Halka'] = df['Halka'].str.replace('halka_', '', regex=True)


df['Support_Again'] = df['Support_Again'].replace("sa_no", "No")
df['Support_Again'] = df['Support_Again'].replace("sa_yes", "Yes")
df['Joined_Before'] = df['Joined_Before'].replace("jb_yes", "Yes")
df['Joined_Before'] = df['Joined_Before'].replace("jb_no", "No")
df['Morcha_Membership'] = df['Morcha_Membership'].replace('_', ' ', regex=True)
df.columns = [col.title().replace('_', ' ') for col in df.columns]
with open('style.css') as f:
   st.markdown(f"<style>{f.read()}</style>",unsafe_allow_html=True)
# side bar
st.sidebar.image("./INLD_logo.webp",caption="Indian National Lok Dal")


# switcher or filter

st.sidebar.header("Please select filter")

district=st.sidebar.multiselect("Select Parliamentry",options=df["Parliamentry"].unique())
if not district:
    df1=df.copy()
else:
    df1=df[df["Parliamentry"].isin(district)]
halka=st.sidebar.multiselect("Select Halka",options=df1["Halka"].unique()) 
if not halka:
    df3=df1.copy()
else:
    df3=df1[df1["Halka"].isin(halka)]

df4=df3.copy()


st.dataframe(df4)

# calculation of data
total_user=len(df4)


ide_support=len(df4[df4["Ideological Support"] == "Yes"])
# male=len(df4[df4["Gender"] == "male"])
# female=len(df4[df4["Gender"] == "female"])
# Get the value counts of 'Parliamentry'
Parliamentry_counts = df4['Parliamentry'].value_counts().reset_index()


# Find the index (value) with the highest count
max_count_index = Parliamentry_counts['count'].idxmax()

# Get the key and value of the max count
max_count_key = Parliamentry_counts.loc[max_count_index, 'Parliamentry']
max_count_value = Parliamentry_counts.loc[max_count_index, 'count']

# Get the value of the max count in occupation
# Occupation_counts = df4['Occupation'].value_counts().reset_index()
# max_count_index_occupation=Occupation_counts["count"].idxmax()
# max_occupation_key=Occupation_counts.loc[max_count_index_occupation,"Occupation"].capitalize()
# max_occupation_value=Occupation_counts.loc[max_count_index_occupation,"count"]
if selected_date==None:
    total_surveyers=len(list(survey.find({})))
#     if district and halka:
#        halka= ["halha_"+h for h in halka]
#        print(halka)
#        total_surveyers = len(list(survey.find({
#     "body.parliamentry": {"$in": district},
#     "body.halka": {"$in": halka}
# })))
#     print(total_surveyers)
else:
    data= retrieve_data(selected_date,1)
    total_surveyers=len(data)
    # print(len(data),1)
co1,co2,co3,co4=st.columns(4,gap="large")

with co1:
    st.info("Surveys completed",icon="👫")
    st.metric("Survey Completion: Count",value=total_user)

with co2:
    st.info("Total Respondent.",icon="👨‍👩‍👧‍👦")
    st.metric("Count who respond on survey",value=total_surveyers)
with co3:
    st.info("Ideological Support",icon="🤝")
    st.metric("Support : Count",value=ide_support)
with co4:
    st.info("Maximum Support",icon="👩‍👧‍👧")
    st.metric(max_count_key,value=max_count_value)
# with co5:
#     st.info("Profession, trend",icon="💼")
#     st.metric(max_occupation_key,value=max_occupation_value)


# col1,col2 =st.columns(2)


    # Group by Parliamentry and count the number of people in each Parliamentry
Parliamentry_counts = df4['Parliamentry'].value_counts().reset_index()
Parliamentry_counts.columns = ['Parliamentry', 'Number of People']

   # Plot the bar chart
st.subheader("Parliamentry wise People")
fig = px.bar(Parliamentry_counts, x="Parliamentry", y="Number of People", text=Parliamentry_counts['Number of People'],
             template="seaborn",color='Parliamentry')
    
    

    # Render the chart
st.plotly_chart(fig, use_container_width=True)

# with col2:
#     Occupation_counts = df4['Occupation'].value_counts().reset_index()
#     Occupation_counts.columns = ['Occupation', 'Number of People']

#     # Plot the pie chart
#     st.subheader("Occupation wise People")
#     fig = px.pie(Occupation_counts, values="Number of People", names="Occupation")
#     fig.update_traces(textinfo='percent+label', textposition='inside', showlegend=False)
#     st.plotly_chart(fig, use_container_width=True)



# Group by Morcha Membership and count the number of people in each Parliamentry
morcha_counts = df4['Morcha Membership'].value_counts().reset_index()
morcha_counts.columns = ['Morcha Membership', 'Number of People']

# Plot the bar chart
st.subheader("Morcha Membership ")
fig = px.bar(morcha_counts, x="Morcha Membership", y="Number of People", text=morcha_counts['Number of People'],
             template="seaborn",color='Morcha Membership')
    
    

# Render the chart
st.plotly_chart(fig, use_container_width=True)




# Download orginal DataSet
csv = df4.to_csv(index = False).encode('utf-8')
st.download_button('Download Survey Data', data = csv, file_name = "Data.csv",mime = "text/csv",use_container_width=True)