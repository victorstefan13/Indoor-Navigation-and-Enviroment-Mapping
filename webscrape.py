#web scrape function which downloads images directly from Google Images
#USAGE: python3 webscrape.py -k internal door

#import packages
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import json
import os
import urllib2
import argparse


# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-k", "--keyword", required=True,
                help="key word to search google images")
args = vars(ap.parse_args())

#the key word will also be the directory name
searchterm = args["keyword"]

#url for google images
url = "https://www.google.co.in/search?q="+searchterm+"&source=lnms&tbm=isch"

# NEED TO DOWNLOAD CHROMEDRIVER, insert path to chromedriver inside parentheses in following line - only if used with chrome
browser = webdriver.Chrome()
browser.get(url)
header={'User-Agent':"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36"}
counter = 0
succounter = 0

#check to see if a directory already exists 
if not os.path.exists(searchterm):
    os.mkdir(searchterm)

#for loop used for scrolling though google images
for _ in range(500):
    browser.execute_script("window.scrollBy(0,10000)")

#grab the HTML data, download the image and store it within a file. Ouput a counter to user for easy visualization of the serach results
for x in browser.find_elements_by_xpath('//div[contains(@class,"rg_meta")]'):
    counter = counter + 1
    print "Total Count:", counter
    print "Succsessful Count:", succounter
    print "URL:",json.loads(x.get_attribute('innerHTML'))["ou"]

    #save the iamge
    img = json.loads(x.get_attribute('innerHTML'))["ou"]
    imgtype = json.loads(x.get_attribute('innerHTML'))["ity"]
    try:
        req = urllib2.Request(img, headers={'User-Agent': header})
        raw_img = urllib2.urlopen(req).read()
        File = open(os.path.join(searchterm , searchterm + "_" + str(counter) + "." + imgtype), "wb")
        File.write(raw_img)
        File.close()
        succounter = succounter + 1
    except:
            print "can't get img"

#terminate the script.
print succounter, "pictures succesfully downloaded"
browser.close()