import json
import urllib.request as urlreq
import urllib.error as urlerr
import re
import random


api_url = "http://api.intellexer.com/analyzeSentiments?apikey=a14cbdea-9f79-4c87-b2d2-8e4fa8fe78c2"




# print response results
def sentiment_extract(response):
    #print("Sentences with sentiment objects and phrases:")
    sentences = response.get('sentences')
    good=0
    bad=0
    neutral=0
    mean=0
    lst=[]
    for sent in sentences:
        if sent.get('w')==0:
            neutral+=1
        elif sent.get('w')>0:
            good+=1
        else:
            bad+=1
        mean+=sent.get('w')
        cleanText=''.join(re.split(r"<.*?>",sent.get('text')))
        lst.append((sent.get('w'),cleanText))
        #print("Sentence Weight = ", sent.get('w'), "\t", cleanText , )
    return lst

# create request to the Sentiment Analyzer API service
def request_Sentiment(url, data):
    header = {'Content-Type': "application/json"}
    # req=urlreq.
    req = urlreq.Request(url,data,header)
    conn = urlreq.urlopen(req)
    try:
        json_response = json.loads(conn.read())
    finally:
        conn.close()
    return sentiment_extract(json_response)



# my token = 2133aca8852d1acf93449dfb13a1fc7e1c801d32
#my key = c1c1a98450601bca40a5060186505c8a
def movieRequestToken():
    header = {'Content-Type': "application/json"}
    req=urlreq.Request(r"https://api.themoviedb.org/3/authentication/token/new?api_key=c1c1a98450601bca40a5060186505c8a",None,header)
    conn=urlreq.urlopen(req)
    try:
        data=conn.read()
    except:
        pass
        #print(data)
    finally:
        conn.close()
    print(data)

def ChooseGenre(genreName):
    header = {'Content-Type': "application/json"}
    req = urlreq.Request(
        r"https://api.themoviedb.org/3/genre/movie/list?api_key=c1c1a98450601bca40a5060186505c8a&language=en-US", None, header)
    conn = urlreq.urlopen(req)
    try:
        data = json.loads(conn.read())
    except:
        return False
        # print(data)
    finally:
        conn.close()
    for genreDict in data['genres']:
        if genreDict['name'].lower()==genreName.lower():
            return genreDict['id']
    return "35"


    #print(data)

def GetMovies(genre):
    genreId=ChooseGenre(genre)
    header = {'Content-Type': "application/json"}
    url=r"https://api.themoviedb.org/3/discover/movie?api_key=c1c1a98450601bca40a5060186505c8a&language=en-US" \
        r"&sort_by=rating.desc&include_adult=false&with_genres="+str(genreId)+"&page="+str(random.randint(1,11))
    req = urlreq.Request(url, None, header)
    conn = urlreq.urlopen(req)
    try:
        data = json.loads(conn.read())
    except:
        return False
        # print(data)
    finally:
        conn.close()
    movieList=[]
    for movieDict in data['results']:
        #print(movieDict)
        movieList.append((movieDict['id'],movieDict['title']))
        #print(movieDict['id'],movieDict['title'])
    return movieList
    #print(data)

def GetVideos(movieName):
    header = {'Content-Type': "application/json"}
    movieName=movieName.split(' ')
    movieName='+'.join(movieName)
    url=r"https://www.googleapis.com/youtube/v3/search?" \
        r"part=snippet&q="+movieName+"+Trailer&type=video&maxResults=3&key=AIzaSyCgNfFK0x5uU41lGR45MmS-5ZZ2fMaxhjQ"
    req = urlreq.Request(url, None, header)
    conn = urlreq.urlopen(req)
    try:
        data = json.loads(conn.read())
    except:
        return False
        # print(data)
    finally:
        conn.close()
    # for movieDict in data['results']:
    #     print(movieDict['id'],movieDict['title'])
    lst=[]
    for video in data['items']:
        lst.append((video['id']['videoId'],video['snippet']['title']))
        #print( ("https://www.youtube.com/watch?v="+video['id']['videoId']) , video['snippet']['title'])
        #for option in video:
            #print(option,video[option])
    return lst
    #print

def GetComments(videoId):
    header = {'Content-Type': "application/json"}
    url=r"https://www.googleapis.com/youtube/v3/commentThreads?" \
        r"part=snippet&videoId="+videoId+"&textFormat=plaintext&key=AIzaSyCgNfFK0x5uU41lGR45MmS-5ZZ2fMaxhjQ"
    req = urlreq.Request(url, None, header)
    conn = urlreq.urlopen(req)
    try:
        data = json.loads(conn.read())
    except:
        return False
        # print(data)
    finally:
        conn.close()
    commentsLst=[]
    for i in data['items']:
        commentsLst.append(i['snippet']['topLevelComment']['snippet']['textDisplay'])
        #print(i['snippet']['topLevelComment']['snippet']['textDisplay'])
        #for j in i['snippet']['topLevelComment']:
            # print(j)
        #print(i['snippet'])
    return commentsLst
    #print(data['items'])

#nyt reviews 2f639c9ff1f24ac2a660cd1841c24ce9

def GetReview(movieName):
    movieName=movieName.split(' ')
    movieName='+'.join(movieName)
    header = {'Content-Type': "application/json"}
    url=r"https://api.nytimes.com/svc/movies/v2/reviews/search.json?api-key=2f639c9ff1f24ac2a660cd1841c24ce9&query="\
        +movieName
    req = urlreq.Request(url,None, header)
    conn = urlreq.urlopen(req)

    try:
        data = json.loads(conn.read())
    except Exception as error:
            return "No review"
        # print(data)
    finally:
        conn.close()
    if len(data['results'])>0:
        asked=data['results'][0]

        #print(asked['display_title'])
        header = {'Content-Type': "application/json"}
        req = urlreq.Request(asked['link']['url'])
        conn = urlreq.urlopen(req)

        try:
            data = conn.read().decode("utf-8")
        except Exception as error:
            print('HTTP error - %s' % error.read())
            exit()
        finally:
            conn.close()
        review=re.findall(r'<p class="story-body-text story-content".*?>(.*?)</p>',data)
        #print(review)
        return review
    else:
        print("No review")
        return "No review"

def processReview(review):
    dictReview = []
    index = 1
    #print(len(review))
    for paragr in review:
        dictReview.append({'id': ('snt' + str(index)),
                           'text': paragr})
        index += 1
    json.dump(dictReview,open("review.json","w"),indent=2)
    json_review = open("review.json", "rb")
    #print(json_review)

    respone = request_Sentiment(api_url, json_review)
    #respone = sorted(respone, key=lambda x: x[0] > 0)
    return respone

#GetMovies("drama")
print(GetVideos("Gone Baby Gone"))
print(GetComments("itPTyd3DkEw"))
#review=getReview("Gone Baby Gone")

#print(respone)

