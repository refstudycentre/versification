from util import *
import MySQLdb

dir="../../living_word/alignment/test_hosea"

# STEP 1: translate

#translate_csv(dir+"/csv_books/Afr1953_28_Hos.csv",'af',dir+"/translated/Afr1953_28_Hos.csv")
#translate_csv(dir+"/csv_books/ESV_28_Hos.csv",'en',dir+"/translated/ESV_28_Hos.csv")
#translate_csv(dir+"/csv_books/NAB_28.csv",'en',dir+"/translated/NAB_28_Hos.csv")

# STEP 2: align

#translations = ['Afr1953','ESV','NAB']
#translated = ["{0}/translated/{1}_28_Hos.csv".format(dir,t) for t in translations]

#align(translations, translated, dir+"/aligned/28_Hos.csv")

# STEP 3: (after being checked by humans) import to mysql database

# Load aligned bible book
hosea = csv_import_aligned_book(dir+"/checked/28_Hos.csv")

# Connect to database
db = MySQLdb.connect("localhost","d1","d1","d1", charset="utf8")
cursor = db.cursor()

# Specify the book number and name for each translation
booknum={
    'Afr1953':28,
    'ESV':28,
}

# Specify the mapping of translation names to translation ids
translation_num = {
    'Afr1953':1,
    'ESV':2,
}

# Keep track of records inserted
n = 0

# TODO: remove this. For now, clear the table before importing and start with vid=0
print cursor.execute(u"delete from lw_verses")
vid=0

# For every group of verses
for group in hosea:

    # TODO: if inserting a new translation, first find the correct vid
    # For now, generate a vid for every group
    vid += 1

    # For every verse in the group (one from each translation)
    for translation in group:

        tnum = translation_num[translation]
        bnum = booknum[translation]
        vnum = group[translation]['versenum']
        cnum = group[translation]['chapternum']
        text = group[translation]['text']

        # Try to insert the new verse
        result = cursor.execute(u"insert into lw_verses (vid, translation, booknum, chapternum, versenum, versetext) values (%s,%s,%s,%s,%s,%s)",(vid, tnum, bnum, cnum, vnum, text))
        if result == 1:
            n += 1
        else:
            print "row not inserted.",result

# Close the database
db.commit()
db.close()

print "records inserted:",n