import os
from util import *

translations = ['ESV','Afr1953','DutSVV']
languages = ['en','af','nl']

translated_files = os.listdir("./translated")
translatable_files = os.listdir("./to_translate")

files = [f for f in translatable_files if f not in translated_files]

for t,l in zip(translations, languages):
    for file in files:
        if file.startswith(t) and file.endswith(".csv"):
            print "Translating:", file
            translate_csv("./to_translate/{0}".format(file), l, "./translated/{0}".format(file))

print "done :)"