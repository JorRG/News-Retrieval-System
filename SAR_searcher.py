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
    for i in var:
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

def search_results_bool(var,dic,headdic,textdic,categorydic,datedic,corpus):
    inter = []
    url = './'+corpus+'/*.sgml'
    # Matching urls
    files = glob(url)
    # Data is a list containing the documents as strings
    data = get_data(files)
    data = extract_news(data)
    data = index_news(data)
    aux = []


    for i in var:
        if 'and' != i and 'or'!=i and 'not'!=i:
            if 'category:' in i:
                i = i.replace('category:','')
                if i in categorydic:
                    ocurrences = categorydic[i]
                    aux.append(list(set(ocurrences)))
            elif 'headline:' in i:
                i = i.replace('headline:','')
                if i in headdic:
                    ocurrences = headdic[i]
                    aux.append(list(set(ocurrences)))
            elif 'text:' in i:
                i = i.replace('text:','')
                if i in textdic:
                    ocurrences = textdic[i]
                    aux.append(list(set(ocurrences)))
            elif 'date:' in i:
                i = i.replace('date:','')
                if i in datedic:
                    ocurrences = datedic[i]
                    aux.append(list(set(ocurrences)))
            else:
                if i in dic:
                    ocurrences = dic[i]
                    aux.append(list(set(ocurrences)))
        else:
            aux.append(i)

        resaux = []

        for a in range(0,len(aux)-1):
            if aux[a]=='and':
                if resaux==[]:
                    resaux = operador_and(aux[a-1],aux[a+1])
                else:
                    resaux = operador_and(resaux,aux[a+1])
            if aux[a]=='or':
                if resaux==[]:
                    resaux = operador_or(aux[a-1],aux[a+1])
                else:
                    resaux = operador_or(resaux,aux[a+1])

        print(len(resaux))

"""
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
    """

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
    return list(set(aux[0]))

def constr_or(inter):
    aux = list(inter)
    tam = len(aux)
    if tam == 1:
        return aux[0]
    while tam>1:
        op1 = aux[0]
        op2 = aux[1]
        aux[1] = operador_or(op1,op2)
        aux.pop(0)
        tam-=1
    return list(set(aux[0]))

def search_results_stemmed(var,dic,headdic,textdic,categorydic,datedic,corpus):

    pals = []
    url = './'+corpus+'/*.sgml'
    # Matching urls
    files = glob(url)
    # Data is a list containing the documents as strings
    data = get_data(files)
    data = extract_news(data)
    data = index_news(data)
    ands = []
    for i in var:
        inter = []
        for j in i:
            if j in dic:
                ocurrences = dic[j]
                inter.append(list(set(ocurrences)))
        ands.append(list(set(constr_or(inter))))

    if(ands)==[]:
        print('News retrieved: 0')
        return 0
    else:
        show = constr_and(ands)
        filescont = list(set(get_files_containing(files,show,corpus)))
        print('Files :'+str(filescont))
        print('News retrieved: '+str(len(show)))
        print()
        info = show_info(show,data,var)
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

#This method sorts the docs retrieved based on its relevance
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


def show_title_snippet(docids,data,var):
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
        fes = open('stopwords_es.txt','r')
        es = fes.read()
        obj = pickle.load(open(sys.argv[1],"rb"))
        dic=obj[0]
        corpus = obj[5]
        headdic = obj[1]
        textdic = obj[2]
        categorydic = obj[3]
        datedic = obj[4]
        if len(obj)==7:
            print('\nSAR News Searcher')
            print('-------------------------------------------------------------\n')
            print('Welcome to SAR News Search Engine,')
            var = input('Please introduce your search: ')
            while True:
                if not var:
                    print("You've finished the app, see you again!")
                    break
                else:
                    stop = obj[6]
                    var = str(var).lower()
                    var = var.split()
                    if stop == 'True':
                        for s in var:
                            if s in es:
                                var.remove(s)
                    if 'and' in var or 'or' in var or 'not' in var:
                        search_results_bool(var,dic,headdic,textdic,categorydic,datedic,corpus)
                    print('\033[1m'+'Results: '+'\n'+'\033[0m')
                    search_results(var,dic,headdic,textdic,categorydic,datedic,corpus)
                    var = input('Introduce another search or press Enter to exit: ')
        if len(obj)==8:
            dicstem = obj[6]
            stop = obj[7]
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
                    var = var.split()
                    if stop == 'True':
                        for s in var:
                            if s in es:
                                var.remove(s)

                    laux = []
                    for i in var:
                        ste = stemmer.stem(i)
                        if ste in dicstem:
                            oc = dicstem[ste]
                            laux.append(oc)
                    print(var)
                    if 'and' in var or 'or' in var or 'not' in var:
                        search_results_bool(var,dic,headdic,textdic,categorydic,datedic,corpus)
                    print('\033[1m'+'Results: '+'\n'+'\033[0m')
                    search_results_stemmed(laux,dic,headdic,textdic,categorydic,datedic,corpus)
                    var = input('Introduce another search or press Enter to exit: ')
