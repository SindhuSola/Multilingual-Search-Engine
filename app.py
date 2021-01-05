from flask import Flask, render_template, url_for, redirect, request
from google_trans_new import google_translator
import lxml.html
import json
import urllib.request
from newsapi import NewsApiClient
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import pandas as pd
analyser = SentimentIntensityAnalyzer()
app = Flask(__name__)
app.config['SECRET_KEY'] = 'scret'

translator = google_translator()
n=0
a=""
def solr12(a, poi, country, lang):
    countrywise={}
    poi_count={}
    num_found=0
    print("inside "+a +poi +country+ lang)
    aa = urllib.parse.quote(a)
    inurl="http://3.85.175.201:8983/solr/gettingstarted/select?fl=country%2C%20user.verified%2C%20poi_name%2C%20lang%2C%20user.screen_name%2C%20full_text%2C%20processed_text&q=full_text%3A%22"+aa+"%22%20AND%20country%3A%20%22"+country+"%22%20AND%20poi_name%3A%20%22"+poi+"%22%20AND%20lang%3A%20%22"+lang+"%22&rows=50&sort=influencer_score%20desc"
    print(inurl)
    data = urllib.request.urlopen(inurl)
    docu = json.load(data)['response']
    num_found=docu['numFound']
    docs=docu['docs']
    if(num_found!=0):
        docs1 = json.dumps(docs)
        docs1 = docs1.replace("['", '"')
        docs1 = docs1.replace("']", '"')
        docs1 = docs1.replace('["', '"')
        docs1 = docs1.replace('"]', '"')
        docs1 = docs1.replace('[false]', 'false')
        docs1 = docs1.replace('[true]', 'true')
        json_docs = json.loads(docs1)
        data_frame = pd.DataFrame(json_docs)
        print(data_frame.info())
        countrywise = {"Countries": [{"country": "India", "total_count": str(
            (data_frame['country'] == 'INDIA').sum() + (data_frame['country'] == 'India').sum())},
                                     {"country": "USA", "total_count": str((data_frame['country'] == 'USA').sum())},
                                     {"country": "Italy", "total_count": str((data_frame['country'] == 'ITALY').sum() + (
                                                 data_frame['country'] == 'Italy').sum())}]}

        poi_count = {"non_poi": str((data_frame['user.verified']== False).sum()), "poi": str((data_frame['user.verified']==True).sum())}

    list1=[]
    i=0
    for doc in docs:
       if(i<7):
           if "processed_text" in doc:
                ptext=doc["processed_text"]
                if(doc["lang"][0]!="en"):
                    new_text=translator.translate(ptext[0])
                    #print(new_text)
                else:
                    new_text=ptext[0]
                score = analyser.polarity_scores(new_text)
                print("score")
                doc["polarity"] = score["compound"]
                list1.append(doc)
                i+=1

    return list1, countrywise, poi_count, num_found

