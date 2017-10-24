# -*- coding: utf-8 -*-
import requests
from lxml import html
#import urllib
import urllib2
from urllib2 import HTTPError
import os
import sys
from PIL import Image
import json
import re
import ssl

RAR_COMMAND = '"C:\\Program Files\\WinRAR\\Rar.exe" a -ep '
RAR_CMD_DESC = ' ""C:\\Program Files\\WinRAR\\Rar.exe" a -ep  "%s" "%s/*"" > null'

adulto = {'adult':'true'}

IDLE = '-'
HOLD = '='
SAVED = '#'
IMG_ERROR = 'X'
SAVE_ERROR = 'S'
FORMAT_ERROR = 'I'
MAX_WIDTH = 60


# ----------------------------------------------------------------------------------------------------------
# Funzione che raccglie la lista dei capitoli senza scaricarli.
# Risultato:
#   False - errore durante l'accesso al sito.
#
#   'manga_name' - Nome del manga
#   'main_url'   - Url del manga
#   'site_sets'  - Setting del sito
#   'all_ch' :
#       'name'   - Nome del capitolo
#       'curl'   - Url del capitolo
#
def scan_chapter_collection(
    manga_url,
    manga_name = False
):
    if not manga_name:
        url_split = manga_url.split('/')
        if url_split[-1]=="":
            manga_name = url_split[-2]
        else:
            manga_name = url_split[-1]
        
        manga_name = manga_name.replace("_"," ").title()
    
    print "\n\n----- " + manga_name +" ("+ manga_url +") -----\n"
    
    len_base_url = len(manga_url)
    
    
    site_sets = {}
    site_sets['base_name'] = ""
    if manga_url.find("mangahere") >= 0:
        site_sets['path_1']   = "//div[@class='detail_list']//ul//span[@class='left']//a"
        site_sets['path_2']   = "(//select[@class='wid60'])[1]//option"
        site_sets['path_3']   = "//section[@id='viewer']//img[2]"
        site_sets['page_url_pattner'] = "%s/%d.html"
    elif manga_url.find("mangafox") >= 0:
        site_sets['path_1']   = "//div[@id='chapters']//ul//li//a[@class='tips']"
        site_sets['path_2']   = "(//select[@class='m'])[1]//option"
        site_sets['path_3']   = "//div[@id='viewer']//img[1]"
        site_sets['page_url_pattner'] = "%s/%d.html"
    elif manga_url.find("mangaeden") >= 0:
        site_sets['path_1']   = "//div[@id='leftContent']//tr//a[@class='chapterLink']"
        site_sets['path_2']   = "//select[@id='pageSelect']//option"
        site_sets['path_3']   = "//img[@id='mainImg']"
        site_sets['page_url_pattner'] = "%s/%d/"
        site_sets['base_name']= "http://www.mangaeden.com"
    elif manga_url.find("mangatown") >= 0:
        site_sets['path_1']   = "//div[@class='chapter_content']//ul[@class='chapter_list']//a"
        site_sets['path_2']   = "(//div[@class='page_select'])[1]//option"
        site_sets['path_3']   = "//img[@id='image']"
        site_sets['page_url_pattner'] = "%s/%d.html"
    elif manga_url.find("hastareader") >= 0:
        site_sets['path_1']   = "//div[@class='element']//div[@class='title']//a"
        site_sets['path_2']   = "//div[@class='topbar_right pull-right']//li"
        site_sets['path_3']   = "//img[@class='open']"
        site_sets['page_url_pattner'] = "%s/page/%d"
    elif False:  #preparo la roba per animegdr: Come lo identifico?
        site_sets['path_1']   = "//select[@id='capitoli']//option"
        site_sets['path_2']   = "//select[@id='pagine']//option"
        #site_sets['path_3']   = "//img[@class='open']"
        #site_sets['page_url_pattner'] = "%s/%d"
        site_sets['base_name']= "http://www.agcscanlation.it"
    elif manga_url.find("pignaquegna") >= 0:
        site_sets['path_1']   = "//div[@class='list']//div[@class='element']//div[@class='title']//a"
        site_sets['path_2']   = "//div[@class='topbar_right']//li"
        site_sets['path_3']   = "//div[@id='page']//a//img"
        site_sets['page_url_pattner'] = "%s/page/%d"
        site_sets['base_name'] = "pignaquegna"
    else: # hentaifantasy, nifteam, eagles-team, tuttoanimemanga, kireicake
        site_sets['path_1']   = "//div[@class='list']//div[@class='element']//div[@class='title']//a"
        site_sets['path_2']   = "//div[@class='topbar_right']//li"
        site_sets['path_3']   = "//img[@class='open']"
        site_sets['page_url_pattner'] = "%s/page/%d"
    
    try:
        result = requests.post(manga_url, data=adulto)
        if result.status_code != 200:
            result = requests.get(manga_url)
            if result.status_code != 200:
                print "Sito non trovato: " + str(result.status_code)
                return False
    except ConnectionError:
        print "Connessione rifiutata"
        return False
    
    page_tree = html.fromstring(result.content)
    a_elements = page_tree.xpath(site_sets['path_1'])
    
    if site_sets['base_name'] == "http://www.agcscanlation.it":
    
        a_elements = [ el.attrib['value'] for el in a_elements[1:] ]
        ch_links = [
            site_sets['base_name'] +'/reader.php?nome='+ manga_url +'&numcap='+ val
            for val in a_elements
        ]
    else:
        
        ch_links = []
        for a_element in a_elements:
            if a_element.attrib['href'][0] == "/":
                ch_link = site_sets['base_name'] + a_element.attrib['href'] #for mangaeden format
            elif a_element.attrib['href'][0] == "#":
                ch_link = manga_url + a_element.attrib['href']
            else:
                ch_link = a_element.attrib['href']
            
            if site_sets['base_name'] == "http://www.mangaeden.com": #Eccezione per mangaeden
                ch_link = ch_link[:-2]
            
            ch_links += [ ch_link ]
        
        ch_links.reverse()
    
    #print 'Ch list:\n' +  "\n\t".join([ch_link.attrib['href'] for ch_link in a_elements]) +'\n'
    print 'Ch list:\n' +  ", ".join([ch_link[len_base_url:] for ch_link in ch_links]) +'\n'
    
    data = {
        'manga_name': manga_name,
        'all_ch': [],
        'main_url': manga_url,
        'site_sets' : site_sets
    }
    
    # CILCO I CAPITOLI
    for ch_url in ch_links:
        
        ch_spec = [ch for ch in ch_url[len_base_url:].split('/')[:-1] if ch is not "" ]
        
        vol = num = None
        sub = 0
        
        if ch_spec[0] =="it":
            ch_spec = ch_spec[1:]
        
        try:
            if len(ch_spec) == 1:
                val = float(ch_spec[0])
                num = int(val)
                sub = int((val%1)*10)
                chap_name = 'c' + ( ('%05.1f' % val) if val % 1 > 0 else ('%03d' % val) )
            elif len(ch_spec) == 2:
                val = float(ch_spec[0])
                vol = val
                chap_name = 'v' + ( ('%04.1f' % val) if val % 1 > 0 else ('%02d' % val) )
                
                val = float(ch_spec[1])
                num = int(val)
                sub = int((val%1)*10)
                chap_name += ' c' + ( ('%05.1f' % val) if val % 1 > 0 else ('%03d' % val) )
            elif len(ch_spec) == 3:
                val = float(ch_spec[0])
                vol = int(val)
                chap_name = 'v' + ( ('%04.1f' % val) if val % 1 > 0 else ('%02d' % val) )
                val = int(ch_spec[1])
                num = int(val)
                chap_name += ' c' + ('%03d' % val)
                val = int(ch_spec[2])
                sub = int(val)
                chap_name += '.' + ('%d' % val)
            elif len(ch_spec) == 4:
                val = float(ch_spec[0])
                vol = int(val)
                chap_name = 'v' + ( ('%04.1f' % val) if val % 1 > 0 else ('%02d' % val) )
                val = int(ch_spec[1])
                num = val
                chap_name += ' c' + ('%03d' % val)
                val = int(ch_spec[2])
                sub = val
                chap_name += '.' + ('%d' % val)
                chap_name +" " + ch_spec[3]
            else:
                chap_name = " ".join(ch_spec)
        except:
            chap_name = " ".join(ch_spec)
            
            regex = ur"^(v([0-9]+))?( )?c([0-9]+)(\.([0-9]))?"
            sch = re.search(regex, chap_name)
            
            if sch.group(2):
                vol = int(sch.group(2))
            if sch.group(4):
                num = int(sch.group(4))
            if sch.group(6):
                sub = int(sch.group(4))
        
        data['all_ch'] += [{
            'name': chap_name,
            'curl': ch_url,
            'vol': vol,
            'num': num,
            'sub': sub
        }]
        
    return data

