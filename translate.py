## LOAD PACKAGES
# use googletrans package to translate texts automatically
from googletrans import Translator
# for sqlite file
import sqlite3
import csv
import time
import random

## LOAD DATA
kununu = sqlite3.connect('kununu_long.sqlite')
c = kununu.cursor()

def read_from_db():
    c.execute('SELECT comment FROM kununu_long')
    data = c.fetchall()
    return(data)

# get comments
data = read_from_db()

# get comments with id to reference later
def get_comments(data):
    comments = []
    counter = 0
    # data are tuples with (comment,) -> turn them into (comment, id) for non None comments
    for comment in data:
        if comment[0] is not None:
            comments.append((comment[0], counter))
        counter +=1
    return(comments)

# perform get_commments
comments = get_comments(data)
# len(data) = 623025 -> len(comments) = 77782 only comments with text are considered, rest do not entail comments

## SAVE COMMENTS AS CSV
# format: comment; doc_id: two columns
csv_columns = ['doc_id','comment']
# create dictionary suitable to transform to column based csv
dict_data = [{'doc_id':id, 'comment':comment} for comment, id in comments]
# name csv file
csv_file = "kununu_comments.csv"
try:
    with open(csv_file, newline = '', mode='w', encoding='utf-8-sig') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        writer.writeheader()
        for data in dict_data:
            writer.writerow(data)
except IOError:
    print("I/O error")

## close connection to sqlite
kununu.close()
c.close()

## OPEN ONCE SAVED TO SAVE TIME WITH READING THE DATA
# open as a dict with the id as key and the comment as a value string
with open('kununu_comments.csv',newline='', mode='r', encoding='utf-8-sig') as infile:
    reader = csv.reader(infile)
    mydict = [{rows[0]:[rows[1]]} for rows in reader]
    full_dict= {}
    for d in mydict:
        full_dict.update(d)

# pop first element for colnames
full_dict.pop("doc_id")

# lastly translated comment
last_translation = list(full_dict)[len(full_dict)-1]

# translator is very instable -> try except enforces the translation being done after an error occurs by saving the
# last key for a condition in the while loop that runs until the lastly translated key, value pair is actually the
# last pair in the entire dictionary
counter = 0
# here from back to the beginning as a test, as unsure, whether blocking would happen or not and second translation
# was running from beginning to end of dict
while last_translation is not list(full_dict)[0]:
    import json
    translator = Translator()
    try:
        print("sth happens")
        for key in reversed(list(full_dict)):
            if len(full_dict[key]) == 1:
                # draws random float btw. 0.05 and 0.7 seconds to wait btw. translations
                seconds = random.uniform(0.05, 0.7)
                # verbose to see progress
                if counter %100 == 0:
                    print("Wait " + str(seconds) + " seconds")
                # wait
                time.sleep(seconds)
                # translate first element of value list
                translation = translator.translate(full_dict[key][0], dest='en')
                # append translation to value list
                full_dict[key].append(translation.text)
                # verbose to see progress
                if counter%200 == 0:
                    print(key)
                    print(translation.text)
                # change while condition variable
                last_translation = key
                counter += 1
    except:
        print("exception")
        break

# save full_dict as csv with three columns: id, comment, translation

# Any non translated comment left? -> NO
next(key for key, value in full_dict.items() if len(full_dict[key]) == 1)

# ## SAVE TRANSLATED COMMENTS AS CSV
# # format: comment; doc_id: two columns
csv_columns = ['doc_id','comment','translation']
# create dictionary suitable to transform to column based csv
translated_dict = [{'doc_id':doc_id, 'comment':comment[0], 'translation':comment[1]} for doc_id, comment in full_dict.items()]
# name csv file
csv_file = "kununu_translated.csv"
try:
    with open(csv_file, newline = '', mode='w', encoding='utf-8-sig') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        writer.writeheader()
        for data in translated_dict:
            writer.writerow(data)
except IOError:
    print("I/O error")