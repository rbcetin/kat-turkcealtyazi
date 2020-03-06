#!/usr/bin/env python
# -*- coding: utf-8-sig -*-
from bs4 import BeautifulSoup
import requests,json,sys,os,re,subprocess
from random import randint
from time import sleep
import cfscrape
import webbrowser

def randomString(stringLength=10):
    import string
    import random
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))

def details(name):
    global isim,sezon,bolum,grup,surum,regex,sifirsiz,movie
    test_str = name.lower().replace(".proper","").replace(".repack","").replace(".real","")
    
    webdl = re.search(r"s[0-9]{1,2}e[0-9]{1,2}.{1,}[0-9]{1,4}p.{1,}web-dl", test_str, re.IGNORECASE)
    webrip = re.search(r"s[0-9]{1,2}e[0-9]{1,2}.{1,}[0-9]{1,4}p.{1,}rip", test_str, re.IGNORECASE)
    web = re.search(r"s[0-9]{1,2}e[0-9]{1,2}.{1,}[0-9]{1,4}p.{1,}web\.", test_str, re.IGNORECASE)
    
    try:
        isim = re.search(r".{1,}.s[0-9]{1,2}", test_str, re.IGNORECASE).group()[:-4].replace(".proper","").replace(".repack","").replace(".real","")
        isim = re.sub(r"[0-9]{4}", "REMOVE", isim, 0).replace(".REMOVE","").replace(".","-")
        sezon = re.search(r"s[0-9]{1,2}", test_str, re.IGNORECASE).group()[1:]
        bolum = re.search(r"e[0-9]{1,2}", test_str, re.IGNORECASE).group()[1:]
        if int(sezon) < 10:
            sifirsiz = sezon[1:]
        else:
            sifirsiz = sezon
            
        if "proper" in name.lower():
            regex = r""+sezon[:-1]+"?"+sezon[1:]+".?"+bolum+".proper"
        elif "repack" in name.lower():
            regex = r""+sezon[:-1]+"?"+sezon[1:]+".?"+bolum+".repack"
        else:
            regex = r""+sezon[:-1]+"?"+sezon[1:]+".?"+bolum+""
        movie = 0
    except:
        movie = 1
       
    if webdl:
            grup = re.search(r"4-.{1,}", test_str, re.IGNORECASE).group()[2:]
            surum = "r8" #webdl
    elif webrip:
            grup = re.search(r"-.{1,}", test_str, re.IGNORECASE).group()[1:]
            surum = "r6" #webrip
    elif web:
            grup = re.search(r"-.{1,}", test_str, re.IGNORECASE).group()[1:]
            surum = "r6" #web
    else:
            grup = re.search(r"-.{1,}", test_str, re.IGNORECASE).group()[1:]
            surum = "r1" #hd

