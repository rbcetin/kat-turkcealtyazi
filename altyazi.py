#!/usr/bin/env python
# -*- coding: utf-8-sig -*-
import requests,json,sys,os,re
from time import sleep

def imdb_search(name,year,tip):
    if tip is None: # meaning that it is a movie
        r = requests.get('https://api.themoviedb.org/3/search/movie?api_key=a0a4437eea1890fcffee70f77f38d496&language=en-US&query='+name+'&page=1', timeout=1)
        d  = r.json()
        myid = d["results"][0]["id"]

        for dat in d["results"]:
            if year == dat["release_date"][:4]:
                myid = dat["id"]
                break
            
        tom_index = next((index for (index, d) in enumerate(d["results"]) if d["id"] == myid), None)       
        title = d["results"][tom_index]["original_title"]
        date =  d["results"][tom_index]["release_date"]
                
        r = requests.get('https://api.themoviedb.org/3/movie/'+str(myid)+'?api_key=a0a4437eea1890fcffee70f77f38d496&language=en-US', timeout=1)
        d  = r.json()
    else: # tv series
        r = requests.get('https://api.themoviedb.org/3/search/tv?api_key=a0a4437eea1890fcffee70f77f38d496&language=en-US&query='+name+'&page=1', timeout=1)
        d  = r.json()
        myid = d["results"][0]["id"]
        
        if year is not None:
            for dat in d["results"]:
                if year == dat["first_air_date"][:4]:
                    myid = dat["id"]
                    break
                
        tom_index = next((index for (index, d) in enumerate(d["results"]) if d["id"] == myid), None)       
        title = d["results"][tom_index]["original_name"]
        date =  d["results"][tom_index]["first_air_date"]
        
        r = requests.get('https://api.themoviedb.org/3/tv/'+str(myid)+'/external_ids?api_key=a0a4437eea1890fcffee70f77f38d496&language=en-US', timeout=1)
        d  = r.json()

    return [d["imdb_id"][2:],title,date]

def randomString(stringLength=10):
    import string
    import random
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))

def filedetails(file):
    returndict = dict()
    file = file.lower().replace(" ",".").replace("-",".")

    episode = None
    season = None
    resolution = None
    name = None
    edited = None
    year = None
    vers = None
    group = file.split(".")[-2]

    if file.find("webrip") > 0:
        vers = "webrip"
    elif file.find("web-dl") > 0:
        vers = "web-dl"
    elif file.find("web") > 0:
        vers = "web"
    elif file.find("bluray") > 0:
        vers = "bluray"
    elif file.find("blu-ray") > 0:
        vers = "bluray"
    elif file.find("hdtv") > 0:
        vers = "hdtv"
    elif file.find("bdrip") > 0:
        vers = "bdrip"
    elif file.find("hdrip") > 0:
        vers = "hdrip"
        
    if file.find("repack") > 0:
        edited = "repack"
    elif file.find("real") > 0:
        edited = "real"
    elif file.find("proper") > 0:
        edited = "proper"

    if re.findall(r"[0-9]{4}\.", file):
        year = re.findall(r"[0-9]{4}\.", file)[-1].replace(".","")
        
    if re.search(r"[0-9]{3,4}p",file):
        resolution = re.search(r"[0-9]{3,4}p",file)[0]
            
    if re.search(r"s[0-9]{1,2}", file):
        season = re.search(r"s[0-9]{1,2}", file)[0].replace("s","")
        episode = re.search(r"e[0-9]{1,2}", file)[0].replace("e","")

    if episode is None:
        name = re.search(r"(.*)(?="+str(year)+")",file)[0].replace("."," ")
    else:
        name = re.search(r"(.*)(?=s[0-9]{1,2})",file)[0].replace("."," ")

    name = name[:-1]
    imdb = imdb_search(name,year,season)
    
    returndict["imdb"] = imdb[0]
    returndict["orj_name"] = imdb[1]
    returndict["releasedate"] = imdb[2]
    returndict["name"] = name
    returndict["year"] = year
    returndict["vers"] = vers
    returndict["res"] = resolution
    returndict["group"] = group
    returndict["season"] = season
    returndict["episode"] = episode
    returndict["edited"] = edited
    
    return returndict

