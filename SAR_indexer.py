import sys
from glob import glob
import re
import pickle
from nltk.stem import SnowballStemmer

stemmer = SnowballStemmer('spanish')

# This method reads the files matching the URL pattern provided
def get_data(files):
    data = []
    for i in files:
        f=open(i,'r')
        f = f.read()
        data.append(f)
    return data

# This method deletes any non alpha-numerical character
def del_symbols(data,spacing):
    mi_er = re.compile("\W+")
    sentence = mi_er.sub(spacing, data)
    return sentence

# This method parses the documents and splits them into the different news
def extract_news(data):
    news = []
    for i in data:
        splited = i.split('<DOC>')
        splited.remove('')
        news.append(splited)
    return news

def extract_voc_head(data):
    headdic = {}
    for i in data:
        for j in i:
            # j -> news in document i
            # Document ID extraction
            posid = j.index('<DOCID>')
            posfinid=j.index('</DOCID>')
            docid = del_symbols(j[posid+len('<DOCID>'):posfinid],'')
            docid = docid.replace('EFE','')

            # Title extraction
            postitle = j.index('<TITLE>')
            posfintitle=j.index('</TITLE>')
            title = del_symbols(j[postitle+len('<TITLE>'):posfintitle], ' ')
            title = title.lower()

            headdic = extract_terms_mod(headdic,docid,title)
    return headdic

def extract_voc_text(data):
    dictext = {}
    for i in data:
        for j in i:
            # j -> news in document i
            # Document ID extraction
            posid = j.index('<DOCID>')
            posfinid=j.index('</DOCID>')
            docid = del_symbols(j[posid+len('<DOCID>'):posfinid],'')
            docid = docid.replace('EFE','')

            # Title extraction
            postext = j.index('<TEXT>')
            posfintext = j.index('</TEXT>')
            text = del_symbols(j[postext+len('<TEXT>'):posfintext],' ')
            text = text.lower()

            dictext = extract_terms_mod(dictext,docid,text)
    return dictext

def extract_voc_category(data):
    diccategory = {}
    for i in data:
        for j in i:
            # j -> news in document i
            # Document ID extraction
            posid = j.index('<DOCID>')
            posfinid=j.index('</DOCID>')
            docid = del_symbols(j[posid+len('<DOCID>'):posfinid],'')
            docid = docid.replace('EFE','')

            # Title extraction
            postext = j.index('<CATEGORY>')
            posfintext = j.index('</CATEGORY>')
            text = del_symbols(j[postext+len('<CATEGORY>'):posfintext],' ')
            text = text.lower()

            diccategory = extract_terms_mod(diccategory,docid,text)
    return diccategory

def extract_voc_date(data):
    dicdate = {}
    for i in data:
        for j in i:
            # j -> news in document i
            # Document ID extraction
            posid = j.index('<DOCID>')
            posfinid=j.index('</DOCID>')
            docid = del_symbols(j[posid+len('<DOCID>'):posfinid],'')
            docid = docid.replace('EFE','')

            # Title extraction
            postext = j.index('<DATE>')
            posfintext = j.index('</DATE>')
            text = del_symbols(j[postext+len('<DATE>'):posfintext],' ')
            text = text.lower()

            dicdate = extract_terms_mod(dicdate,docid,text)
    return dicdate


# This method extracts the desired fields in the documents
# such as the document ID, Title and text.
def extract_voc(data):
    dic = {}
    for i in data:
        for j in i:
            # j -> news in document i
            # Document ID extraction
            posid = j.index('<DOCID>')
            posfinid=j.index('</DOCID>')
            docid = del_symbols(j[posid+len('<DOCID>'):posfinid],'')
            docid = docid.replace('EFE','')

            # Title extraction
            postitle = j.index('<TITLE>')
            posfintitle=j.index('</TITLE>')
            title = del_symbols(j[postitle+len('<TITLE>'):posfintitle], ' ')
            title = title.lower()

            # Text Extraction
            postext = j.index('<TEXT>')
            posfintext = j.index('</TEXT>')
            text = del_symbols(j[postext+len('<TEXT>'):posfintext],' ')
            text = text.lower()

            # Call to vocabulary builder method
            dic = extract_terms(dic,docid,title,text)
    return dic

