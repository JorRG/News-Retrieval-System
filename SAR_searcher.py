import sys
import pickle
from glob import glob
import re
import functools
from nltk.stem import SnowballStemmer
import itertools
stemmer = SnowballStemmer("spanish")
printf = functools.partial(print, end=" ")


def get_data(files):
    data = []
    for i in files:
        f=open(i,'r')
        f = f.read()
        data.append(f)
    return data

def extract_news(data):
    news = []
    for i in data:
        splited = i.split('<DOC>')
        splited.remove('')
        news.append(splited)
    return news

def index_news(data):
    fes = open('stopwords_es.txt','r')
    es = fes.read()
    news_indexed = {}
    for i in data:
        for j in i:
            posid = j.index('<DOCID>')
            posfinid=j.index('</DOCID>')
            docid = del_symbols(j[posid+len('<DOCID>'):posfinid],'')
            docid = docid.replace('EFE','')

            # Title extraction
            postitle = j.index('<TITLE>')
            posfintitle=j.index('</TITLE>')
            title = j[postitle+len('<TITLE>'):posfintitle]

            # Text Extraction
            postext = j.index('<TEXT>')
            posfintext = j.index('</TEXT>')
            text = j[postext+len('<TEXT>'):posfintext]

            news_indexed[docid] = [title,text]
    return news_indexed

def remove_stopwords(text,es):
    text = text.split()
    text =  [t for t in text if t not in es]
    text = ' '.join(text)
    return text

def search_results(var,dic,headdic,textdic,categorydic,datedic,corpus):
    inter = []
    url = './'+corpus+'/*.sgml'
    # Matching urls
    files = glob(url)
    # Data is a list containing the documents as strings
    data = get_data(files)
    data = extract_news(data)
    data = index_news(data)
    var = var.split()
    for i in var:
        if 'and'==i:
            ind = var.index(i)
            n = var[ind+1]
            if 'category:' in n:
                i = i.replace('category:','')
                if i in categorydic:
                    ocurrences = categorydic[n]
                    inter.append(list(set(ocurrences)))
            elif 'headline:' in n:
                i = i.replace('headline:','')
                if i in headdic:
                    ocurrences = headdic[n]
                    inter.append(list(set(ocurrences)))
            elif 'text:' in n:
                i = i.replace('text:','')
                if i in textdic:
                    ocurrences = textdic[n]
                    inter.append(list(set(ocurrences)))
            elif 'date:' in n:
                i = i.replace('date:','')
                if i in datedic:
                    ocurrences = datedic[n]
                    inter.append(list(set(ocurrences)))
            else:
                if n in dic:
                    ocurrences = dic[n]
                    inter.append(list(set(ocurrences)))
            pos = len(inter)
            inter[pos-1] = operador_and(inter[pos-2],inter[pos-1])

        elif 'or'==i:
            ind = var.index(i)
            n = var[ind+1]
            if 'category:' in n:
                i = i.replace('category:','')
                if i in categorydic:
                    ocurrences = categorydic[n]
                    inter.append(list(set(ocurrences)))
            elif 'headline:' in n:
                i = i.replace('headline:','')
                if i in headdic:
                    ocurrences = headdic[n]
                    inter.append(list(set(ocurrences)))
            elif 'text:' in n:
                i = i.replace('text:','')
                if i in textdic:
                    ocurrences = textdic[n]
                    inter.append(list(set(ocurrences)))
            elif 'date:' in n:
                i = i.replace('date:','')
                if i in datedic:
                    ocurrences = datedic[n]
                    inter.append(list(set(ocurrences)))
            else:
                if n in dic:
                    ocurrences = dic[n]
                    inter.append(list(set(ocurrences)))
            pos = len(inter)
            inter[pos-1] = operador_or(inter[pos-2],inter[pos-1])

        elif i=='not':
            ind = var.index(i)
            n = var[ind+1]
            if 'category:' in n:
                i = i.replace('category:','')
                if i not in categorydic:
                    ocurrences = categorydic[n]
                    inter.append(list(set(ocurrences)))
            elif 'headline:' in n:
                i = i.replace('headline:','')
                if i not in headdic:
                    ocurrences = headdic[n]
                    inter.append(list(set(ocurrences)))
            elif 'text:' in n:
                i = i.replace('text:','')
                if i not in textdic:
                    ocurrences = textdic[n]
                    inter.append(list(set(ocurrences)))
            elif 'date:' in n:
                i = i.replace('date:','')
                if i not in datedic:
                    ocurrences = datedic[n]
                    inter.append(list(set(ocurrences)))
            else:
                if n not in dic:
                    ocurrences = dic[n]
                    inter.append(list(set(ocurrences)))
            pos = len(inter)
            print(pos)
            var.pop(var.index(n))
            inter[pos-1] = operador_not(inter[pos-2],inter[pos-1])

        else:
            if 'category:' in i:
                i = i.replace('category:','')
                if i in categorydic:
                    ocurrences = categorydic[i]
                    inter.append(list(set(ocurrences)))
            elif 'headline:' in i:
                i = i.replace('headline:','')
                if i in headdic:
                    ocurrences = headdic[i]
                    inter.append(list(set(ocurrences)))
            elif 'text:' in i:
                i = i.replace('text:','')
                if i in textdic:
                    ocurrences = textdic[i]
                    inter.append(list(set(ocurrences)))
            elif 'date:' in i:
                i = i.replace('date:','')
                if i in datedic:
                    ocurrences = datedic[i]
                    inter.append(list(set(ocurrences)))
            else:
                if i in dic:
                    print(i)
                    ocurrences = dic[i]
                    inter.append(list(set(ocurrences)))
    if len(inter) == 0:
        print('News retrieved: 0')
        return 0

    show = constr_and(inter)
    filescont = list(set(get_files_containing(files,show,corpus)))
    print('Files :'+str(filescont))
    print('News retrieved: '+str(len(show)))
    print()
    info = show_info(show,data,var)
    return info