def download_sub(link,yol,mkv):
    try:
        from bs4 import BeautifulSoup
        import shutil
        from zipfile import ZipFile
        from rarfile import RarFile
        import codecs
        randfold = randomString()
        os.mkdir(yol+randfold)
        if "turkish" in link:
            s = requests.Session()
            req = s.get("https://subscene.com/" + link).text
            finalink = BeautifulSoup(req).find('a', attrs={'id':'downloadButton'}).get('href')
            f = s.post("https://subscene.com" + finalink, stream=True)
        else:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            url = "https://www.turkcealtyazi.org/" + link
            options = Options()
            options.headless = True
            options.add_argument('--blink-settings=imagesEnabled=false')
            options.add_argument('--no-proxy-server')
            options.add_experimental_option('excludeSwitches', ['enable-logging'])
            options.add_experimental_option("prefs", {
              "download.default_directory": r""+yol+randfold+"/",
              "download.prompt_for_download": False,
              "download.directory_upgrade": True,
              "safebrowsing.enabled": True
            })       
            driver = webdriver.Chrome(options=options, executable_path=r'C:/Program Files (x86)/kat-dp/chromedriver.exe')
            driver.get(url)
            content = driver.find_element_by_class_name('altIndirButton')
            content.click()
            while True:
                if len(os.listdir(yol+randfold)) == 0: 
                    sleep(0.5)
                else: 
                    filename = max([yol+randfold + "\\" + f for f in os.listdir(yol+randfold)],key=os.path.getctime)
                    local_name = filename
                    driver.quit()
                    break
                    
        if local_name.endswith(".rar"):
            with RarFile(local_name) as file:
                if movie==0:
                    saks = [i for i in file.namelist() if re.search(regex, i, re.IGNORECASE) and i.endswith(".srt")]
                else:
                    saks = [1]
                if saks[0] and movie==0:
                    print("\t Found: " + saks[0])
                    file.extract(saks[0],path=yol)
                else:
                    saks = [i for i in file.namelist() if i.endswith(".srt")]
                    print ("\t Found: " + saks[0])
                    file.extract(saks[0],path=yol)
        else:
            with ZipFile(local_name) as file:
                if movie==0:
                    saks = [i for i in file.namelist() if re.search(regex, i, re.IGNORECASE) and i.endswith(".srt")]
                else:
                    saks = [1]
                if saks[0] and movie==0:
                    print ("\t Found: " + saks[0])
                    file.extract(saks[0],path=yol)
                else:
                    saks = [i for i in file.namelist() if i.endswith(".srt")]
                    print ("\t Found: " + saks[0])
                    file.extract(saks[0],path=yol)
                    
        eben = yol+saks[0]
        fullpath = yol+mkv+".srt"
        
        if os.path.isfile(fullpath):
            fullpath = yol+mkv+".tr.srt"
            
        print("\t Renaming with the same name as video file.")
        os.rename(eben, fullpath)
        with codecs.open(fullpath, 'r', encoding='windows-1254', errors='ignore') as f:
            text = f.read()
        with codecs.open(fullpath, 'w', encoding='utf-8') as f:
            f.write(text)
        
        print ("\t Removing: " + local_name.rsplit('\\', 1)[-1])
        shutil.rmtree(yol+randfold)
        
    except Exception as e:
        print(e)
        webbrowser.get("C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s").open("https://www.turkcealtyazi.org/" + link)



def download_sub_old(link,yol,mkv):
    try:
        from bs4 import BeautifulSoup
        from zipfile import ZipFile
        from rarfile import RarFile
        import codecs
        
        if "turkish" in link:
            s = requests.Session()
            req = s.get("https://subscene.com/" + link).text
            finalink = BeautifulSoup(req).find('a', attrs={'id':'downloadButton'}).get('href')
            f = s.post("https://subscene.com" + finalink, stream=True)
        else:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
                'origin': "https://turkcealtyazi.org",
                'referer': "https://www.turkcealtyazi.org/" + link,
            }

        with requests.Session() as sess:
            res = sess.get("https://www.turkcealtyazi.org/" + link)
            indir_keys = BeautifulSoup(res.content,"html.parser").find('form', action='/ind').findAll('input', attrs={'type': 'hidden'})     
            form_data = {}
            for k in indir_keys:
                form_data[k['name']] = k['value']                
            f = sess.post('https://www.turkcealtyazi.org/ind', data=form_data,cookies=res.cookies)
            print(f.content)



        if f.status_code == 200:
            if 'Content-Disposition' in f.headers:
                local_name = f.headers['Content-Disposition'].split('filename=')[1].strip('"\'')
            else:
                local_name = 'test.zip'
                raise ValueError("Couldn't Get The File")
            local_tmp_file = os.path.join(yol, str(randint(0,20)) + local_name)
            with open(local_tmp_file, 'wb') as outfile:
                for chunk in f.iter_content(1024):
                    outfile.write(chunk)
        else:
            raise ValueError("Couldn't Get The File")
        
        if local_name.endswith(".rar"):
            with RarFile(local_tmp_file) as file:
                if movie==0:
                    saks = [i for i in file.namelist() if re.search(regex, i, re.IGNORECASE) and i.endswith(".srt")]
                else:
                    saks = [1]
                if saks[0] and movie==0:
                    print("\t Found: " + saks[0])
                    file.extract(saks[0],path=yol)
                else:
                    saks = [i for i in file.namelist() if i.endswith(".srt")]
                    print ("\t Found: " + saks[0])
                    file.extract(saks[0],path=yol)
        else:
            with ZipFile(local_tmp_file) as file:
                if movie==0:
                    saks = [i for i in file.namelist() if re.search(regex, i, re.IGNORECASE) and i.endswith(".srt")]
                else:
                    saks = [1]
                if saks[0] and movie==0:
                    print ("\t Found: " + saks[0])
                    file.extract(saks[0],path=yol)
                else:
                    saks = [i for i in file.namelist() if i.endswith(".srt")]
                    print ("\t Found: " + saks[0])
                    file.extract(saks[0],path=yol)                 

        eben = yol+saks[0]
        fullpath = yol+mkv+".srt"
        
        if os.path.isfile(fullpath):
            fullpath = yol+mkv+".tr.srt"
            
        print("\t Renaming with the same name as video file.")
        os.rename(eben, fullpath)
        with codecs.open(fullpath, 'r', encoding='windows-1254', errors='ignore') as f:
            text = f.read()
        with codecs.open(fullpath, 'w', encoding='utf-8-sig') as f:
            f.write(text)
        
        print ("\t Removing: " + local_tmp_file[3:])
        os.remove(local_tmp_file)
    except:
        webbrowser.get("C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s").open("https://www.turkcealtyazi.org/" + link)

