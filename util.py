
import numpy as np

import unicodecsv
import codecs
import goslate

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

def imp_load(filename):

    texts = []
    books = []
    chapters = []
    verses = []

    # Read in a whole bible
    with codecs.open(filename,encoding='utf-8') as f:
        bibletext = f.read()

    # Split by verse
    bible_verses = bibletext.split('$$$')

    # Process verses
    for verse in bible_verses:
        try:
            verse = verse.split('\n',1)
            ref = verse[0].strip()
            text = verse[1].strip()
            ref = ref.split('.')
            book = ref[0].strip()
            cnum = ref[1].strip()
            vnum = ref[2].strip()

            texts.append(text)
            books.append(book)
            chapters.append(cnum)
            verses.append(vnum)

        except IndexError:
            pass

    return books, chapters, verses, texts

def load_verses(filename):
    """
    load verses from csv file
    """

    texts = []
    books = []
    chapters = []
    verses = []

    # Read in a whole file of verses
    with open(filename,'rb') as f:
        cr = unicodecsv.reader(f, encoding='utf-8')
        header = cr.next() # skip header

        # Process verses
        for book,cnum,vnum,text in cr:
            books.append(book)
            chapters.append(cnum)
            verses.append(vnum)
            texts.append(text)

    # return results
    return books,chapters,verses,texts

def load_translated_verses(input_translations, input_files):
    """
    load translated bibles from csv files
    """

    texts_en = []
    texts_original = []
    translations = []
    books = []
    chapters = []
    verses = []

    # For each translation
    for in_t, in_fname in zip(input_translations, input_files):
        
        # Read in a whole (Google translated) file of verses
        with open(in_fname, 'rb') as f:
            cr = unicodecsv.reader(f, encoding='utf-8')
            header = cr.next() # skip header

            # Process verses
            for book,cnum,vnum,text_original,text_en in cr:
                translations.append(in_t)
                books.append(book)
                chapters.append(cnum)
                verses.append(vnum)
                texts_original.append(text_original)
                texts_en.append(text_en)

    # return results
    return translations,books,chapters,verses,texts_original,texts_en

def calculate_similarity(texts, translations):

    # Train the tf-idf thingy on the translated texts
    tfidf = TfidfVectorizer().fit_transform(texts)

    # Build a matrix representation of the similarities between verses
    # This will yield a simmetrical matrix
    # TODO: For performance and logical reasons: Only calculate similarity for nearby verses, assume others 0 ?
    M = np.array([linear_kernel(tfidf[j:j+1], tfidf).flatten() for j in range(len(texts))])

    # Hack(ish): Set similarity with verses of same translation to 0
    for i in range(len(M)):
        for j in range(i+1):
            if translations[i] == translations[j]:
                M[i][j] = M[j][i] = 0

    # print np.round(M*100,0)

    return M

def find_best_couple(M,t):
    """
    find best couple in similarity matrix M
    the translation(s) of each verse is given in t
    """

    # assume values are 0 for verses in same translation
    i_max, j_max = np.unravel_index(M.argmax(), M.shape)
    P_max = M[i_max, j_max]

    """
    N = len(M)
    P_max = 0
    i_max = None
    j_max = None

    for i in range(N):
        for j in range(i):

            # Make sure they are not from the same translation(s)
            if len([val for val in t[i] if val in t[j]]) == 0:

                # Check if similarity is best yet
                if M[i][j] > P_max:
                    P_max = M[i][j]
                    i_max = i
                    j_max = j
                    
                    if P_max == 1.: # float comparison... this is fine because there are not many posible values for this using tf-idf
                        return i_max, j_max, P_max
    """
    
    return i_max, j_max, P_max

def merge_nodes(M,a,b):
    """
    merge indices a and b in similarity matrix M into one supernode,
    averaging similarity values between the supernode and other verses
    """
    
    N = len(M)
    
    # calculate a new row (and column) for the supernode
    supernode_similarity = [np.average([M[k][a],M[k][b]]) for k in range(N)]
    
    # append the row (this will jumble the verse order...)
    newM = np.append(M, np.array(supernode_similarity)[None,:], axis=0)
    
    # append 0 (supernode's similarity with itself) to the row and add it as a column
    supernode_similarity.append(0.)
    newM = np.append(newM, np.array(supernode_similarity)[:,None], axis=1)
    
    # to preserve verse indices, don't delete
    # newM = np.delete(newM,[a,b],axis=0)
    # rather make rows a and b 0
    # to preserve verse indices, don't delete
    # newM = np.delete(newM,[a,b],axis=1)
    # rather make columns a and b 0
    
    newM[:,a] = np.zeros_like(newM[:,a])
    newM[:,b] = np.zeros_like(newM[:,b])
    newM[a,:] = np.zeros_like(newM[a,:])
    newM[b,:] = np.zeros_like(newM[b,:])
    
    return newM

