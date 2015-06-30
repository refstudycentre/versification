"""
Import a bible in imp format, and export separated books in csv format
"""

import unicodecsv, codecs
from util import *

def imp_to_csv(translation):

    books,chapters,verses,texts = imp_load(translation+".txt")

    current_book = None
    n = 0
    # Loop through entire bible
    for book,cnum,vnum,text in zip(books,chapters,verses,texts):

        # If the book changes, write out old csv file and start a new one
        if book != current_book:
            if current_book != None:

                # Write to CSV file
                with open("./to_translate/{0}_{1:0=2}_{2}.csv".format(translation, n, current_book),'wb') as f:
                    cw = unicodecsv.writer(f,encoding='utf-8')
                    cw.writerows(rows)

            current_book = book
            n += 1
            rows = []
            rows.append(['book','chapter','verse','text']) # header

        # Add a row for this verse
        rows.append([book,cnum,vnum,text])

    # Write last book to CSV file
    with open("./to_translate/{0}_{1:0=2}_{2}.csv".format(translation, n, current_book),'wb') as f:
        cw = unicodecsv.writer(f,encoding='utf-8')
        cw.writerows(rows)


for t in ['ESV','Afr1953','DutSVV']:
    imp_to_csv(t)
