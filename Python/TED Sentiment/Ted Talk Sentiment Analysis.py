
# coding: utf-8

# In[1]:

import urllib2
import lxml.html
from lxml.cssselect import CSSSelector
from textblob import TextBlob
import matplotlib.pyplot as plt
import requests
import pandas as pd
import numpy as np


# In[ ]:

# Talk gallery
# prefix
talkList = 'http://www.ted.com/talks?page='

# suffix
suffixPop = '&sort=popular'


# In[54]:

def transcriptLinks(pageURL):
    r = requests.get(pageURL)
    tree = lxml.html.fromstring(r.text)
    # CSS Selector for talk title names
    sel = CSSSelector('#browse-results .m5 a')
    # Apply the selector to the DOM tree.
    results = sel(tree)
    # get the titles from all of the results
    titles = [result.text.replace('\n','') for result in results]
    
    # Durations
    durationSel = CSSSelector('.thumb__duration')
    durations = [time.text for time in durationSel(tree)]
    
    # Speakers
    # speakerSel = CSSSelector('.talk-link__speaker')
    # speakers = [name.text.decode("utf-8") for name in speakerSel(tree)] # need to convert to uni for special characters
    
    # TED Talk transcript page
    # prefix
    transBase = 'http://www.ted.com'
    # suffix (english)
    suffixTrans = '/transcript?language=en'
    transLinks = [transBase + entry.get('href') + suffixTrans for entry in results]
    
    return pd.DataFrame({'Title': titles, 'Duration': durations, 'Transcript URL': transLinks})


# In[66]:

page1Trans = transcriptLinks('http://www.ted.com/talks?page=1&sort=popular')


# http://vverma.net/scrape-the-web-using-css-selectors-in-python.html

# In[57]:

def LoadTrans(link):
    print 'Fetching: ' + link

    getTrans = requests.get(link)
    treeTrans = lxml.html.fromstring(getTrans.text)

    # CSS Selector for talk title names
    sel = CSSSelector('.talk-transcript__fragment , .talk-transcript__para:nth-child(1) .talk-transcript__para__text')
    
    # Apply the selector to the DOM tree.
    talkTrans = sel(treeTrans)

    # get the text out of all the results
    transcript = [phrase.text for phrase in talkTrans]
    transcript = ' '.join(transcript)
    
    # Clean laughter and applause
    transcript = transcript.replace('(Laughter)', '')
    transcript = transcript.replace('(Applause)', '')

    # Clean carriage returns and escape characters
    transcript = transcript.replace('\n', ' ')
    transcript = transcript.replace('\\', '')

    return transcript


# Join and separate the list by some specified number of words

# In[58]:

def running_sum(a):
  tot = 0
  for item in a:
    tot += item
    yield tot

def buildSent(link):
    trans = LoadTrans(link)
    blob = TextBlob(trans)
    sent = [sentence.sentiment.polarity for sentence in blob.sentences]
    return list(running_sum(sent))
    
def plotSent(link):
    trans = LoadTrans(link)
    blob = TextBlob(trans)
    sent = [sentence.sentiment.polarity for sentence in blob.sentences]
    buildSent = list(running_sum(sent))
    sentNorm = pd.DataFrame(zip(np.linspace(0,100,len(buildSent)),buildSent))
    plt.plot(sentNorm[0],sentNorm[1])


# In[ ]:

for link in page1Trans['Transcript URL'][0:10]:
    plotSent(link)
plt.show()

