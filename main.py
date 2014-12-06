# coding: utf-8
from pulsar import provider
from urllib import unquote_plus
import re
import common

# this read the settings
settings = common.Settings()
# define the browser
browser = common.Browser()
# create the filters
filters = common.Filtering()
# special settings
values2 = {"ALL":'1_0',"English translations":'1_37',"Non English translations":'1_38' ,"Raw":'1_11'} # read category
category = values2[provider.ADDON.getSetting('category')]

# using function from Steeve to add Provider's name and search torrent
def extract_torrents(data):
    try:
        filters.information()  # print filters settings
        data = common.clean_html(data)
        name = re.findall(r'/.page=view&#..;tid=(.*?)>(.*?)</a></td>',data) # find all names
        size = re.findall(r'<td class="tlistsize">(.*?)</td>',data) # find all sizes
        cont = 0
        for cm, torrent in enumerate(re.findall(r'/.page=download&#..;tid=(.*?)"', data)):
            #find name in the torrent
            if re.search(r'Searching torrents',data) is not None:
                if filters.verify(name[cm][1], size[cm]):
                        yield { "name": name[cm][1] + ' - ' + size[cm] + ' - ' + settings.name_provider,"uri": settings.url + '/?page=download&tid=' + torrent}
                        cont+= 1
                else:
                    provider.log.warning(filters.reason)
                if cont == settings.max_magnets:  # limit magnets
                    break
        provider.log.info('>>>>>>' + str(cont) + ' torrents sent to Pulsar<<<<<<<')
    except:
        provider.log.error('>>>>>>>ERROR parsing data<<<<<<<')

def search(query):
    global filters
    filters.title = query  # to do filtering by name
    query += ' ' + settings.extra
    if settings.time_noti > 0: provider.notify(message="Searching: " + query.title() + '...', header=None, time=settings.time_noti, image=settings.icon)
    query = provider.quote_plus(query)
    url_search = "%s/?page=search&cats=%s&term=%s&sort=2" % (settings.url,category,provider.quote_plus(query))  # change in each provider
    provider.log.info(url_search)
    if browser.open(url_search):
        results = extract_torrents(browser.content)
    else:
        print browser.status
        results = []
    return results

def search_movie(info):
    return []

def search_episode(info):
    filters.use_TV()
    query =  common.clean(info['title']) + ' %02d' % info['absolute_number']  # define query
    return search(query)

# This registers your module for use
provider.register(search, search_movie, search_episode)