def operador_not(p1,p2):
    p1.sort()
    p2.sort()
    resp = []
    ip1 = 0
    ip2 = 0
    while ip1<len(p1) and ip2<len(p2):
        if p1[ip1] == p2[ip2]:
            #resp.append(p1[ip1])
            ip1+=1
            ip2+=1
        elif p1[ip1] < p2[ip2]:
            resp.append(p1[ip1])
            ip1+=1
        else:
            ip2+=1
    return resp

def constr_and(inter):
    aux = inter
    tam = len(inter)
    if tam == 1:
        aux[0] = inter[0]
    while tam>1:
        op1 = aux[0]
        op2 = aux[1]
        aux[1] = operador_and(op1,op2)
        aux.pop(0)
        tam-=1
    return aux[0]

def search_results_stemmed(var,dic,headdic,textdic,categorydic,datedic,corpus):
    inter = []
    pals = []
    url = './'+corpus+'/*.sgml'
    # Matching urls
    files = glob(url)
    # Data is a list containing the documents as strings
    data = get_data(files)
    data = extract_news(data)
    data = index_news(data)

    var = var.split()
    for i in var:
        if 'category:' in i:
            i = i.replace('category:','')
            ste = stemmer.stem(i)
            try:
                p = dicstem[ste]
                for j in p:
                    if j in categorydic:
                        ocurrences = categorydic[i]
                        inter.append(list(set(ocurrences)))
            except Exception as e:
                pass

        elif 'headline:' in i:
            i = i.replace('headline:','')
            ste = stemmer.stem(i)
            try:
                p = dicstem[ste]
                for j in p:
                    if j in headdic:
                        ocurrences = headdic[i]
                        inter.append(list(set(ocurrences)))
            except Exception as e:
                pass
        elif 'text:' in i:
            i = i.replace('text:','')
            ste = stemmer.stem(i)
            try:
                p = dicstem[ste]
                for j in p:
                    if j in textdic:
                        ocurrences = textdic[i]
                        inter.append(list(set(ocurrences)))
            except Exception as e:
                raise

        elif 'date:' in i:
            i = i.replace('date:','')
            ste = stemmer.stem(i)
            try:
                p = dicstem[ste]
                for j in p:
                    if j in datedic:
                        ocurrences = datedic[i]
                        inter.append(list(set(ocurrences)))
            except Exception as e:
                raise

        else:
            ste = stemmer.stem(i)
            p = dicstem[ste]
            for j in p:
                pals.append(j)

    for x in pals:
        if x in dic:
            ocurrences = dic[x]
            inter.append(list(set(ocurrences)))
    if len(inter) == 0:
        print('News retrieved: 0')
        return 0
    aux = list(inter)
    l = len(inter)-1
    if l == 0:
        aux[0] = inter[0]
    else:
        while l>0:
            op1 = aux[0]
            print('op1 :'+str(op1))
            op2 = aux[1]
            print('op2 :'+str(op2))

            aux[1] = operador_and(op1,op2)
            aux.pop(0)
            l-=1

    print('Files :'+str(list(set(get_files_containing(files,aux[0],corpus)))))
    print('News retrieved: '+str(len(aux[0])))
    print()

    info = show_info(aux[0],data,var)
    return info