def imdb_movsearch(name):
    r = requests.get('https://api.themoviedb.org/3/search/movie?api_key=a0a4437eea1890fcffee70f77f38d496&language=en-US&query='+name+'&page=1')
    d  = r.json()
    r = requests.get('https://api.themoviedb.org/3/movie/'+str(d["results"][0]["id"])+'?api_key=a0a4437eea1890fcffee70f77f38d496&language=en-US')
    d  = r.json()
    imdbid = d["imdb_id"]
    return imdbid[2:]

def imdb_search(name):
    r = requests.get('https://api.themoviedb.org/3/search/tv?api_key=a0a4437eea1890fcffee70f77f38d496&language=en-US&query='+name+'&page=1')
    d  = r.json()
    r = requests.get('https://api.themoviedb.org/3/tv/'+str(d["results"][0]["id"])+'/external_ids?api_key=a0a4437eea1890fcffee70f77f38d496&language=en-US')
    d  = r.json()
    imdbid = d["imdb_id"]
    return imdbid[2:]

def degistir(gelen):
    memo = gelen.replace("r3", "DVDScr").replace("r10", "HDTS").replace("r8", "WEB-DL").replace("r6", "WEBRip").replace("r1", "HD").replace("r2", "DVDRip").replace("r9", "HDRip").replace("r7", "BDRip")
    return memo

def safe_str(obj):
    try: return str(obj)
    except UnicodeEncodeError:
        return obj.encode('ascii', 'ignore').decode('ascii')
    return ""

def let_user_pick(options,no):
    print("Found subtitles:")
    for idx, element in enumerate(options):
        if no == 0:
            if movie==0:
                print ("\t (" + str(idx+1) + ") " + isim + " [" + element[6] + "] S" + sezon + "E" + bolum + " <" + element[2] + "> [" + degistir(element[4]) + " "+element[5]+"]")
            elif movie==1:
                print ("\t (" + str(idx+1) + ") " + isim + " [" + element[5] + "] <" + element[1] + "> [" + degistir(element[3]) + " "+element[4]+"]")
        elif no == 1:
            print ("\t (" + str(idx+1) + ") " + element[1])
    i = raw_input("Input number: ")
    try:
        if 0 <= int(i) <= len(options):
            return int(i)-1
    except:
        pass
    return None