# ----------------------------------------------------------------------------------------------------------
# Funzione che raccglie le illagini
# Risultato:
#    0 - capitolo già esistente
#   -1 - errore nel download del capitolo
#
#   'name' - Nome del capitolo
#   'curl' - Url del capitolo
#   'imgs' - lista degli urls delle immagini
#
def scan_pages_download(
    chapter,
    manga_name,
    site_sets,
    BASE='./',
    links_flag = False,
    imgs_flag = True,
    rars_flags = True
):
    
    #if chapter['curl'][0:5] == 'https':
    #    handler = urllib2.HTTPSHandler()
    #else:
    #    handler = urllib2.HTTPHandler()
    #
    #opener = urllib2.build_opener(handler)
        
    
    try:
        os.stat(BASE + manga_name)
    except:
        os.makedirs(BASE + manga_name)
    
    dir_name = manga_name +"/"+ manga_name + " " + chapter['name']
    archive_name = dir_name + '.cbr'
    try:
        os.stat(BASE + archive_name)
        return 0    #Il capitolo esiste già e c'è già l'archivio
    except:
        post_flag = True
        result = requests.post(chapter['curl'], data=adulto)
        if result.status_code != 200:
            result = requests.get(chapter['curl'])
            post_flag = False
            if result.status_code != 200:
                print "Pagina capitolo non trovata: " + str(result.status_code)
                return -1
        
        # CREO LA CARTELLA PER LE IMMAGINI
        if imgs_flag:
            try:
                os.stat(BASE + dir_name)
            except:
                os.makedirs(BASE + dir_name)
        
        
        if links_flag:
            try:
                os.remove(BASE + dir_name +".txt")
            except:
                pass

        
        page_tree = html.fromstring(result.content)
        pages_number = len(page_tree.xpath(site_sets['path_2']))    # trovo il numero delle pagine.
        
        #with open("test.txt", 'w') as tmp:
        #    tmp.write(result.content)
        #
        #return
        
        if pages_number == False and site_sets['base_name'] == "pignaquegna":
            #TODO: vado con il sistema alternativo.
            
            riga_giusta = [riga for riga in result.content.split('\n') if riga.find('\tvar pages = ')>=0 ]
            
            dati = json.loads(riga_giusta[0].replace('\tvar pages = ','').replace(';',''))

            pages_links = [dato['url'] for dato in dati ]
            
            pages_number = len(pages_links)
            
            print "\tCh: "+ chapter['name'] +"\t*Number of pages: " + str(pages_number)
            
            # CICLO LE PAGINE DI UN CAPITOLO
            list_loading = ['-' for n in pages_links ]
            sys.stdout.write('\r\t%5.1f%% : ' % 0 )
            sys.stdout.write(''.join(list_loading[0:MAX_WIDTH]))
            sys.stdout.flush()
            
            img_urls = []
            for ix, img_tag in enumerate(pages_links):
                #print "\n\n"+img_tag.attrib['src']+"\n\n"
                if img_tag[0:2] == "//":
                    img_tag = "http:" + img_tag
                
                img_url = img_tag
                file_name = dir_name + "/" + ("%03d" % (ix+1)) + ".jpg"
                
                img_urls += [ img_url ]
                
                if imgs_flag:
                    #try:
                    #    os.stat(BASE+file_name)
                    if os.path.isfile(BASE+file_name):
                        list_loading[ix] = HOLD
                    else:
                    #except:
                        try:
                            req = urllib2.Request(img_url, None, { 'User-Agent' : 'Mozilla/5.0' })
                            img_open = urllib2.urlopen(req)
                            im = Image.open(img_open).convert('RGB')
                        except IOError:
                            list_loading[ix] = IMG_ERROR
                            im = False
                        
                        if im:
                            try:
                                im.save(BASE+file_name, 'jpeg')
                                list_loading[ix] = SAVED
                            except IOError:
                                list_loading[ix] = SAVE_ERROR
                                os.remove(BASE+file_name)
            
                if links_flag:
                    url_list = open(BASE+dir_name +".txt", 'a')
                    url_list.write(img_url + '\n')
                    url_list.close()
            
                sys.stdout.write('\r\t%5.1f%% : ' % (float(ix+1)/float(pages_number)*100.0) )
                sys.stdout.write(''.join(list_loading[0:MAX_WIDTH]))
                sys.stdout.flush()
            
        else:

            pages_links = [ chapter['curl'] ]
            
            pages_links += [
                site_sets['page_url_pattner'] % ( '/'.join(chapter['curl'].split('/')[:-1]), ix+1 )
                for ix in range(1, pages_number)
            ]
            
            #pages_links = [('/'.join(chapter['curl'].split('/')[:-1])+"/"+site_sets['page_pre']+str(ix+1)+site_sets['page_ext']) for ix in range(0, pages_number)]
            
            print "\tCh: "+ chapter['name'] +"\tNumber of pages: " + str(pages_number)
            
            
            
            # CICLO LE PAGINE DI UN CAPITOLO
            list_loading = ['-' for n in pages_links ]
            sys.stdout.write('\r\t%5.1f%% : ' % 0 )
            sys.stdout.write(''.join(list_loading[0:MAX_WIDTH]))
            sys.stdout.flush()
            
            img_urls = []
            for ix, img_page_url in enumerate(pages_links):
                #print "\n\n"+img_page_url+"\n\n"
                file_name = dir_name + "/" + ("%03d" % (ix+1)) + ".jpg"
                
                if os.path.isfile(BASE+file_name):
                    list_loading[ix] = HOLD
                    
                else:
                
                    if post_flag:
                        result = requests.post(img_page_url, data=adulto)
                    else:
                        result = requests.get(img_page_url)
                    
                    if result.status_code != 200:
                        #print "Pagina immagine non trovata: " + str(result.status_code)
                        list_loading[ix] = IMG_ERROR
                        post_flag = True
                            
                    else:
                        page_tree = html.fromstring(result.content)
                        if len(page_tree.xpath(site_sets['path_3']))<1:
                            #print "Immagine non trovata"
                            list_loading[ix] = FORMAT_ERROR
                        else:
                            
                            img_tag = page_tree.xpath(site_sets['path_3'])[0]
                            
                            #print "\n\n"+img_tag.attrib['src']+"\n\n"
                            if img_tag.attrib['src'][0:2] == "//":
                                img_tag.attrib['src'] = "http:" + img_tag.attrib['src']
                            
                            #sys.stdout.write(img_tag.attrib['src'] + " ")
                            img_url = img_tag.attrib['src'].replace(' ','%20')
                            
                            img_urls += [ img_url ]
                            
                            
                            if imgs_flag:
                                try:
                                    img_open = urllib2.urlopen(img_url)
                                    im = Image.open(img_open).convert('RGB')
                                except IOError:
                                    list_loading[ix] = IMG_ERROR
                                    im = False
                                    #print("\n\t\tImg corrupted")
                                
                                if im:
                                    try:
                                        im.save(BASE+file_name, 'jpeg')
                                        list_loading[ix] = SAVED
                                    except IOError:
                                        list_loading[ix] = SAVE_ERROR
                                        os.remove(BASE+file_name)
                    
                    if links_flag:
                        url_list = open(BASE+dir_name +".txt", 'a')
                        url_list.write(img_url + '\n')
                        url_list.close()
                
                sys.stdout.write('\r\t%5.1f%% : ' % (float(ix+1)/float(pages_number)*100.0) )
                sys.stdout.write(''.join(list_loading[0:MAX_WIDTH]))
                sys.stdout.flush()
            
        
        # CREO L'ARCHIVIO E RIMUOVO LE IMMAGINI (SE E SOLO SE HO TROVATO TUTTE LE IMG)
        ch_data = chapter
        ch_data['imgs'] = img_urls
        
        if imgs_flag:
            files_list = os.listdir(BASE+dir_name)
            if len(files_list) >= pages_number:
                
                if rars_flags:
                    #os.system(' "'+RAR_COMMAND+' "'+ BASE + archive_name +'" "' + BASE+dir_name + '/*"" > null')
                    os.system( RAR_CMD_DESC%(BASE+archive_name, BASE+dir_name) )
                    print "\n\tArchivio correttamente realizzato"
                    for ans in files_list:
                        os.remove(BASE+dir_name+"/"+ans)
                    os.rmdir(BASE+dir_name)
            else:
                print "\nMancano delle pagine."
                return -1
        
        print '\n'
    
    return ch_data

