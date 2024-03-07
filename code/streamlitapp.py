
import datetime
import numpy as np
import pandas as pd
import streamlit as st
from st_aggrid import AgGrid, JsCode, GridOptionsBuilder
#here we need to add system path so that it takes it as module 
import sys
import os

import lambda_


@st.cache(supress_st_warning=True)
def get_data(start_date, end_date):

    conn = lambda_.lambda_funciton.get_db_connection()
    sql="""select * from tweets_analytcs where timestampt betweet date('{start_date}' and date('{end_date}') """
    print(sql)

    df = pd.read_sql_query(sql)
    now = str(datetime.datetime.now())[:-7]

    st.sidebar.markdown("Latest update data: {} Adjust starting date or ending date to refresh data".format(now))


def get_local_tz():
    return datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo

@st.cache
def process_data(df, key_word, start_date, end_date):
    #converting to local timezone
    local_tz=get_local_tz
    df['timestamp'] = df['timestamp'].dt.tz_convert(local_tz)

    #removing author column 
    df=df.drop(columns=['author'])

    if key_word:
        df=df.loc[df['text'].str.contains(key_word), :]

    df['sentiment_score'] = df['sentiment_score'].round(2)
    #sort column index
    df=df.reindex(['timestamp', 'sentiment_score', 'text'], axis=1)



def display_table(df: pd.DataFrame) -> None:
    # this is some javascript code
    # to color cells
    # positive -> green, neuter -> white negative -> red
    sentiment_score_style = JsCode("""
    function(params) {
        if (params.value < 0) {
            return {
                'color': 'black',
                'backgroundColor': 'darkred'
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
    start_date = st.side_bar.text_input("Starting date", "2024-03-12")
    end_date = st.side_bar.text_input("End date", "2024-03-12")
    st.sidebar.subheader("Explanation")
    st.sidebar.markdown("Positive number in sentiment column indicates positive sentiment, and negative value negative. Scores above 0.2 or under -0.2 are considered very positive or very negative ")


    df=get_data(start_date=start_date, end_date=end_date)
    df = process_data(df, key_word=keyword, start_date=start_date, end_date=end_date)


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


    




