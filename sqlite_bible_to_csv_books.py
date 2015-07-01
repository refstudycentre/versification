"""
Import a bible from an sqlite3 file (E-Sword .bblx) format, and export separated books in csv format
"""

from util import *
import sqlite3

def sqlite3_to_csv(translation, filename):

    # Open the database
    connection = sqlite3.connect(filename)
    c = connection.cursor()

    # Get a list of books
    c.execute("select distinct book from bible")
    books = [i[0] for i in c.fetchall()]

    # For each book
    for booknum in books:

        # Query the DB for all verses in this book
        result = c.execute("select chapter,verse,scripture from bible where book=?",(booknum,)).fetchall()

        # TODO: strip surrounding whitespace from text?

        # Save the verses to csv file
        csv_export_book("{0}_{1:0=2}.csv".format(translation, booknum),rows=result)


sqlite3_to_csv("NAB","../../living_word/NAB.bblx")