# ----------------------------------------------------------------------------------------------------------
# Funzione che scarica dal sito SNAFU (al momento lo uso solo per Grim Tales)
# Risultato:
#   n - numero dell'ultima pagina
#
def snafu_download(
    first_page, # Sovascritta nel caso esista già il manga
    name,
    BASE='./'
):

    dir_name = name
    ix = 0
    
    print "\n\n----- " + name +" ("+ first_page +") -----\n"
    
    try:
        os.stat(BASE + dir_name)
    except:
        os.makedirs(BASE + dir_name)

    try:
        with open( BASE + dir_name+'/'+dir_name + " lp.txt",'r') as last_page_file:
            line = last_page_file.readline().split('\t')
        first_page = line[0]
        ix = int(line[1])
        print "Riprendo da: " + first_page
        
    except IOError:
        pass
    

    next_page = True
    next_link = first_page
    headers = { 'User-Agent' : 'Mozilla/5.0' }
    
    old_ix = ix
    while next_page:
    
        last_name = next_link.split('/')[-2]
        
        file_name = dir_name +'/'+ (" %04d - " % ix) + last_name +'.jpeg'
        print file_name
        
        page_tree = html.fromstring(requests.get(next_link).content)
        next_page = page_tree.xpath("(//div[@id='navarea1']//a[@class='previous'])")
        if next_page:
            next_link = next_page[0].attrib['href']
        
        img_url = page_tree.xpath("(//div[@class='comicpage']//img[@class='bs'])")[0].attrib['src']
        img_url = 'http:' + img_url
        #print img_url
        try:
            req = urllib2.Request(img_url, None, headers)
            img_open = urllib2.urlopen(req)
            im = Image.open(img_open).convert('RGB')
        except IOError:
            print "ERRORE ------------------------------\n\n"
            im = False
        im.save(BASE+file_name, 'jpeg')
        with open( BASE + dir_name+'/'+dir_name + " lp.txt",'w') as last_page_file:
            last_page_file.write(next_link + '\t' + str(ix) +'\n')
        ix += 1
        
        #TODO: Mettere un sistema per archiviare i capitoli
        #if (ix%page_per_chapter) == 0:
        #    print "Nuovo capitolo"
        #    ch_number = int(ix/page_per_chapter)
        #    archive_name = dir_name + (" c%03d" % ch_number)
        #    if rars_flags:
        #        os.system(' "'+RAR_COMMAND+' "'+ BASE+dir_name + archive_name +'" "' + BASE+dir_name + '/*.jpg"" > null')
                

    print "Ultima pagina: " + next_link
    if ix == old_ix+1:
        return 0
    else:
        return ix-1