def news(a,poi, country, lang):
    print("a value news"+a)
    dict_c = {"India": "in", "Italy": "it", "USA": "us", "": ""}
    dict_l = {"hi": "", "it": "it", "en": "en", "": ""}
    dict_language={"it":"Italy","en":"USA","hi":"India","":""}
    dict_poi = {"narendramodi": "Narendra Modi", "SrBachchan": "Amitab Bachchan",
                "DrRPNishank": "Dr. Ramesh Pokhriyal Nishank",
                "BernieSanders": "Bernie Sanders", "JoeBiden": "Joe Biden", "NYGovCuomo": "Andrew Cuomo",
                "juventusfc": "JuventusFC",
                "matteorenzi": "Matteo Renzi", "matteosalvinimi": "Matteo Salvini", "AmitShah": "Amit Shah",
                "CDCgov": "CDC",
                "KamalaHarris": "Kamala Harris", "PiyushGoyal": "Piyush Goyal", "GiorgiaMeloni": "Giorgia Meloni",
                "matteosalvinimi": "Matteo Salvinimi", "ewarren": "Elizabeth Warren",
                "realDonaldTrump": "Donald J. Trump",
                "ArvindKejriwal": "Arvind Kejriwal", "RahulGandhi": "Rahul Gandhi", "": ""}
    poi_name = dict_poi[poi]
    language = dict_l[lang]
    coun = dict_c[country]
    print(poi_name + country + language)
    newsapi = NewsApiClient("ea6895c26d0e4c4e9f3d163373114089")
    if(a=="" and poi_name=="" and lang!= "" and coun==""):
        everything = newsapi.get_everything(q=coun+ " " + dict_language[lang],page_size=7)
    elif (a == "" and poi_name == "" and coun != "" and language==""):
        everything = newsapi.get_top_headlines(q=coun + " " + dict_language[lang], country=coun, page_size=7)
    elif (coun != "" and language == "" and poi_name == ""):
        print("country!="" and language==""" and poi == "")
        everything = newsapi.get_top_headlines(q=a, country=coun, page_size=7)
    elif (language != "" and coun != "" and poi_name == ""):
        everything = newsapi.get_top_headlines(q=a, language=language, country=coun, page_size=7)
    elif (language != "" and coun == "" and poi_name == ""):
        everything = newsapi.get_everything(q=a, language=language, page_size=7)
    elif (language != "" and coun == "" and poi_name!=""):
        everything = newsapi.get_everything(q=a+" " + poi_name, language=language, page_size=7)
    elif (coun != "" and language == "" and poi_name != ""):
        print("country!="" and language=="" and poi != """)
        everything = newsapi.get_everything(q=a+" " + poi_name + " " + coun, page_size=7)
    elif (language != "" and coun != "" and poi_name != ""):
        everything = newsapi.get_top_headlines(q=a+" " + poi_name + " " + coun, language=language, country=coun,
                                            page_size=7)
    else:
        print("else")
        everything = newsapi.get_everything(q=a+" " + poi_name, page_size=7)

    articles=[]
    articles = everything['articles']
    desc = []
    news = []
    url = []
    mylist = []
    myarticles=[]
    for i in range(len(articles)):
        myarticles = [articles[i]]
        myarticles[0]["desc"]= lxml.html.fromstring(myarticles[0]["description"]).text
        mylist.append(myarticles[0])

    return mylist

with open('covid_counts/POIs_India.json', encoding='utf8') as fp:
    data_india = fp.read()
fp.close()
with open('covid_counts/POIs_Italy.json', encoding='utf8') as fp:
    data_italy = fp.read()
fp.close()
with open('covid_counts/POIs_USA.json', encoding='utf8') as fp:
    data_usa = fp.read()
fp.close()
with open('Tweet_Counts.json', encoding='utf8') as fp:
    tweet_count = fp.read()
fp.close()

with open('covid_counts/convertcsv.json', encoding='utf8') as fp:
    total_poi_counts = fp.read()
fp.close()
with open('covid_counts/lang_count.json', encoding='utf8') as fp:
    total_lang_counts = fp.read()
fp.close()
datap = json.loads(data_india)
datap1 = json.loads(data_italy)
datap2 = json.loads(data_usa)
count_json = json.loads(tweet_count)
total_poi_counts =json.loads(total_poi_counts)
total_lang_counts =json.loads(total_lang_counts)

@app.route('/Analytics')
def index():
    return render_template("Analytics.html",india=datap,italy=datap1,usa=datap2,
    total=count_json,total_poi_counts=total_poi_counts,total_lang_counts=total_lang_counts)

@app.route('/', methods=['GET','POST'])
def form():
    list1=[]
    mylist=[]
    num_found=0
    a=""
    poi=""
    country=""
    lang=""
    country_data={}
    poicount={}
    n=0
    if request.method=="POST":
        if request.form["action"]=='Submit':
                a = request.form["item"]
                poi=request.form["poi"]
                country=request.form["country"]
                lang = request.form["language"]
                list1,country_data, poicount, num_found=solr12(a, poi, country, lang)
                n=len(list1)
                if(a=="" and poi=="" and country=="" and lang==""):
                    mylist=[]
                else:
                    mylist=news(a,poi, country, lang)
    return render_template('form.html', word=a, poiname=poi, countr=country, langu=lang, n=n, list1=list1, mylist=mylist, country_data=country_data, poicount=poicount, nt=num_found, form=form)


if __name__ == '__main__':
    app.run(debug=True)