def download_sub(link,yol,mkv):
    from bs4 import BeautifulSoup
    randfold = randomString()
    os.mkdir(yol+randfold)
    
    if "http" in link:
        print("\t Downloading from opensubtitles.org.")
        filen = link.split('/')[-1]
        r = requests.get(link, stream=True)
        with open(yol+randfold+"//"+filen, 'wb') as fd:
            for chunk in r.iter_content(chunk_size=512):
                fd.write(chunk)
        filename = max([yol+randfold + "\\" + f for f in os.listdir(yol+randfold)],key=os.path.getctime)
        local_name = filename
        print("\t Downloaded file: " + str(local_name))
    else:
        print("\t Downloading from turkcealtyazi.org.")
        url = "https://www.turkcealtyazi.org/" + link
        indir_keys = BeautifulSoup(requests.get(url, timeout=3).content,"html.parser").find('form', action='/ind').findAll('input', attrs={'type': 'hidden'})     
        form_data = {}
        for k in indir_keys:
            form_data[k['name']] = k['value']
        f = requests.post("https://turkcealtyazi.org/ind", data=form_data, stream = True)
        if f.status_code == 200:
            if 'Content-Disposition' in f.headers:
                local_name = f.headers['Content-Disposition'].split('filename=')[1].strip('"\'')
            else:
                local_name = 'test.zip'
                raise ValueError("Couldn't Get The File")
            
            local_tmp_file = os.path.join(yol+randfold, str(randfold) + local_name)
            
            with open(local_tmp_file, 'wb') as outfile:
                for chunk in f.iter_content(1024):
                    outfile.write(chunk)
        else:
            raise ValueError("Couldn't Get The File")
        local_name = local_tmp_file
        
    return local_name


def handlezip(local_name,yol,mkv):
    from pyunpack import Archive
    import shutil
    import codecs
    import glob
    
    def isUTF8(data):
        try:
            decoded = data.decode('UTF-8')
        except UnicodeDecodeError:
            return False
        else:
            for ch in decoded:
                if 0xD800 <= ord(ch) <= 0xDFFF:
                    return False
            return True
        
    def get_bytes_from_file(filename):
        return open(filename, "rb").read()

    
    currentpath = local_name.rsplit('\\', 1)[0] + "\\"
    
    print("\t Extracting the archive: " + str(local_name))
    Archive(local_name).extractall(currentpath)

    if local_name.endswith(".gz"):
        zipfiles = [f for f in glob.glob(currentpath + "\\"+"*")]
        extractedfile = zipfiles[0]
    else:
        zipfiles = [f for f in glob.glob(currentpath + "\\"+"*.srt")]
        if len(zipfiles) == 1:
            extractedfile = zipfiles[0]
        else:
            tobefound = re.search(r"s[0-9]{1,2}.e[0-9]{1,2}", mkv.lower())[0]
            for correct in zipfiles:
                if tobefound in correct.lower():
                    extractedfile = correct       

    print("\t Renaming the file: " +str(extractedfile))
    
    fullpath = yol+mkv[:-4]+".tr.srt"
        
    os.rename(extractedfile, fullpath)

    result = isUTF8(get_bytes_from_file(fullpath))
    if result is False:
        with codecs.open(fullpath, 'r', encoding='windows-1254', errors='ignore') as f:
            text = f.read()
        with codecs.open(fullpath, 'w', encoding='utf-8') as f:
            f.write(text)
    
    print ("\t Removing: " + local_name.rsplit('\\', 1)[-1])
    shutil.rmtree(currentpath)
            

def subprint(idx,element):
    from colorama import init
    from colorama import Fore, Back, Style
    init(autoreset=True)
    color = "\033[37;41;2m"            
    if element[-1] == 100:
        color = "\033[36;45;1m"        
    elif element[-1] == 90:
        color = "\033[42m"
    elif element[-1] == 80:
        color = "\033[43m"
    elif element[-1] == 0:
        color = "\033[44m"
        
    if element[6] is None or element[6] == str(0): # Season is None so it is Movie
        print ("\t"+color+" (" + str(idx+1) + ") "
               + str(element[0])  +
               " [" + str(element[2]) + "] [" + str(element[8]).upper() + " "+str(element[7])+"] %" + str(element[-1]))
    else:
        print ("\t"+color+" (" + str(idx+1) + ") "
               + str(element[0])  +
               " [" + str(element[2]) + "] S" + str(element[6]) + "E" + str(element[5]) + " [" + str(element[8]).upper() + " "+str(element[7])+"] %" + str(element[-1]))            

def let_user_pick(options,no):

    print("Found subtitles:")
    for idx, element in enumerate(options):
        subprint(idx,element)
        
    i = input("Input number: ")
    try:
        if 0 < int(i) <= len(options):
            return int(i)-1
        else:
            return False
    except:
        return False