if __name__ == '__main__':

    turkce = []
    hepsi = []
    yolu = sys.argv[1].rsplit('\\', 1)[0] + "\\"
    mkv = sys.argv[1].split('\\', -1)[-1][:-4]
    details(mkv)

    if movie == 0:
        dizilink = "http://www.turkcealtyazi.org/mov/" + imdb_search(isim) + "/"
        altyazilar = BeautifulSoup(requests.post(dizilink,stream=True).content,"html.parser").findAll('div', attrs={'class':'sezon_'+sifirsiz})

        if altyazilar:
            print ("Searching Turkcealtyazi.org for " + mkv)
            for teker in altyazilar:
                isitme = teker.find("img", { "src" : "/images/isitme.png" })
                if isitme is not None: continue
                sublink = teker.find('div', attrs={'class':'alisim'}).find('a', attrs={'class':'underline'}).get('href')
                subdil = teker.find('div', attrs={'class':'aldil'}).find('span').get('class')[0].replace("flag","")
                subcevir = teker.find('div', attrs={'class':'alcevirmen'}).text
                subsayi = int(teker.find('div', attrs={'class':'alindirme'}).text.replace(",",""))
                subep = teker.find('div', attrs={'class':'alcd'}).findAll('b')[1].text
                subgr = teker.find('div', attrs={'class':'ripdiv'})
                try:
                    subsur = teker.find('div', attrs={'class':'ripdiv'}).find('span').get('class')[1]
                    subgr.find('span').decompose()
                except:
                    subsur = surum.lower()
                    subgr = teker.find('div', attrs={'class':'ripdiv'})
                    
                subgr = subgr.text.strip().lower()

                if "tr" in subdil: # Get turkish subtitles for every version
                    if bolum in subep:                                                                          ### Get matches for episode number
                        if surum in subsur and grup in subgr:                                                   ##### Perfect match
                            turkce.append((sublink,subep,subcevir,subsayi,subsur,subgr,subdil))
                            break
                        elif (surum in subsur and grup not in subgr) or (surum not in subsur and grup in subgr):##### One of them matched
                            turkce.append((sublink,subep,subcevir,subsayi,subsur,subgr,subdil))
                            break
                        else:                                                                                   ##### Neither version nor group matched.
                            hepsi.append((sublink,subep,subcevir,subsayi,subsur,subgr,subdil))
                            
                    elif "Paket" in subep:                                                                      ### When no matches for episode number check Paket
                        if surum in subsur and grup in subgr: 
                            turkce.append((sublink,subep,subcevir,subsayi,subsur,subgr,subdil))
                            break
                        elif surum in subsur and grup not in subgr or (surum not in subsur and grup in subgr): 
                            turkce.append((sublink,subep,subcevir,subsayi,subsur,subgr,subdil))
                            break
                        else: 
                            hepsi.append((sublink,subep,subcevir,subsayi,subsur,subgr,subdil))          



            if turkce: # if there is a perfect match
                turkce = sorted(turkce, key=lambda tup: tup[3], reverse=True)
                download_sub(turkce[0][0],yolu,mkv)
                print ("\t Finished: " +  isim + " [" + turkce[0][6] + "] S" + sezon + "E" + bolum + " <" + turkce[0][2] + "> [" + degistir(turkce[0][4]) + "] \n")
            else:
                if hepsi:
                    hepsi = sorted(hepsi, key=lambda tup: tup[3], reverse=True)
                    secilen = let_user_pick(hepsi,0)
                    if isinstance(secilen, int):
                        download_sub(hepsi[secilen][0],yolu,mkv)
                        print ("\t Finished: " + isim + " [" + hepsi[secilen][6] + "] S" + sezon + "E" + bolum + " <" + hepsi[secilen][2] + "> [" + degistir(hepsi[secilen][4]) + " *] \n")
                    else:
                        print ("No TR subtitle for " + isim + " S" + sezon + "E" + bolum + " " + degistir(surum) + " " + grup + ". \n")
                else:
                    print ("No TR subtitle for " + isim + " S" + sezon + "E" + bolum + " " + degistir(surum) + " " + grup + ". \n")
        else:
            print ("Nothing found. Going for subscene.com")
            #url2="https://subscene.com/subtitles/release?q=" + isim + "+S" + sezon + "E" + bolum + "+" + degistir(surum) + "&r=true"
            url2="https://subscene.com/subtitles/release?q=" + mkv + "&r=true"
            cookie = {'LanguageFilter': '41'} # Turkce = 41
            data2=requests.post(url2,stream=True, cookies=cookie)
            data2=BeautifulSoup(data2.content,"html.parser")

            tbody = data2.find('tbody', attrs={'class':None})
            listem = tbody.findAll('tr', attrs={'class':None})

            for d in listem:
                sublink = d.find('td', attrs={'class':'a1'}).find('a').get('href')
                fullx = d.find('td', attrs={'class':'a1'}).findAll('span')[1].text.strip()
                if "S"+sezon+"E"+bolum in fullx and grup in fullx.lower():
                    turkce.append((sublink,fullx,"tr"))
                    break
                if "S"+sezon+"E"+bolum in fullx:
                    hepsi.append((sublink,fullx,"tr"))

            if turkce:
                download_sub(turkce[0][0],yolu,mkv)
                print ("\t Finished: " + isim + " [tr] S" + sezon + "E" + bolum + " " + grup + " [" + turkce[0][1] + "]")
            else:
                secilen = let_user_pick(hepsi,1) 
                if isinstance(secilen, int):
                    download_sub(hepsi[secilen][0],yolu,mkv)
                    print ("\t Finished: " + isim + " [tr] S" + sezon + "E" + bolum + " " + grup + " [" + hepsi[secilen][1] + "]")
                else:
                    print  ("No TR subtitle for " + isim + " [tr] S" + sezon + "E" + bolum + " " + grup + " [" + degistir(surum) + "]")
    else:
        str1 = mkv.lower().replace(" ", ".").replace("blu-ray", "bluray").replace(".proper","").replace(".repack","").replace(".rosubbed","").replace(".korsub","")
        isim = re.search(r".{1,}.[0-9]{4}\.", str1, re.IGNORECASE).group()[:-6].replace(".","-")
        year = re.search(r"[0-9]{4}\.", str1, re.IGNORECASE).group()[:-1]

        #scraper = .create_scraper() 
        dizilink = "http://www.turkcealtyazi.org/mov/" + imdb_movsearch(isim) + "/"
        altyazilar = BeautifulSoup(requests.post(dizilink,stream=True).content,"html.parser").findAll('div', attrs={'class':'altsonsez2'})
        #altyazilar = BeautifulSoup(scraper.post(dizilink,stream=True).content,"html.parser").findAll('div', attrs={'class':'altsonsez2'})

        if altyazilar:
            print ("Searching Turkcealtyazi.org for " + mkv)
            for teker in altyazilar:
                isitme = teker.find("img", { "src" : "/images/isitme.png" })
                if isitme is not None: continue
                sublink = teker.find('div', attrs={'class':'alisim'}).find('a', attrs={'class':'underline'}).get('href')
                subdil = teker.find('div', attrs={'class':'aldil'}).find('span').get('class')[0].replace("flag","")
                subcevir = teker.find('div', attrs={'class':'alcevirmen'}).text
                subsayi = int(teker.find('div', attrs={'class':'alindirme'}).text.replace(",",""))
                subgr = teker.find('div', attrs={'class':'ripdiv'})
                subep = teker.find('div', attrs={'class':'alcd'}).text
                if int(subep) >= 2: continue
                if not subcevir: subcevir = "Yok"
                try:
                    subsur = teker.find('div', attrs={'class':'ripdiv'}).find('span').get('class')[1]
                    subgr.find('span').decompose()
                except:
                    subsur = surum.lower()
                    subgr = teker.find('div', attrs={'class':'ripdiv'})
                    
                subgr = subgr.text.strip().lower()

                if "tr" in subdil:
                    hepsi.append((sublink,safe_str(subcevir),subsayi,subsur,subgr,subdil))
            
            if hepsi:
                hepsi = sorted(hepsi, key=lambda tup: tup[3], reverse=True)
                secilen = let_user_pick(hepsi,0)
                if isinstance(secilen, int):
                    download_sub(hepsi[secilen][0],yolu,mkv)
                    print ("\t Finished: " + isim + " [" + hepsi[secilen][5] + "] <" + hepsi[secilen][1] + "> [" + degistir(hepsi[secilen][3]) + " *] \n")
                else:
                    print( "No TR subtitle for " + mkv + ". \n"   ) 
            else:
                print( "No TR subtitle for " + mkv + ". \n")
