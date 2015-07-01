
import os
import sys
from util import *

input_dir = "./translated"
#input_dir = str(sys.argv[1])

translations = ['ESV','Afr1953','DutSVV']
translated_files = os.listdir(input_dir)
aligned_files = os.listdir("./aligned")

# use the translated_files folder as a job list for alignment
for filename in translated_files:
    translation, booknum, book = filename.split('_',3)
    book = book.rsplit(".",1)[0]

    # only proceed if this file has not been used for alignment yet
    out_filename = "{0}_{1}.csv".format(booknum, book)
    if out_filename not in aligned_files:

        # get the filnames for other translations of this book
        in_filenames = [input_dir+"/{0}_{1}_{2}.csv".format(t,booknum,book) for t in translations]

        # run alignment
        print "Aligning:", in_filenames, out_filename
        align(translations, in_filenames, "./aligned/"+out_filename)

        # update list of completed files
        aligned_files = os.listdir("./aligned")
