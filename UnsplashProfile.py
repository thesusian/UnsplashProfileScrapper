#!/bin/python

import os
import sys
import wget
import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

DownloadPath = "/drives/HardD/Art/Unsplash/"
ChromeDriverPath = "/bin/chromedriver"

ButtonClass = "CwMIr.DQBsa.p1cWU.jpBZ0.AYOsT.Olora.I0aPD.dEcXu"
PictureCountClass = "NVSs7"

# Check if arg is supplied and create a url based on it
if len(sys.argv) != 2:
    print("Usage: ./UnsplashProfile.py <username>")
    exit()
else:
    username = sys.argv[1]
    url = 'https://unsplash.com/@' + username

# Start the webdriver, set prefs and get the link
driverOptions = Options()
driverOptions.headless = True
driver = webdriver.Chrome(service=Service(ChromeDriverPath), options=driverOptions)
driver.get(url)
time.sleep(2)
print("INFO: loaded page (I hope)")

# Wait for the page to load
"""
try:
    app = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.ID, 'app'))) # app is the main dev right after <body>
except TimeoutException:
    print("ERROR: page timed out, check your connection")
    exit()
"""

# Find how many pictures are in the profile
soup = BeautifulSoup(driver.page_source, 'html.parser')
pictureCount = soup.find(class_=PictureCountClass)
pictureCount = int(pictureCount.text.strip())
print("INFO: there are " + str(pictureCount) + " pictures in this account")
gotAllPics = False

if pictureCount <= 20:
    gotAllPics = True
    print("INFO: account has 20 or less pictures so there is no need to scroll")

if not gotAllPics:
# Define the button and scroll to it
    button = driver.find_element(By.CLASS_NAME, ButtonClass)
    scroll_origin = ScrollOrigin.from_element(button)
    ActionChains(driver)\
        .scroll_from_origin(scroll_origin, 0, 200)\
        .perform()
    print("INFO: scrolled to the button")

# Click on the button and wait a bit
    time.sleep(1)
    print("INFO: clicked the button")
    button.click()
    time.sleep(2)

# Scroll down then up untill all pictures are found
    print("INFO: started loading extra pics")

    while not gotAllPics:
        time.sleep(0.2)
        ActionChains(driver)\
            .scroll_by_amount(0, 2000)\
            .perform()
        time.sleep(0.2)
        ActionChains(driver)\
            .scroll_by_amount(0, -300)\
            .perform()
        
        # get download links count and compare to pic count
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        downloadLinks = []
        for link in soup.find_all('a'):
            innerLink = link.get('href')
            if 'download' in innerLink:
                downloadLinks.append(innerLink)
        print("INFO: got " + str(len(downloadLinks)) + " links")
        if len(downloadLinks) == pictureCount:
            gotAllPics = True

print("INFO: done loading downloading links")
soup = BeautifulSoup(driver.page_source, 'html.parser')
driver.quit()

downloadLinks = []
for link in soup.find_all('a'):
    innerLink = link.get('href')
    if 'download' in innerLink:
        downloadLinks.append(innerLink)
print("INFO: got " + str(len(downloadLinks)) + " links")

if not downloadLinks:
    print("ERROR: could not find any download links, check the username")
else:
    for link in downloadLinks:
        photoID = link.split("photos/")[1]
        photoID = photoID.split("/download")[0]

        downloadName = username + "-" + photoID + ".jpg"
        finalDownloadPath = DownloadPath+username+"/"
        
        mkdir = os.system("mkdir -p " + finalDownloadPath)

        if os.path.exists(finalDownloadPath+downloadName):
            print("WARNING: file " + downloadName + " already exists, skipping")
        else:
            wget.download(link, finalDownloadPath+downloadName)
            print()
            print("INFO: downloaded " + downloadName)
