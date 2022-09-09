
from unittest import result
import nltk
import pandas as pd
import sqlite3 as sd
from flask import Flask, flash, request, redirect, url_for,render_template
import os,string,random
from werkzeug.utils import secure_filename
UPLOAD_FOLDER = 'D:\Interface'
ALLOWED_EXTENSIONS = {'db','sql'}
app = Flask(__name__,static_url_path='/static')
p=""
chat_row_neg={}
@app.route('/interface',methods=["POST",'GET'])
def uploadfile():
    if(request.method=="POST"):
        data=request.files['upload']
        data.save(secure_filename(data.filename))
        p=data.filename
        conn=sd.connect(p)
        if(conn):
            print("DB connected successfully")
        cursor=pd.read_sql_query("SELECT sender_jid_raw_string,text_data from message WHERE sender_jid_raw_string is NOT NULL and text_data is NOT NULL and text_data!='' ORDER BY sender_jid_raw_string ",conn)
        name=''.join(random.choices(string.ascii_lowercase +
                             string.digits, k=8))
        cursor.to_csv(name+'.csv',index=False)
        data=pd.read_csv(name+'.csv',nrows=2000).astype('str')
        data.dropna()
        chat_row_pos={}
        global chat_row_neg
        df=pd.DataFrame(data)
        df=df.reset_index()
        from nltk.sentiment.vader import SentimentIntensityAnalyzer
        sentiments = SentimentIntensityAnalyzer()
        df["Positive"] = [sentiments.polarity_scores(i)["pos"] for i in df["text_data"]]
        df["Negative"] = [sentiments.polarity_scores(i)["neg"] for i in df["text_data"]]
        df["Neutral"] = [sentiments.polarity_scores(i)["neu"] for i in df["text_data"]]
        for index,row in df.iterrows():
            chat_row_neg[row['sender_jid_raw_string']]=0.0
            chat_row_pos[row['sender_jid_raw_string']]=0.0
        for index,row in df.iterrows():
            x=chat_row_pos[row['sender_jid_raw_string']]
            y=chat_row_neg[row['sender_jid_raw_string']]
            x+=row["Positive"]
            y+=row["Negative"]
            chat_row_neg[row['sender_jid_raw_string']]=y
            chat_row_pos[row['sender_jid_raw_string']]=x
        i=0
        x=0
        y=0
        k=0
        chat_row_neg=sorted(chat_row_neg.items(), key=lambda kv:
                        (kv[1], kv[0]),reverse=True)
        negative=chat_row_neg
        for x in chat_row_neg:
            print(x)
        return redirect(url_for('display'))
    return render_template('interface.html')
@app.route('/display')
def display():
    return render_template('display.html',result=chat_row_neg)
app.run('0.0.0.0',port="5000")
