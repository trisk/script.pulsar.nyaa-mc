from pulsar import provider

# this read the settings
url = provider.ADDON.getSetting('url_address')
icon = provider.ADDON.getAddonInfo('icon') # gets icon
anime_quality = provider.ADDON.getSetting('anime_quality') # read quality from anime
values2={"ALL":'1_0',"English translations":'1_37',"Non English translations":'1_38' ,"Raw":'1_11'} # read category
category = values2[provider.ADDON.getSetting('category')]
extra = provider.ADDON.getSetting('extra')
max_magnets = int(provider.ADDON.getSetting('max_magnets'))  #max_magnets
values3 = {'ALL': 0, 'HDTV': 1,'480p': 1,'DVD': 1,'720p': 2 ,'1080p': 3, '3D': 3, "1440p": 4 ,"2K": 5,"4K": 5} #code_resolution steeve

# it gets the absolute_number_episode
def convert_episode_season(tvdb_id,season,episode):
	from xml.etree import ElementTree
	page=provider.GET('http://thetvdb.com/api/1D62F2F90030C444/series/' + tvdb_id + '/all/en.xml')
	pageXML = ElementTree.fromstring(page.data)
	results=str(episode)
	total=0
	for item in pageXML.findall('Episode'):
		if item[10].text == str(episode) and item[19].text==str(season):
			if item[21].text is not None:
				results=item[21].text
		if item[21].text is not None:
			total+=1
	if total<100:
		results="%02d" % eval(results)
	else:
		results="%003d" % eval(results)
	return results

# using function from Steeve to add Provider's name			
def extract_torrents(data,name_provider,code_resolution,max_torrents):
	import re
	name = re.findall(r'/.page=view&#..;tid=(.*?)>(.*?)</a></td>',data) # find all names
	size = re.findall(r'<td class="tlistsize">(.*?)</td>',data) # find all sizes
	for cont, torrent in enumerate(re.findall(r'/.page=download&#..;tid=(.*?)"', data)):
		#find name in the torrent
		if re.search(r'Searching torrents',data) is not None:
			#There are several torrents
			yield { "name": name[cont][1] + ' - ' + size[cont] + ' - ' + name_provider,"uri": url + '/?page=download&tid=' + torrent, 'resolution': code_resolution}
			#limit torrents
			if (cont == max_torrents):
				break
		else:
			#Just one torrent
			name = re.search(r'"viewtorrentname">(.*?)<', data).group(1) + ' - ' + name_provider
			yield { "name": name,"uri": url + '?page=download&tid=' + torrent, 'resolution': code_resolution}
			break

def search(info):
	query = info['query'] + ((' ' + anime_quality) if (anime_quality !='ALL') else ' ' )  + ' ' + extra
	provider.notify(message="Searching: " + query + '...', header=None, time=1000, image=icon)
	query = provider.quote_plus(query)
	response = provider.GET("%s/?page=search&cats=%s&term=%s&sort=2" % (url,category,query))
	return extract_torrents(response.data,'Nyaa Provider',values3[anime_quality],10)

def search_movie(info):
	return []

def search_episode(info):
	# abs_episode=info['absolute_number_episode'] : not yet supported
	abs_episode= convert_episode_season(info['tvdb_id'],info['season'],info['episode'])
	query='"' + info['title'] + '" ' + abs_episode
	return search({'query': query})

# This registers your module for use
provider.register(search, search_movie, search_episode)