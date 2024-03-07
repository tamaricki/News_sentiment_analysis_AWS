
import datetime
import numpy as np
import pandas as pd
import streamlit as st
from st_aggrid import AgGrid, JsCode, GridOptionsBuilder
#here we need to add system path so that it takes it as module 
import sys
import os

parent = os.path.dirname(os.path.realpath(__file__))+'/../..'
sys.path.append(parent)
import lambda_.lambda_function
#c=lambda_.lambda_function.get_db_connection()

#@st.cache_resource
def get_data(start_date='2024-01-01', end_date='2026-01-01'):

    conn = lambda_.lambda_function.get_db_connection()
    sql=f"""select * from tweets_analytics where timestamp between date('{start_date}') and date('{end_date}') """
    print(sql)

    df = pd.read_sql_query(sql, conn)
    #print(df)
    now = str(datetime.datetime.now())[:-7]

    st.sidebar.markdown("Latest update data: {} Adjust starting date or ending date to refresh data".format(now))
    return df


def get_local_tz():
    return datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo

#@st.cache_data
def process_data(df, key_word, start_date, end_date):
    #converting to local timezone
    local_tz=get_local_tz()
    df['timestamp'] = df['timestamp'].dt.tz_convert(local_tz)
    #print(df)

    #removing author column 
    df=df.drop(columns=['author'])

    if key_word:
        df=df.loc[df['text'].str.contains(key_word), :]

    df['sentiment_score'] = df['sentiment_score'].round(2)
    #sort column index
    df=df.reindex(['timestamp', 'sentiment_score', 'text'], axis=1)

    return df

def display_table(df: pd.DataFrame) -> None:
    # this is some javascript code
    # to color cells
    # positive -> green, neuter -> white negative -> red
    sentiment_score_style = JsCode("""
    function(params) {
        if (params.value < 0) {
            return {
                'color': 'black',
                'backgroundColor': 'red'
            }
        } else if (params.value == 0) {
            return {
                'color': 'black',
                'backgroundColor': 'gray'
            }
        } else {
            return {
                'color': 'black',
                'backgroundColor': 'green'
            }
        }
    };
    """)
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_column("sentiment_score",
                        cellStyle=sentiment_score_style)

    AgGrid(df, height=500, width=1000,
           fit_columns_on_grid_load=False,
           gridOptions = gb.build(),
           allow_unsafe_jscode=True)
    return None

st.set_page_config(layout='wide')

if __name__=="__main__":
    st.title('News analytics sentiment score dashboard')
    view_name=st.sidebar.radio("", ("View news", 'Analytics'))
    keyword=st.sidebar.text_input("Keyword", "")
    start_date = st.sidebar.text_input("Starting date", "2024-02-01")
    end_date = st.sidebar.text_input("End date", "2025-03-01")
    st.sidebar.subheader("Explanation")
    st.sidebar.markdown("Positive number in sentiment column indicates positive sentiment, and negative value negative. Scores above 0.2 or under -0.2 are considered very positive or very negative ")


    df= get_data(start_date=start_date, end_date=end_date)
    #print(type(df))
    df=process_data(df, key_word=keyword, start_date=start_date, end_date=end_date)


    if df.empty:
        st.error('Your search parameter resulted in no findings.')


    col1, col2, col3 = st.columns(3)

    if view_name=="View news":
        display_table(df)

    else:
        #sentiments over time 
        st.markdown("Sentiment score over time")
        keyword_info = f"Keyword = {keyword}" if keyword else ""
        st.markdown(f"{keyword_info} start date={start_date} \n end date ={end_date}")
        df.set_index('timestamp')
        st.line_chart(df['sentiment_score'])


    





# %%
