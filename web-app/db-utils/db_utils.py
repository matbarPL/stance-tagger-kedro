from app import db
from app.models import Text, TextCategory, TextFavourAgainst
import pandas as pd
import random
from random import randrange
from datetime import timedelta
import sqlite3
import csv
import os

def random_date(start, end):
    """
    This function will return a random datetime between two datetime
    objects.
    """
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = randrange(int_delta)
    return start + timedelta(seconds=random_second)
from datetime import datetime


file_path = "..\\..\\stance-tagger-kedro\\data\\01_raw\\stances.csv"

def add_text_to_database(file_path):
    d1 = datetime.strptime('1/1/2020 1:30 PM', '%m/%d/%Y %I:%M %p')
    d2 = datetime.strptime('4/22/2020 4:50 AM', '%m/%d/%Y %I:%M %p')
    df = pd.read_csv(file_path,delimiter = ",")
    for index,row in df.iterrows():
        text = Text(user_id = 1, body=row["Tweet"], title="", stance=row["Stance"],
                    target=row["Target"], opinion_towards=row["Opinion towards"],
                    sentiment=row["Sentiment"])
        text.publication_date = random_date(d1, d2)
        db.session.add(text)
    db.session.commit()

def dump_to_csv():
    outfile = open('mydump.csv', 'w', encoding="utf-8")
    outcsv = csv.writer(outfile)
    records = db.session.query(Text).all()
    [outcsv.writerow([getattr(curr, column.name) for column in Text.__mapper__.columns]) for curr in records]

    outfile.close()

if __name__ == '__main__':
    add_text_to_database(file_path)