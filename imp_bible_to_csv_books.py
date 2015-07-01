"""
Import a bible in imp format, and export separated books in csv format
"""

from util import *

def imp_to_csv(translation, input_filename, output_directory):

    # Load the entire bible from an text file in imp format
    books,chapters,verses,texts = imp_load(input_filename)

    # Get a ordered set of books
    book_set = set()
    books_ordered = [b for b in books if b not in book_set and not book_set.add(b)]

    booknum = 0

    # for every book
    for book in books_ordered:
        booknum += 1

        # select all verses from the current book
        rows = [[c,v,t] for b,c,v,t in zip(books,chapters,verses,texts) if b == book]

        # export those verses to csv file
        csv_export_book("{0}/{1}_{2:0=2}_{3}.csv".format(output_directory, translation, booknum, book), rows)


imp_to_csv('ESV', '../../living_word/alignment/bibles_imp/ESV.txt', '../../living_word/alignment/csv_books/ESV')
imp_to_csv('Afr1953', '../../living_word/alignment/bibles_imp/Afr1953.txt', '../../living_word/alignment/csv_books/Afr1953')
imp_to_csv('DutSVV', '../../living_word/alignment/bibles_imp/DutSVV.txt', '../../living_word/alignment/csv_books/DutSVV')