def process_TAorg(name,imdbid,season,group,vers,episode):
    from bs4 import BeautifulSoup

    def updatevers(vers):
        newvers = vers.replace("r3", "DVDScr").replace("r10", "HDTS").replace("r8", "WEB-DL").replace("r6", "WEBRip").replace("r1", "HD/Bluray").replace("r2", "DVDRip").replace("r9", "HDRip").replace("r7", "BDRip/Bluray")
        return newvers.lower()

    if season is None:
        searchClass = "altsonsez2"
    else:
        if int(season) < 10:
            season = season[1:]
        searchClass = 'sezon_'+season
                
    link = "http://www.turkcealtyazi.org/mov/" + imdbid + "/"
    subtitles = BeautifulSoup(requests.get(link,stream=True, timeout=3).content,"html.parser").findAll('div', attrs={'class':searchClass})
    trsubtitlelist = list()
    ensubtitlelist = list()
        
    if subtitles:
        for teker in subtitles:
            isitme = teker.find("img", { "src" : "/images/isitme.png" })
            if isitme is not None: continue
            
            subhref = teker.find('div', attrs={'class':'alisim'}).find('a', attrs={'class':'underline'}).get('href')
            sublang = teker.find('div', attrs={'class':'aldil'}).find('span').get('class')[0].replace("flag","")
            subtrns = teker.find('div', attrs={'class':'alcevirmen'}).text
            subdown = int(teker.find('div', attrs={'class':'alindirme'}).text.replace(",",""))
            subep = None if season is None else teker.find('div', attrs={'class':'alcd'}).findAll('b')[1].text

            subgr = teker.find('div', attrs={'class':'ripdiv'})

            try:
                subvers = teker.find('div', attrs={'class':'ripdiv'}).find('span').get('class')[1]
                subgr.find('span').decompose()
            except:
                subvers = vers.lower()
                subgr = teker.find('div', attrs={'class':'ripdiv'})
            subgr = subgr.text.strip().lower()

            subvers = updatevers(subvers)
            
            if subep == episode or subep == "Paket":
                if "tr" == sublang:
                    if group in subgr:
                        if vers in subvers: # in because web can be web-dl or webrip
                            trsubtitlelist.append(["TA "+name,subhref,sublang,subtrns,subdown,subep,season,subgr,subvers,100]) # Both matches #1
                            break
                        else:
                            trsubtitlelist.append(["TA "+name,subhref,sublang,subtrns,subdown,subep,season,subgr,subvers,80]) # Only Group matches #3
                    else:
                        if vers in subvers: 
                            trsubtitlelist.append(["TA "+name,subhref,sublang,subtrns,subdown,subep,season,subgr,subvers,90]) # Version matches #2
                        else:
                            trsubtitlelist.append(["TA "+name,subhref,sublang,subtrns,subdown,subep,season,subgr,subvers,0]) # Nothing matches #4
                else:
                    if group in subgr:
                        if vers in subvers: # in because web can be web-dl or webrip
                            ensubtitlelist.append(["TA "+name,subhref,sublang,subtrns,subdown,subep,season,subgr,subvers,100]) # Both matches #1
                        else:
                            ensubtitlelist.append(["TA "+name,subhref,sublang,subtrns,subdown,subep,season,subgr,subvers,80]) # Only Group matches #3
                    else:
                        if vers in subvers: 
                            ensubtitlelist.append(["TA "+name,subhref,sublang,subtrns,subdown,subep,season,subgr,subvers,90]) # Version matches #2
                        else:
                            ensubtitlelist.append(["TA "+name,subhref,sublang,subtrns,subdown,subep,season,subgr,subvers,0]) # Nothing matches #4


    if len(trsubtitlelist) > 0:
        subtitlelistTA = sorted(trsubtitlelist, key=lambda tup: (tup[-1],tup[4]), reverse=True)
    else:
        subtitlelistTA = sorted(ensubtitlelist, key=lambda tup: (tup[-1],tup[4]), reverse=True)

    return subtitlelistTA

