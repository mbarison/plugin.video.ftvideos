'''
    ftvideos.scraper
    ~~~~~~~~~~~~~~~~~~~~~

    This module contains some functions which do the website scraping for the
    API module. You shouldn't have to use this module directly.
'''
import re
import os
from urllib import unquote
from urllib2 import urlopen
from urlparse import urljoin
from BeautifulSoup import BeautifulSoup as BS

video_ptn   = re.compile("(http.+?mp4)")
thumb_ptn   = re.compile("(http://cdn.ftvgirls.com/.+?jpg)")

BASE_URL = 'http://www.ftvgirls.com'
def _url(path):
    '''Returns a full url for the given path'''            
    return urljoin(BASE_URL, path)


def get(url):
    '''Performs a GET request for the given url and returns the response'''
    conn = urlopen(url)
    resp = conn.read()
    conn.close()
    return resp


def _html(url):
    '''Downloads the resource at the given url and parses via BeautifulSoup'''
    return BS(get(url), convertEntities=BS.HTML_ENTITIES)


def make_showall_url(url):
    '''Takes an api url and appends info to the path to force the page to
    return all entries instead of paginating.
    '''
    if not url.endswith('/'):
        url += '/'
    return url + 'page:1/show:500'


def get_girl_name(url):
    # split into components
    _n = os.path.basename(url).split('-')
    _n2 = []
    for i in _n:
        if i=='i' or i=='ii':
            _n2.append(i.upper())
        else:
            _n2.append(i.capitalize())
    return " ".join(_n2[:-1])
    
def get_girl_name2(html):
    return html.find("a", {"class" : "jackbox"}).attrMap["data-title"]

def get_girls(url):
    '''Returns a list of girls for the website. Each girl is a dict with
    keys of 'name' and 'url'.
    '''
    url = _url(url)
    html = _html(url)
    #subjs = html.findAll('a',
    #    {'href': lambda attr_value: attr_value.startswith('/update/')
    #                                and len(attr_value) > len('/update/')})

    subjs = html.findAll('div', {'class' : 'relatedContainer'})

    # subjs will contain some duplicates so we will key on url
    items = []
    urls = set()
    for subj in subjs:
        #url = unquote(_url(subj['href']))
        url = unquote(_url(subj.a['href']))
        if url not in urls:
            urls.add(url)
            items.append({
                'name': get_girl_name(url),
                'url': url,
                'thumbnail' : subj.img['src'],
            })

    #print items

    # filter out any items that didn't parse correctly
    return [item for item in items if item['name'] and item['url']]


def get_girl_metadata(girl_url):
    '''Returns metadata for a girl parsed from the given url'''
    #html = _html(make_showall_url(girl_url))
    html = _html(girl_url)
    name = get_girl_name(girl_url)
    videos = get_videos(html)
    desc = get_girl_description(html)
    age,height,figure = getBioStats(html)

    _info =  {
        'name': name,
        'age' : age,
        'height' : height,
        'figure' : figure,
        'description' : desc,
        'videos'      : videos,
    }
    #print _info
    return _info

def getBioStats(html):
    _stats = html.find("div", {"id" : "BioHeader"}).h2.text.split("|")
    return(_stats[0],_stats[1],_stats[2])

def get_video_name(html):
    #return html.find('section', {'class': 'pagenav'}).span.text
    node = html.find('a', {'class': 'jackbox'})
    return os.path.basename(video_ptn.findall(node.__repr__())[0])

def get_girl_description(html):
    #desc_nodes = html.find('article').findAll('span')
    #return '\n'.join(node.text.strip() for node in desc_nodes)
    return html.find("div", {"id" : "Bio"}).p.text

def get_videos(html):
    nodes = html.findAll('a', {'class': 'jackbox'})

    items = [{
        #'name': os.path.basename(video_ptn.findall(node.__repr__())[0]),
        'name' : html.find("title").text,
        #'url':  video_ptn.findall(node.__repr__())[0],
        #'icon': node.img['src'],
        #'university':  '',
        #'speaker': '',
    } for node in nodes]

    return items


def get_video_metadata(url):
    print "METADATA FOR", url
    html = _html(url)
    name = html.find("title").text #get_video_name(html)
    video_url = parse_video_url(html)
    thumb_url = parse_thumb_url(html)
    return {
        'name': name,
        'video_url': video_url,
        'thumbnail' : thumb_url,
        'cast'      : get_cast(html),
    }
    


def parse_video_url(html):
    node = html.find('a', {'class': 'jackbox'})
    match = video_ptn.search(node.__repr__())
    if match:
        return match.group(1)
    return None

def parse_thumb_url(html):
    node = html.find('a', {'class': 'jackbox'})
    match = thumb_ptn.search(node.__repr__())
    if match:
        return match.group(1)
    return None

def get_cast(html):
    girls = html.find("div", {"id" : "BioHeader"}).findAll("h1")
    stats = html.find("div", {"id" : "BioHeader"}).findAll("h2")
    #print girls
    #print stats
    #print ["%s %s" % (i[0].text.split("'")[0],i[1].text) for i in zip(girls,stats)]
    return ["%s %s" % (i[0].text.split("'")[0],i[1].text) for i in zip(girls,stats)]