# This method extracts the desired fields in the documents
# such as the document ID, Title and text.
def extract_voc_stopwords(data):
    fes = open('stopwords_es.txt','r')
    es = fes.read()
    dic = {}
    for i in data:
        for j in i:
            # j -> news in document i
            # Document ID extraction
            posid = j.index('<DOCID>')
            posfinid=j.index('</DOCID>')
            docid = del_symbols(j[posid+len('<DOCID>'):posfinid],'')
            docid = docid.replace('EFE','')

            # Title extraction
            postitle = j.index('<TITLE>')
            posfintitle=j.index('</TITLE>')
            title = del_symbols(j[postitle+len('<TITLE>'):posfintitle], ' ')
            title = title.lower()
            title = remove_stopwords(title,es)

            # Text Extraction
            postext = j.index('<TEXT>')
            posfintext = j.index('</TEXT>')
            text = del_symbols(j[postext+len('<TEXT>'):posfintext],' ')
            text = text.lower()
            text = remove_stopwords(text,es)
            # Call to vocabulary builder method
            dic = extract_terms(dic,docid,title,text)
    return dic

def extract_terms_mod(dic,docid,text):

    # Splitting title and text per term
    text = text.split()

    # Adding each element in title and text to the dictionary
    for i in text:
        if i not in dic:
            dic[i] = {str(docid):1}
        else:
            posting = dic[i]
            if docid in posting:
                dic[i][docid]+=1
            else:
                dic[i][docid]=1
    return dic

def remove_stopwords(text,es):
    text = text.split()
    text =  [t for t in text if t not in es]
    text = ' '.join(text)
    return text


# This method adds the elements to the vocabulary. It is called from
# extract_voc(data)
def extract_terms(dic, docid, title, text):

    # Splitting title and text per term
    title = title.split()
    text = text.split()

    # Adding each element in title and text to the dictionary
    for i in title:
        if i not in dic:
            dic[i] = {str(docid):1}
        else:
            posting = dic[i]
            if docid in posting:
                dic[i][docid]+=1
            else:
                dic[i][docid]=1

    for i in text:
        if i not in dic:
            dic[i] = {str(docid):1}
        else:
            posting = dic[i]
            if docid in posting:
                dic[i][docid]+=1
            else:
                dic[i][docid]=1

    return dic

if __name__=="__main__":
    if len(sys.argv) > 2:
        # Files directory URL construction
        url = './'+sys.argv[1]+'/*.sgml'
        # Matching urls
        files = glob(url)
        # Data is a list containing the documents as strings
        data = get_data(files)
        # Extracting the news for each file
        data_news = extract_news(data)
        # Call to dictionary extraction
        if len(sys.argv)>3:
            if sys.argv[4] == 'True':
                dicc = extract_voc(data_news)
                headdic = extract_voc_head(data_news)
                textdic = extract_voc_text(data_news)
                categorydic = extract_voc_category(data_news)
                datedic = extract_voc_date(data_news)
            else:
                dicc = extract_voc(data_news)
                headdic = extract_voc_head(data_news)
                textdic = extract_voc_text(data_news)
                categorydic = extract_voc_category(data_news)
                datedic = extract_voc_date(data_news)
        else:
            dicc = extract_voc(data_news)
            headdic = extract_voc_head(data_news)
            textdic = extract_voc_text(data_news)
            categorydic = extract_voc_category(data_news)
            datedic = extract_voc_date(data_news)

        if sys.argv[3] == 'True':
            dicstem={}
            for i in list(dicc.keys()):
                stemmed = stemmer.stem(i)
                if stemmed not in dicstem:
                    dicstem[stemmed] = [i]
                else:
                    post = dicstem[stemmed]
                    if i not in post:
                        dicstem[stemmed].append(i)
            pickle.dump((dicc,headdic,textdic,categorydic,datedic,sys.argv[1],dicstem),open(sys.argv[2],"wb"))

        # Save dictionary to the file given
        #
        # Notes: .p extension is preferable
        else:
            pickle.dump((dicc,headdic,textdic,categorydic,datedic,sys.argv[1]),open(sys.argv[2],"wb"))