def group_verses(M, t, numT, P_min = 0.1):
    """
    Automatically group verses
    t = the translation of each verse
    numT = max number of verses in a group = number of translations
    """

    t = [[val] for val in t]
    N = len(M)
    groups = {} # keyed by supernode index
    iteration = 0
    max_iteration = N
    
    while iteration < max_iteration:
        iteration += 1
        #print "\t\tGrouping: iteration ",iteration

        i,j,P = find_best_couple(M, t)
        #print "\t\tbest couple: ",i,j,P

        # Stop iterating if similarity gets too low...
        if P < P_min:
            break;
        
        group = []
        
        # merge supernodes if they exist, else merge nodes:
        
        if i in groups:
            group.extend(groups[i])
        else:
            group.append(i)
        
        if j in groups:
            group.extend(groups[j])
        else:
            group.append(j)
        
        # group now contains all of the verses for the new supernode

        if len(group) > numT:
            # this grouping is invalid
            # prevent it from happening again by making P 0
            M[i][j] = 0
        else:
            # valid grouping. save it.

            # Remove the previous supernode groups
            if i in groups:
                del groups[i]

            if j in groups:
                del groups[j]

            # Create the supernode
            M = merge_nodes(M,i,j)
            t.append(t[i] + t[j])

            # Save the index of the new supernode
            supernode_index = len(M)-1
            groups[supernode_index] = group

        print "\r\t\t",len(groups),

    print

    return groups

def align(input_translations, input_filenames, output_filename):
    """
    Load one csv file for each translation
    Group, align and sort the verses
    Export a csv file containing a column for each translation
    """

    if len(input_translations) != len(input_filenames):
        raise ValueError("Number of translations and number of files must be the same")

    M = len(input_translations)

    # Load pre-translated data
    print "\tLoading data from files..."
    translations,books,chapters,verses,texts_original,texts_en = load_translated_verses(input_translations, input_filenames)

    # Calculate similarity between verses
    print "\tCalculating similarity matrix..."
    similarity = calculate_similarity(texts_en, translations)

    def canonical_group_cmp(a, b):
        """
        Define sort order for groups of verses
        """

        # find two verses from the same translation to compare their canonical order
        for i in a:
            for j in b:
                if translations[i] == translations[j]:
                    return i - j

    # Group the verses
    print "\tGrouping verses..."
    groups = group_verses(similarity, translations, 3).values()
    # print groups

    # Put groups back into canonical order
    print "\tSorting verses..."
    groups.sort(canonical_group_cmp)

    # prepare data for csv export
    print "\tPreparing csv data..."
    csv_rows = []
    csv_rows.append(input_translations) # headers

    for group in groups:

        # create a row in the csv file for every group
        if len(group) == M:
            # rows where all translations are present, are quick:
            group.sort()
            row = [u"{0}:{1}:{2}:{3}".format(books[verse],chapters[verse],verses[verse],texts_original[verse]) for verse in group]
        else:
            # for other rows, we have to find the missing translation, and substitute it with a blank
            row = []
            for translation in input_translations:
                found = False
                for verse in group:
                    if translation == translations[verse]:
                        # verse found for this translation
                        row.append(u"{0}:{1}:{2}:{3}".format(books[verse],chapters[verse],verses[verse],texts_original[verse]))
                        found = True
                        break
                if not found:
                    # fill in a blank
                    row.append("")

        csv_rows.append(row)

    # print csv_rows

    # Export to csv file
    print "\tWriting csv file..."
    with open(output_filename,'wb') as f:
        cw = unicodecsv.writer(f, encoding='utf-8')
        cw.writerows(csv_rows)

    print "\tDone!"

def translate_csv(in_filename, language, out_filename):
    """
    Load a bible book from csv file
    translate it
    save it as a new file
    """

    gs = goslate.Goslate(retry_times=100, timeout=100)

    books,chapters,verses,texts_original = load_verses(in_filename)

    if language != 'en':
        texts_translated = gs.translate(texts_original, 'en', language)
    else:
        texts_translated = texts_original

    rows = zip(books, chapters, verses, texts_original, texts_translated)

    # Write to CSV file
    with open(out_filename,'wb') as f:
        cw = unicodecsv.writer(f, encoding='utf-8')
        cw.writerow(['book','chapter','verse','text_original','text_english'])
        cw.writerows(rows)