def ergo_team_download(
    name,
    tag,
    BASE='./'
):
    addres_string = "http://ergoreader.altervista.org/reader.php?chapter=%02d&series=%s"
    
    img_string = "http://ergoreader.altervista.org/files/%s/%d/%02d.png"
    
    tag = "kodomo"
    chs = range(68, 73)
    try:
        os.stat(BASE + name)
    except:
        os.makedirs(BASE + name)
    
    for ch in chs:
        base_name = name + "/" + name + "_c%03d/"%ch
        
        try:
            os.stat(BASE + base_name)
        except:
            os.makedirs(BASE + base_name)
        
        for numb_page in range(1,200):
        
            file_name = base_name + "%03d.jpeg"%numb_page
            
            img_url = img_string%(tag, ch, numb_page)
            
            try:
                img_open = urllib2.urlopen(img_url)
            except HTTPError:
                break
        
            im = Image.open(img_open).convert('RGB')
            im.save(BASE+file_name, 'jpeg')
    
    return
# ----------------------------------------------------------------------------------------------------------
# ---- MAIN ------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    
    manga_urls = []

    if len(sys.argv)>1:
        manga_urls = [ arg for arg in sys.argv[1:] ]
    else:
        while 1:
            input_var = raw_input("Inserisci un url [invio per terminare]:\n")
            if input_var == "":
                break
            manga_urls += [(input_var, False)]

    if manga_urls == []:
        file = open("download_list.txt","r")
        string = file.read()
        manga_list = string.split('\n')
        manga_urls = []
        for manga_list_line in manga_list:
            temp = manga_list_line.split('\t')
            manga_urls += [ (temp[0], temp[1] if len(temp)==2 else False) ]
            
    BASE = "./"
    for manga_url in manga_urls:
        if manga_url[0][0] =='[':
            BASE = manga_url[0][1:-1] + '/'
            continue
        if manga_url[0][0] =='#':
            continue

        if manga_url[0].find("snafu-comics.com") >= 0:
            ix = snafu_download.snafu_download(manga_url[0], manga_url[1], BASE)
            
        else:
            data = scan_chapter_collection(manga_url[0], manga_url[1])
            if data:
                for chapter in data['all_ch']:
                    scan_pages_download( chapter, data['manga_name'], data['site_sets'], BASE, links_flag = True)
            else:
                print "Errore con il manga " + manga_url[1]
    