
#!/usr/bin/python -tt

import os
import hashlib
import urllib2
import sys
import logging
import requests,time,re,zipfile
from PyQt4 import QtGui,QtCore
from bs4 import BeautifulSoup

def get_hash(name):
        readsize = 64 * 1024
        with open(name, 'rb') as f:
            size = os.path.getsize(name)
            data = f.read(readsize)
            f.seek(-readsize, os.SEEK_END)
            data += f.read(readsize)
        return hashlib.md5(data).hexdigest()

def sub_downloader(path):

    hash = get_hash(path)
    replace = ['.avi', '.dat', '.mp4', '.mkv', '.vob',".mpg",".mpeg"]
    for content in replace:
        path = path.replace(content,"")
    if not os.path.exists(path+".srt"):
        headers = { 'User-Agent' : 'SubDB/1.0 (subtitle-downloader/1.0; http://google.com)' }
        url = "http://api.thesubdb.com/?action=download&hash="+hash+"&language=en"
        req = urllib2.Request(url, '', headers)
        try:
            response = urllib2.urlopen(req).read()
            with open (path+".srt","wb") as subtitle:
                subtitle.write(response)
        except:
			print "subtitles not found"
            
def sub_downloader2(path):
    try:
        root, extension = os.path.splitext(path)
        if extension not in [".avi", ".mp4", ".mkv", ".mpg", ".mpeg", ".mov", ".rm", ".vob", ".wmv", ".flv", ".3gp",".3g2"]:
            return  
        if os.path.exists(root + ".srt"):
            return
        j=-1
        root2=root
        for i in range(0,len(root)):
            if(root[i]=="\\"):
                j=i
        root=root2[j+1:]
        root2=root2[:j+1]
        r=requests.get("http://subscene.com/subtitles/release?q="+root);
        soup=BeautifulSoup(r.content,"html.parser")
        atags=soup.find_all("a")
        href=""
        for i in range(0,len(atags)):
            spans=atags[i].find_all("span")
            if(len(spans)==2 and spans[0].get_text().strip()=="English"):
                href=atags[i].get("href").strip()               
        if(len(href)>0):
            r=requests.get("http://subscene.com"+href);
            soup=BeautifulSoup(r.content,"html.parser")
            lin=soup.find_all('a',attrs={'id':'downloadButton'})[0].get("href")
            r=requests.get("http://subscene.com"+lin);
            soup=BeautifulSoup(r.content,"html.parser")
            subfile=open(root2+".zip", 'wb')
            for chunk in r.iter_content(100000):
                subfile.write(chunk)
                subfile.close()
                time.sleep(1)
                zip=zipfile.ZipFile(root2+".zip")
                zip.extractall(root2)
                zip.close()
                os.unlink(root2+".zip")
                os.rename(root2+zip.namelist()[0], os.path.join(root2, root + ".srt"))
    except:
        #Ignore exception and continue
        print "Error in fetching subtitle for " + path
        print "Error", sys.exc_info()
        
        logging.error("Error in fetching subtitle for " + path + str(sys.exc_info()))            
        print "trying subdb api"
        sub_downloader(path)
def processFile(currentDir):
    currentDir = os.path.abspath(currentDir)
    filesInCurDir = os.listdir(currentDir)
    for file in filesInCurDir:
        curFile = os.path.join(currentDir, file)
        if os.path.isfile(curFile):
            curFileExtension = curFile[-3:]
            if curFileExtension in ['avi', 'dat', 'mp4', 'mkv', 'vob',"mpg","mpeg"]:
                print('downloading the subtitle for %s' %curFile)
                sub_downloader2(curFile)
                print('downloading completed')
        else:
            print('entering to directory %s'%curFile)
            processFile(curFile)

if __name__ == "__main__" :
	
	app = QtGui.QApplication(sys.argv)
	
	widget = QtGui.QWidget()
	widget.resize(500, 250)
		
	screen = QtGui.QDesktopWidget().screenGeometry()
	widget_size = widget.geometry()
	
	widget.move((screen.width()-widget_size.width())/2,(screen.height()-widget_size.height())/2)
		
	widget.setWindowTitle('https://github.com/arajparaj/pysub')
	widget.setWindowIcon(QtGui.QIcon('exit.png'))
	
	foldername = QtGui.QFileDialog.getExistingDirectory(widget,'Choose a Video Folder directory')
	if foldername:
		processFile(str(foldername))
	else :
		print "please input a valid folder name"