def operador_and(p1,p2):
    p1.sort()
    p2.sort()
    resp = []
    ip1 = 0
    ip2 = 0
    while ip1<len(p1) and ip2<len(p2):
        if p1[ip1] == p2[ip2]:
            resp.append(p1[ip1])
            ip1+=1
            ip2+=1
        elif p1[ip1] < p2[ip2]:
            ip1+=1
        else:
            ip2+=1
    return resp

def operador_or(p1,p2):
    resp = []
    resp.append(p1)
    resp.append(p2)
    resp = list(itertools.chain(*resp))
    resp = list(set(resp))
    resp.sort()
    return resp



def get_files_containing(files,docids,corpus):
    f = []
    for i in docids:
        if len(f)==len(docids):
            break
        else:
            i=i[:8]
            doc=int(i)
            f.append('/'+corpus+'/'+str(doc)+'.sgml')
    return f


def show_info(docids,data,var):
    numresults = len(docids)
    docids = sort_docs(docids,var,data)
    if numresults<3:
        info = show_text_title(docids,data)
    elif numresults>=3 and numresults<=5:
        info = show_title_snippet(docids, data,var)
    else:
        info = show_ten_titles(docids,data)
    return info

def sort_docs(docids,query,data):
    scores = []
    lengths = []
    for i in docids:
        wtq=0
        wtd=0
        documento = ''
        lengths.append(len(i))
        doc = data[i]
        for x in doc:
            documento+=x
        documento = documento.lower()
        documento = del_symbols(documento,' ')
        documento = documento.split()
        for j in query:
            wtq += query.count(j)
            wtd += documento.count(j)
        scores.append(wtq*wtd)
    for s,l in list(zip(scores,lengths)):
        ind = scores.index(s)
        print(type(s))
        scores[ind] = s/l
    return [docids for (scores,docids) in sorted(zip(scores,docids),reverse=True)]

def del_symbols(data,spacing):
    mi_er = re.compile("\W+")
    sentence = mi_er.sub(spacing, data)
    return sentence

def show_text_title(docids, data):
    info = []
    for i in docids:
        info.append(data[i])
    for i in info:
        for j in i:
            print(j)


def show_title_snippet(docids, data,var):
    info = []
    for i in docids:
        info.append(data[i])
    for i in info:
        print(i[0])
        get_snippets(i[1],i[0],5,var)
        print()

def get_snippets(text,title,surrounders,word):
    text=del_symbols(text,' ').lower()
    title=del_symbols(title,' ').lower()
    text=text+title
    text=text.split()
    for i in word:
        pos = text.index(i)
        snip = text[pos-surrounders:pos+surrounders+1]
        for i in snip:
            printf(i)
        print()


def show_ten_titles(docids,data):
    info = []
    for i in docids:
        info.append(data[i])

    info = info[:10]
    for i in info:
        print(i[0])

if __name__=="__main__":
    if len(sys.argv) > 1:
        # Dictionary load from file given
        obj = pickle.load(open(sys.argv[1],"rb"))
        dic=obj[0]
        corpus = obj[5]
        headdic = obj[1]
        textdic = obj[2]
        categorydic = obj[3]
        datedic = obj[4]
        if len(obj)==6:
            print('\nSAR News Searcher')
            print('-------------------------------------------------------------\n')
            print('Welcome to SAR News Search Engine,')
            var = input('Please introduce your search: ')
            while True:
                if not var:
                    print("You've finished the app, see you again!")
                    break
                else:
                    var = str(var).lower()
                    print('\033[1m'+'Results: '+'\n'+'\033[0m')
                    search_results(var,dic,headdic,textdic,categorydic,datedic,corpus)
                    var = input('Introduce another search or press Enter to exit: ')
        if len(obj)==7:
            dicstem = obj[6]
            print('\nSAR News Searcher')
            print('-------------------------------------------------------------\n')
            print('Welcome to SAR News Search Engine,')
            print('You are using our "Stemming" version')
            var = input('Please introduce your search: ')
            while True:
                if not var:
                    print("You've finished the app, see you again!")
                    break
                else:
                    var = str(var).lower()
                    print('\033[1m'+'Results: '+'\n'+'\033[0m')
                    search_results_stemmed(var,dic,headdic,textdic,categorydic,datedic,corpus)
                    var = input('Introduce another search or press Enter to exit: ')
