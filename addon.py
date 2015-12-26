from xbmcswift2 import Plugin
from operator import itemgetter

from resources.lib.ftvideos.api import FTVideos, Girl, Video

import subprocess, platform

plugin = Plugin()
api = FTVideos()
pagecount = 1

@plugin.route('/')
def main_menu():
 items = [
     {'label': 'Show Models', 'path': plugin.url_for('show_girls',url="1")},
 ]
 return items

@plugin.route('/girls/<url>')
def show_girls(url):    
    pagecount = int(url)
    girls = api.get_girls(pagecount)

    print "GIRLS", len(girls)

    items = [{
        'label': girl.name,
        'path': plugin.url_for('show_girl_info', url=girl.url),
        'thumbnail' : girl.thumbnail,
        #'info' : {"Plot" : girl.description},
    } for girl in girls]

    items.insert(0, {'label' : "Previous Girls",
                   'path'  : plugin.url_for('show_girls',url=[1,pagecount-1][pagecount>1])})
    items.insert(1, {'label' : "Next Girls",
                   'path'  : plugin.url_for('show_girls',url=pagecount+1)})
    
    print "ITEMS", len(items)
   
    #sorted_items = sorted(items, key=lambda item: item['label'])
    #return sorted_items
    return items

@plugin.route('/girl/<url>/')
def show_girl_info(url):
    girl = Girl.from_url(url)

    videos = [{
        'label': video.name,
        'path': plugin.url_for('play_video', url=url),
        'is_playable': True,
        'thumbnail' : girl.thumbnail,
        'icon'      : girl.thumbnail,
        'info' : {"Plot" : girl.description, "Cast" : video.cast},
    } for video in girl.videos]

    by_label = itemgetter('label')
    sorted_items = sorted(videos, key=by_label)
    return sorted_items


@plugin.route('/videos/<url>/')
def play_video(url):
    video = Video.from_url(url)
    url = video.video_url
    plugin.log.info('Playing url: %s' % url)
    plugin.set_resolved_url(url)
    if platform.machine() == 'x86_64':
        subprocess.call(["vlc",url])

if __name__ == '__main__':
    plugin.run()
