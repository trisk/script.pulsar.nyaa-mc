from pulsar import provider
import re

# this read the settings
url = provider.ADDON.getSetting('url_address')
icon = provider.ADDON.getAddonInfo('icon')
name_provider = provider.ADDON.getAddonInfo('name') # gets name
extra = provider.ADDON.getSetting('extra')
values2 = {"ALL":'1_0',"English translations":'1_37',"Non English translations":'1_38' ,"Raw":'1_11'} # read category
category = values2[provider.ADDON.getSetting('category')]
anime_key_allowed = provider.ADDON.getSetting('anime_key_allowed')
anime_key_denied = provider.ADDON.getSetting('anime_key_denied')
anime_min_size = float(provider.ADDON.getSetting('anime_min_size'))
anime_max_size = float(provider.ADDON.getSetting('anime_max_size'))
max_magnets = int(provider.ADDON.getSetting('max_magnets'))  #max_magnets

#define quality variables
quality_allow = ['480p', 'DVD', 'HDTV', '720p','1080p', '3D' , 'WEB', 'Bluray', 'BRRip', 'HDRip', 'MicroHD', 'x264', 'AC3', 'AAC', 'HEVC', 'CAM'] 
quality_deny = []
max_size = 10.00 #10 it is not limit
min_size = 0.00

#quality_TV
anime_q1 = provider.ADDON.getSetting('anime_q1') #480p
anime_q2 = provider.ADDON.getSetting('anime_q2') #DVD
anime_q3 = provider.ADDON.getSetting('anime_q3') #HDTV
anime_q4 = provider.ADDON.getSetting('anime_q4') #720p
anime_q5 = provider.ADDON.getSetting('anime_q5') #1080p
anime_q7 = provider.ADDON.getSetting('anime_q7') #WEB
anime_q8 = provider.ADDON.getSetting('anime_q8') #Bluray
anime_q9 = provider.ADDON.getSetting('anime_q9') #BRRip
anime_q10 = provider.ADDON.getSetting('anime_q10') #HDRip
anime_q12 = provider.ADDON.getSetting('anime_q12') #x264
anime_q15 = provider.ADDON.getSetting('anime_q15') #HEVC
anime_allow = re.split('\s',anime_key_allowed)
anime_deny = re.split('\s',anime_key_denied) 
anime_allow.append('480p') if anime_q1 == 'true' else anime_deny.append('480p')
anime_allow.append('DVD') if anime_q2 == 'true' else anime_deny.append('DVD')
anime_allow.append('HDTV') if anime_q3 == 'true' else anime_deny.append('HDTV')
anime_allow.append('720p') if anime_q4 == 'true' else anime_deny.append('720p')
anime_allow.append('1080p') if anime_q5 == 'true' else anime_deny.append('1080p')
anime_allow.append('WEB') if anime_q7 == 'true' else anime_deny.append('WEB')
anime_allow.append('Bluray') if anime_q8 == 'true' else anime_deny.append('Bluray')
anime_allow.append('BRRip') if anime_q9 == 'true' else anime_deny.append('BRRip')
anime_allow.append('HDRip') if anime_q10 == 'true' else anime_deny.append('HDRip')
anime_allow.append('x264') if anime_q12 == 'true' else anime_deny.append('x264')
anime_allow.append('HEVC') if anime_q15 == 'true' else anime_deny.append('HEVC')
if '' in anime_allow: anime_allow.remove('')
if '' in anime_deny: anime_deny.remove('') 

# validate keywords
def included(value, keys):
	value = value.replace('-',' ')
	res = False
	for item in keys:
		if item.upper() in value.upper():
			res = True 
			break
	return res

# validate size
def size_clearance(size):
	global max_size
	max_size = 100 if max_size == 10 else max_size
	res = False
	value = float(re.split('\s', size.replace(',',''))[0])
	value *= 0.001 if 'M' in size else 1
	if min_size <= value and value <= max_size:
		res = True
	return res

# clean_html
def clean_html(data):
	lines = re.findall('<!--(.*?)-->',data)
	for line in lines:
		data = data.replace(line,'')
	return data

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
def extract_torrents(data):
	try:
		name = re.findall(r'/.page=view&#..;tid=(.*?)>(.*?)</a></td>',data) # find all names
		size = re.findall(r'<td class="tlistsize">(.*?)</td>',data) # find all sizes
		provider.log.info('Keywords allowed: ' + str(quality_allow))
		provider.log.info('Keywords denied: ' + str(quality_deny))
		provider.log.info('min Size: ' + str(min_size) + ' GB')
		provider.log.info('max Size: ' + str(max_size)  + ' GB' if max_size != 10 else 'max Size: MAX')
		cm = 0
		for cm, torrent in enumerate(re.findall(r'/.page=download&#..;tid=(.*?)"', data)):
			#find name in the torrent
			if re.search(r'Searching torrents',data) is not None:
				if included(name[cm][1], quality_allow) and not included(name[cm][1], quality_deny) and size_clearance(size[cm]):
					yield { "name": name[cm][1] + ' - ' + size[cm] + ' - ' + name_provider,"uri": url + '/?page=download&tid=' + torrent}
				else:
					provider.log.warning(name[cm][1] + ' - ' + size[cm] + '   ***Not Included for keyword filtering or size***')
				if (cm == max_magnets): #limit magnets
					break
			else:
				#Just one torrent
				name = re.search(r'"viewtorrentname">(.*?)<', data).group(1) + ' - ' + name_provider
				yield { "name": name,"uri": url + '?page=download&tid=' + torrent}
				break
	except:
		provider.log.error('>>>>>>>ERROR parsing data<<<<<<<')

def search(info):
	query = info['query'] + extra
	provider.notify(message="Searching: " + query.title() + '...', header=None, time=1000, image=icon)
	query = provider.quote_plus(query)
	provider.log.info("%s/?page=search&cats=%s&term=%s&sort=2" % (url,category,query))
	response = provider.GET("%s/?page=search&cats=%s&term=%s&sort=2" % (url,category,query))
	if response == (None, None):
		provider.log.error('404 Page not found')
		return []
	else:
		return extract_torrents(response.data)


def search_movie(info):
	return []

def search_episode(info):
	global quality_allow, quality_deny, min_size, max_size
	quality_allow = anime_allow
	quality_deny = anime_deny
	min_size = anime_min_size
	max_size = anime_max_size
	# abs_episode=info['absolute_number_episode'] : not yet supported
	abs_episode= convert_episode_season(info['tvdb_id'],info['season'],info['episode'])
	query='"' + info['title'] + '" ' + abs_episode
	return search({'query': query})

# This registers your module for use
provider.register(search, search_movie, search_episode)