#! /usr/bin/env python

import urllib2
import re
import sys
import os

def verifyDirectory():
    '''
    Checks to see if the specified directory is present and empty.  If it is not present
    it is created.  If it is not empty, the user is notified.
    '''
    try:
        if len(os.listdir(saveDirectory)) > 0:
            print 'Please specify a clean directory to save to...'
            exit(0)
    except IOError:
        os.makedirs(saveDirectory)
        print 'making - '+saveDirectory 

def getExtension(filelocation):
    '''
    Grabs the extension of a file, or if the file doesn't have one, automatically returns a 
    jpeg type, since this will force the correct OS behavior on open anyhow.
    '''
    extension = filelocation[-4:]
    if not extension[0] == '.':
        extension = '.jpg'
    return extension
    
def fetchFile(filelocation):
    try:
        response = urllib2.urlopen(filelocation)
        picture = response.read()
        return picture
    except:
        return None
    
def fetchAndSaveFile(filelocation,namepart):
      '''
      Take in a remote image file to save to the local hard drive, as specified by the 
      saveName variable.
      '''
      picture = fetchFile(filelocation)
      filename = saveDirectory + saveName + namepart + getExtension(filelocation)
      fout = open(filename, "wb")
      fout.write(picture)
      fout.close()

def tidyUpFileLocationForSite(filename,website):
    '''
    Takes in a filename and ensures two things.  1) If it is a relative directory, that the
    hostname is appended on the front.  2) That it begins with the HTTP prefix.
    '''
    if filename.startswith('/'):
        filename = website+filename
    if not filename.startswith('http://'):
        filename = 'http://'+filename
    return filename
      
def tidyUpFileLocation(filename):
    '''
    Takes in a filename and ensures two things.  1) If it is a relative directory, that the
    hostname is appended on the front.  2) That it begins with the HTTP prefix.
    '''
    if filename.startswith('/'):
        filename = url+filename
    if not filename.startswith('http://'):
        filename = 'http://'+filename
    return filename

def scrubSite(url):
    '''
    Gathers the source from the given url, and passes it off to find all of the images on that site.
    Then, it iterates through the images and delegates the saving of them to the local hard drive.
    '''
    verifyDirectory()
    source = returnSource(url)
    images = findImages(source)
    count = 1
    for image in images:
        if count <= limit or limit == -1:
            image = tidyUpFileLocation(image,url)
            fetchAndSaveFile(image,str(count))
            count = count+1

def returnSource(url):
    '''
    Returns the source code from the specified url.
    '''
    response = urllib2.urlopen(url)
    source = response.read()
    source = source.replace('\n','')
    return source

def findImages(text):
    '''
    Searches a given String of source code for all html image references.
    '''
    imageSearch = re.compile('<img[^>]* src=\"([^\"]*)\"[^>]*>')
    images = re.findall(imageSearch, text)
    uniqueImages = set(images)
    return uniqueImages

def usage():
    print 'Fetches the images from a specified website and saves them locally'
    print ''
    print 'python imageScrub.py URL SAVEDIRECTORY SAVENAMEPREFIX PICTURE LIMIT[optional]'
    print ''
    print 'Example: python imageScrub.py http://homedepot.com /images/ stuff 15'

if __name__ == '__main__':
    url = ''
    saveDirectory = ''
    saveName = '' 
    limit = -1
    
    if len(sys.argv) >= 4:
        saveDirectory = sys.argv[2]
        saveName = sys.argv[3]
        url = sys.argv[1]
        if len(sys.argv) == 5:
            limit = int(sys.argv[4]) 
    else:
        usage()
        exit(0)
    scrubSite(url)