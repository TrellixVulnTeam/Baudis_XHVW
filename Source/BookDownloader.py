import codecs
import os.path

from requests import get
from bs4 import BeautifulSoup
import urllib3
from threading import Thread
from requests_html import HTMLSession
import sys
import codecs
from pathlib import Path

poolM = urllib3.PoolManager()

def downloadBook(link, title, *largs):
    with HTMLSession() as session:
        response = session.get(link)
        response.html.render()
        response.close()
    downloadLink = findDownloadLink(response)
    loading(downloadLink, title)

def findDownloadLink(html):
    data_bid = html.html.find('div.bookpage--chapters.player--chapters', first = True).attrs['data-bid']
    jplPlayers = html.html.find('div.jpl')

    for jpl in jplPlayers:
        if('data-bid' in jpl.attrs and jpl.attrs['data-bid'] == data_bid):
            downloadLink = jpl.find('audio',first= True).attrs['src']

    return downloadLink

def newDownloadThread(link, filename, path = ''):
    download_thread = threading.Thread(target=loading, args=(link,filename,path))
    download_thread.start()

def loading(link,filename, path = os.path.expanduser('~/Baudis/SavedBooks')):
    response = poolM.request('GET',link,preload_content = False)
    Path(path ).mkdir(parents=True, exist_ok=True)#Create directory for books if not exist
    contentLength = response.getheader('Content-Length')
    chunkSize = 1024
    filePercent = int(contentLength) / 100
    loadPercent = 0;
    inCompletePercent = 0;
    filename = filename.replace(' ','_')

    with open(R'{path}/{filename}.mp3'.format(path=path, filename=filename),'wb') as out_file:
        for chunk in response.stream(chunkSize):
            if chunk:
                inCompletePercent += chunkSize
                if inCompletePercent >= filePercent:
                    loadPercent += 1
                    inCompletePercent -= filePercent
                    print('Load: {percent}%'.format(percent = loadPercent))
                out_file.write(chunk)
    print(f' Download end: \n Link: {link} \n Filename: {filename} \n Filepath: {path}/{filename}.mp3')
    print('Close downloader')


while True:
    prefix = '-d'
    LinkTitle = sys.stdin.readline()
    if(LinkTitle.strip() == 'cancel'):
        print('Canceled')
    elif prefix in LinkTitle:
        LinkTitle = LinkTitle.removeprefix(prefix)
        LinkTitle = LinkTitle.split(' ||| ')
        downloadBook(LinkTitle[0],LinkTitle[1])
    else: print('Unknown command {LinkTitle}'.format(LinkTitle = LinkTitle))
    sys.stdin.flush()
    sys.stdin.close()
    break

