import pandas as pd
from app import db
from app.models import Text

def add_texts_from_file():
    input_path = "C:\\Users\\Mateusz\\OneDrive\\NLP\\stance-data-all-annotations\\data-all-annotations\\testdata-taskA-all-annotations.txt"
    stances = pd.read_csv(input_path, header=0, sep='\t')
    stances['Tweet length'] = stances['Tweet'].apply(len)
    for i, row in stances.iterrows():
        if row["Stance"] == 'NONE':
            is_stance = False
        else:
            is_stance = True
        text = Text(user_id=1, is_stance=is_stance , title=row["Target"], characters=row["Tweet length"],
                body=row["Tweet"], category=row["Target"], stance =  row["Stance"], opinion_towards = row["Opinion towards"])
        db.session.add(text)
    db.session.commit()
