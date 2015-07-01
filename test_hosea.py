from util import *

dir="../../living_word/alignment/test_hosea"

#translate_csv(dir+"/csv_books/Afr1953_28_Hos.csv",'af',dir+"/translated/Afr1953_28_Hos.csv")
#translate_csv(dir+"/csv_books/ESV_28_Hos.csv",'en',dir+"/translated/ESV_28_Hos.csv")
#translate_csv(dir+"/csv_books/NAB_28.csv",'en',dir+"/translated/NAB_28_Hos.csv")

translations = ['Afr1953','ESV','NAB']
translated = ["{0}/translated/{1}_28_Hos.csv".format(dir,t) for t in translations]

align(translations, translated, dir+"/aligned/28_Hos.csv")
