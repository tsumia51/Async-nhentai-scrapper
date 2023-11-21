import cloudscraper
import concurrent.futures
from bs4 import BeautifulSoup
import re,os,sys,requests
import argparse
import math

parser = argparse.ArgumentParser()
parser.add_argument('nhentaiCodeArg', nargs='*', default='0')
args = parser.parse_args()

def vpnNodeErrorHandle(mainPage):
    if re.findall('Just a moment', str(mainPage)):
        print('Use a different vpn server!')
        quit()

if args.nhentaiCodeArg == '0':
    print('Put in some numbers dummy!')
    quit()

scraper = cloudscraper.create_scraper() 

vpnNodeErrorHandle(BeautifulSoup((scraper.get(f"https://nhentai.net/").content), "html.parser"))

getHowManyNhentaiGallery = BeautifulSoup((scraper.get(f"https://nhentai.net/").content), "html.parser")

mostRecentGallery = getHowManyNhentaiGallery.select('#content > div:nth-child(3) > div > a:first-child')[0]['href']

num = re.findall(r'\d+', mostRecentGallery)[0]

def validateArg(arg):
    #check if numbers exist in arg
    #eg https://nhentai.net/g/123/
    #eg matches 123
    if (len(re.findall(r'\d+', arg)) <= 0):
        print('Put in some numbers dummy !')
        quit()
    return re.findall(r'\d+', arg)
    
def validateArrayArg():
    #123,123, 123
    listToStr = ' '.join([str(elem) for elem in args.nhentaiCodeArg])
    #123 123  123
    replace = listToStr.replace(",", " ")
    #['123', '123', '', '123']
    newList = list(replace.split(" "))
    #['123', '123', '123']
    return list(filter(None, newList))
  
nhentaiCode = args.nhentaiCodeArg

if len(args.nhentaiCodeArg) < 2:
    nhentaiCode = validateArg(args.nhentaiCodeArg[0])
else:
    for i in args.nhentaiCodeArg:
    #poor fuck used args https://nhentai.net/g/123/ https://nhentai.net/g/123/ ?
        if re.findall(r'http', i):
            index = nhentaiCode.index(i)
            nhentaiCode[index] = validateArg(i)
        #poor fuck used args 123,123, 123 ?
        #["123,123,", "123"]
        if re.findall(r',', i):
            nhentaiCode = validateArrayArg()   
        
for i in nhentaiCode:
    if int(i) > int(num):
        print(f'{i} is not a valid gallery')
        quit()

def cls():
    os.system('cls' if os.name=='nt' else 'clear')
        
def getAmountOfImgInDir():
    count = 0 
    for paths in os.listdir(path):
        # check if current path is a file
        if os.path.isfile(os.path.join(path, paths)):
            count += 1
    return count
    
def progressMenu(num, title,maxPage,count):
    index = nhentaiCode.index(num)
    cls()
    if len(nhentaiCode) > 50:
        print('You do NOT need this much porn')
    elif len(nhentaiCode) > 20:
        print('Try downloading in chunks instead!')
    print(f'Gallery {index + 1} out of {len(nhentaiCode)}')
    print(title)
    print(f'page downloaded = {count} out of {maxPage}')
    
def makeDirectory(path):
    if (not(os.path.exists(path))):
        os.mkdir(path) 

def getPath(title):
    normalizedTitle = re.sub(r'[\\\/?*:"<>|]','',title)
    parent_dir = sys.path[0]
    return os.path.join(parent_dir, normalizedTitle) 
    
def mainPageInfo():
    scraper = cloudscraper.create_scraper() 
    i = BeautifulSoup((scraper.get(f"https://nhentai.net/g/{num}/").content), "html.parser")
    return i
    
def findMaxPage(mainPage):
    lastImg = mainPage.select('.thumb-container:last-child > .gallerythumb > .lazyload')
    
    #grabs pageCount + t
    #eg https://t7.nhentai.net/galleries/2712361/16t.jpg
    #16t
    if re.findall(r'\d+t', str(lastImg)) == []:
        print('The format is asynctest.py num')
        quit()
    r = re.findall(r'\d+t', str(lastImg))[0]
    
    #slice t at the end
    return int(r[:len(r)-1])
    
def getTitle(mainPage):
    line = mainPage.select('h1.title > span')
    
    return f'[{num}] {line[1].text}{line[2].text}'
    
def getImgHostNum(mainPage):
    span = mainPage.select('.thumb-container:last-child > .gallerythumb > img')[0]
    #eg https://t3.nhentai.net/galleries/2712361/17t.jpg
    #\d+ find num
    #\/ \/ find num inside / / 
    return re.findall(r'\/(\d+)\/', span['data-src'])[0]
    
def allImgFileType(maxPage):
    fileTypes = []
    if len(fileTypes) > 50:
        fileTypes = []
    for i in range(maxPage):
        i = i + (50 * limit)
        if i >= maxPage:
            break;
        imageInfo = imgSrc[i].select('.gallerythumb > img')[0]['data-src']
        #\w+ find all leters
        #$ search at end of string
        fileInfo = re.findall(r'\w+$', imageInfo)[0]
        fileTypes.append(fileInfo)
        if i > 50 + (50 * limit):
            break;
    return fileTypes

def imgHostSiteUrl(fileTypes, maxPage):
    URLS = []
    if len(URLS) > 50:
        URLS = []
    for n in range(maxPage):
        n = n + (50 * limit)
        if n >= maxPage:
            break;
        URLS.append(f'https://i7.nhentai.net/galleries/{imgHostNum}/{n + 1}.{fileTypes[int(n - (50 * limit))]}')
        if n > 50 + (50 * limit):
            break;
    return URLS

# Retrieve a single page and report the URL and contents
def load_url(url, timeout):
    with requests.get(url, timeout=timeout) as conn:
        return conn.content
        
def asyncWorkers(fileTypes,URLS,maxPage):
    global limit
    #idk man i just copy and pasted this async thing
    # We can use a with statement to ensure threads are cleaned up promptly
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        # Start the load operations and mark each future with its URL
        future_to_url = {executor.submit(load_url, url, 60): url for url in URLS}
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            try:
                data = future.result()
            except Exception as exc:
                print('%r generated an exception: %s' % (url, exc))
            else:
                writeDataToImg(fileTypes,url,data)
                count = getAmountOfImgInDir() 
                progressMenu(num, title, maxPage,count)
                if (count >= 50 + (50*limit)):
                    limit += 1
            
def writeDataToImg(fileTypes,url,data):
    pageCount = re.findall(r'\d+', url)[2]
    normalized = int(pageCount) - (50 * limit)
    f = open(f'{path}\\page {pageCount}.{fileTypes[int(normalized) - 1]}','wb') 
    f.write(data) 
    f.close()
    
def loop(maxPage):
    count = getAmountOfImgInDir()    
    fileTypes = allImgFileType(maxPage)
    URLS = imgHostSiteUrl(fileTypes,maxPage)
    asyncWorkers(fileTypes,URLS,maxPage)

for num in nhentaiCode:
    limit = 0
    mainPage = mainPageInfo()
    imgSrc = mainPage.select('.thumb-container')
    maxPage =  findMaxPage(mainPage)
    title = getTitle(mainPage)
    
    path = getPath(title)
    makeDirectory(path)
    count = getAmountOfImgInDir() 
    imgHostNum = getImgHostNum(mainPage)
    if (count >= maxPage):
        continue;
    loopCycle = math.ceil(maxPage/50)
    for a in range(loopCycle):
        loop(maxPage)