def processOS(filename,detay):
    from pythonopensubtitles.opensubtitles import OpenSubtitles
    from pythonopensubtitles.utils import File
    trsubtitlelist = list()
    ensubtitlelist = list()
    
    ost = OpenSubtitles() 
    ost.login('katates', 'hijuhiji')
    f = File(filename)
    data = ost.search_subtitles([{'imdbid': detay["imdb"],'season': detay["season"],'episode': detay["episode"],'sublanguageid': 'tur,eng','tag':detay["group"]+","+detay["vers"]}])
    for sub in data:
        realep = detay["episode"]
        
        name = "OS "+detay["name"]
        subhref = sub["SubDownloadLink"]
        sublang = sub["LanguageName"].replace("English","en").replace("Turkish","tr")
        subtrns = sub["SubTranslator"]
        subdown = int(sub["SubDownloadsCnt"])
        subep = sub["SeriesEpisode"]
        season = sub["SeriesSeason"]
        subgr = sub["InfoReleaseGroup"].lower()
        subvers = sub["InfoFormat"].lower()

        if int(realep) < 10:
            realep = realep[1:]
            

        if subep == realep:
            if "tr" == sublang:
                if detay["group"] in subgr:
                    if detay["vers"] in subvers: # in because web can be web-dl or webrip
                        trsubtitlelist.append([name,subhref,sublang,subtrns,subdown,subep,season,subgr,subvers,100]) # Both matches #1
                        break
                    else:
                        trsubtitlelist.append([name,subhref,sublang,subtrns,subdown,subep,season,subgr,subvers,80]) # Only Group matches #3
                else:
                    if detay["vers"] in subvers: 
                        trsubtitlelist.append([name,subhref,sublang,subtrns,subdown,subep,season,subgr,subvers,90]) # Version matches #2
                    else:
                        trsubtitlelist.append([name,subhref,sublang,subtrns,subdown,subep,season,subgr,subvers,0]) # Nothing matches #4
            else:
                if detay["group"] in subgr:
                    if detay["vers"] in subvers: # in because web can be web-dl or webrip
                        ensubtitlelist.append([name,subhref,sublang,subtrns,subdown,subep,season,subgr,subvers,100]) # Both matches #1
                    else:
                        ensubtitlelist.append([name,subhref,sublang,subtrns,subdown,subep,season,subgr,subvers,80]) # Only Group matches #3
                else:
                    if detay["vers"] in subvers: 
                        ensubtitlelist.append([name,subhref,sublang,subtrns,subdown,subep,season,subgr,subvers,90]) # Version matches #2
                    else:
                        ensubtitlelist.append([name,subhref,sublang,subtrns,subdown,subep,season,subgr,subvers,0]) # Nothing matches #4

    if len(trsubtitlelist) > 0:
        subtitlelistOS = sorted(trsubtitlelist, key=lambda tup: (tup[-1],tup[4]), reverse=True)
    else:
        subtitlelistOS = sorted(ensubtitlelist, key=lambda tup: (tup[-1],tup[4]), reverse=True)
    
    return subtitlelistOS


if __name__ == '__main__':
    import webbrowser

    path = sys.argv[1].rsplit('\\', 1)[0] + "\\"
    mkv = sys.argv[1].split('\\', -1)[-1]
    
    while(1):
        try:
            print("Trying to get metadata for " + mkv)
            detay = filedetails(mkv)
            break
        except Exception as e:
            sleep(0.2)
            print(e)
            pass

    print("Metadata found. IMDB: " + str(detay["imdb"]) + " Title: " + str(detay["orj_name"]) + " Date: " + str(detay["releasedate"]))
    
    try:
        print("Searching Turkcealtyazi.org for " + mkv)
        subtitlelistTA = process_TAorg(detay["name"],detay["imdb"],detay["season"],detay["group"],detay["vers"],detay["episode"])
        try:
            print("Searching Opensubtitles.org for " + mkv)
            subtitlelistOS = processOS(sys.argv[1],detay)
            subtitlelist = subtitlelistTA + subtitlelistOS
        except:
            subtitlelist = subtitlelistTA
            print("Opensubtitles.org failed.")
    except:
        print("Search failed.")
        subtitlelist = None


    try:
        trsubtitlelist = [i for i in subtitlelist if i[2] == "tr"]
        if len(trsubtitlelist) > 0:
            subtitlelist = trsubtitlelist
            
        subtitlelist = sorted(subtitlelist, key=lambda tup: (tup[-1],tup[4]), reverse=True)
        
        hundred = [i for i in subtitlelist if i[-1] == 100]
        
        if len(hundred) > 0:
            subtitlelist = hundred
    except:
        subtitlelist = None
    
    if subtitlelist is not None:
        while(1):
            if len(subtitlelist) == 1:
                selected = 0
                subprint(selected,subtitlelist[selected])
            else:
                selected = let_user_pick(subtitlelist,0)
            if selected is not False:
                break
            
        if isinstance(selected, int):
            try:
                filedownloaded = download_sub(subtitlelist[selected][1],path,mkv)
                handlezip(filedownloaded,path,mkv)
            except Exception as e:
                print(e)
                webbrowser.get("C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s").open("https://www.turkcealtyazi.org/"+subtitlelist[selected][1])

        print ("\t Finished: " +  str(subtitlelist[selected][0]) + " [" +  str(subtitlelist[selected][2]) + "] S" +  str(subtitlelist[selected][6]) + "E" +  str(subtitlelist[selected][5]) + " [" + str(subtitlelist[selected][8].upper()) + " " + str(subtitlelist[selected][7]) + "] \n")
    else:
        webbrowser.get("C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s").open("https://turkcealtyazi.org/mov/"+detay["imdb"]+"/")
