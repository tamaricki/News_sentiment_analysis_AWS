#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from dateutil import parser
from datetime import datetime
import logging
import json
import os

#accurate cross-platform timezone calculations 
import pytz
#botocore and boto3 are foundation for AWS CLI
from botocore.exceptions import ClientError
import boto3
from nltk.sentiment import SentimentIntensityAnalyzer
import pandas as pd
import psycopg2
import psycopg2.extras
#from twython import Twython
from newsapi import NewsApiClient


###do not change 
try:
    sia=SentimentIntensityAnalyzer()

except LookupError:
    import nltk
    #in lambda you can only write in tmp folder and nltk needs to download the data
    nltk.download('vader_lexicon', download_dir='/tmp')
    nltk.data.path.append("/tmp")
    sia=SentimentIntensityAnalyzer()


def _time_parser(news_datetime):
    """parsing time from news api to datetime object """

    return parser.parse(news_datetime)

####

###change 
def is_recent(article, max_time_interval_days=2): 
    time_created = _time_parser(article['publishedAt'])
    now = datetime.now(tz=pytz.UTC)
    days_diff=(now - time_created).days
    
    recent= days_diff <=max_time_interval_days
    return recent

###change
def extract_data(news):
    """ extract arbitary data from reveiw dict, as start
    extract user id, time and text. """
    author = news['author']
    time = _time_parser(news['publishedAt'])
    text = news['description']
    return {'author': author, 'publishedAt':time, 'text':text}
###DO NOT CHANGE
def _get_sentiment(text):
    score= sia.polarity_scores(text) # it actually returns 4 values, we want just one between -1 (very negative) and 1(very positive), 0 is neural?
    score = score['neg']*-1 + score['pos']

    return score

def add_sentiment_score(news):
    news['sentiment_score'] = _get_sentiment(news['text'])
    return news


def upload_file_s3(local_file_name, bucket, s3_object_name=None):

    if s3_object_name is None:
        s3_object_name=local_file_name

    s3_client=boto3.client('s3')

    try:
        s3_client.upload_file(local_file_name, bucket, s3_object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True

def get_db_connection():
    conn = psycopg2.connect(user='postgres', password=os.environ['DB_PASSWORD'], host=os.environ['DB_HOST'], 
            port='5432', connect_timeout=1)

    return conn
##CHANGE
def convert_timestamp_to_int(news):
    news=news.copy()
    news['publishedAt'] = news['publishedAt'].timestamp()
    return news


def insert_data_in_db(df, conn, table_name='tweets_analytics'):
    len_data = len(df)>0

    if len_data and conn is not None:
        try:
            cur = conn.cursor()
        #reshaping data in strings in order to perform batch insert 
            df_columns = df.columns
            columns = ",".join(df_columns)

            values = "VALUES({})".format(",".join(["%s" for _ in df_columns])) 

            insert_string ="INSERT INTO {} ({}) {}"
            statemet = insert_string.format(table_name, columns, values)

            psycopg2.extras.execute_batch(cur, statement, df.values)
            conn.commit()

            print('succesful update')

        except psycopg2.errors.InFailedSqlTransaction:
            # if the transaction fails, rollback to avoid DB lock problems
            logging.exception('FAILED transaction')
            cur.execute("ROLLBACK")
            conn.commit()

        except Exception as e:
            # if the transaction fails, rollback to avoid DB lock problems
            logging.exception(f'FAILED  {str(e)}')
            cur.execute("ROLLBACK")
            conn.commit()
        finally:
            # close the DB connection after this
            cur.close()
            conn.close()
    elif conn is None:
        raise ValueError('Connection to DB must be alive!')
    elif len(df) == 0:
        raise ValueError('df has 0 rows!')

def lambda_handler(event, context):
    #wrapping body to try /catch to avoid lambda automatically retrying
    #environment variables
    try:
        S3_BUCKET_NAME = os.environ['S3_BUCKET_NAME']

        news = NewsApiClient(os.environ['NEWS_API_KEY'])

        

       # today = datetime.now().date() this will be needed if we add from_param 
        articles = news.get_everything(q='sport',language='en')
     
        recent=[news for news in articles['articles'] if is_recent(news)]

    #adding sentiment 
        recent = [add_sentiment_score(news) for news in recent]

        recent_news = [extract_data(news) for news in recent]

        clean_news = []
        #skipping missing values 
        for art in recent_news:
            if art['author'] is None:
                continue
        clean_news.append(art)

    #create filename with timestamp
        now_str = datetime.now(tz=pytz.UTC).strftime('%d-%m-%Y-%H:%M:%S')
        filename = f'{now_str}.json'

        output_path_file=f'/tmp/{filename}' #in lambda files are in tmp folder
        with open(output_path_file,'w') as out:
            news_to_save=[convert_timestamp_to_int(news) for news in recent_news]

            json.dump(news_to_save, out)
        upload_file_s3(local_file_name=output_path_file, bucket=S3_BUCKET_NAME, s3_object_name=f'raw-messages/{filename}')

        news_df = pd.DataFrame(recent)
        conn=get_db_connection()
        insert_data_in_db(news, conn, 'tweets_analytics')
    except Exception as e:
        logging.exception('Exception occured \n')

    print('Lambda executed successfully!')

if __name__=='__main__':
    lambda_handler({}, {})

