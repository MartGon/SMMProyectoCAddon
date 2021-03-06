# -*- coding: utf-8 -*-
# Module: default
# Author: Guillermo Rodriguez Agrasar
# Created on: 28.12.2017

import sys
from urllib import urlencode

import xbmcgui
import xbmcplugin
import requests
import json
import urllib2
import sys
import datetime
import os
import time
from urlparse import parse_qsl

# Get the plugin url in plugin:// notation.
_url = sys.argv[0]
# Get the plugin handle as an integer number.
_handle = int(sys.argv[1])
thumb='http://www.vidsplay.com/wp-content/uploads/2017/04/crab-screenshot.jpg'
# Free sample videos are provided by www.vidsplay.com



def get_url(**kwargs):
    """
    Create a URL for calling the plugin recursively from the given set of keyword arguments.

    :param kwargs: "argument=value" pairs
    :type kwargs: dict
    :return: plugin call URL
    :rtype: str
    """
    return '{0}?{1}'.format(_url, urlencode(kwargs))


def get_categories():
    """
    Get the list of video categories.

    Here you can insert some parsing code that retrieves
    the list of video categories (e.g. 'Movies', 'TV-shows', 'Documentaries' etc.)
    from some site or server.

    .. note:: Consider using `generator functions <https://wiki.python.org/moin/Generators>`_
        instead of returning lists.

    :return: The list of video categories
    :rtype: list
    """
    url="http://localhost:3000/peliculas"
    categories=[]
    response=requests.get(url)
    if response.status_code == 200:
    	results=response.json()
    	for result in results:
			for key,value in result.items():
				if(key!="nombre") and (key!="path") and (key!="_id") and (key not in categories):
					categories.append(key)
    else:
    	print "Error code %s" % response.status_code
    categories.append("Recomendado")	
    return categories


def get_videos(category,sub_category):
    """
    Get the list of videofiles/streams.

    Here you can insert some parsing code that retrieves
    the list of video streams in the given category from some site or server.

    .. note:: Consider using `generators functions <https://wiki.python.org/moin/Generators>`_
        instead of returning lists.

    :param category: Category name
    :type category: str
    :return: the list of videos in the category
    :rtype: list
    """
    videos=[]
    url="http://localhost:3000/peliculas"
    response=requests.get(url)
    if response.status_code == 200:
    	results=response.json()
    	for result in results:
    		for key,value in result.items():
    			if(key==category) and (str(value)==str(sub_category)):
    				videos.append(result)
    else:
    	print "Error code %s" % response.status_code
    return videos


def list_categories():
    """
    Create the list of video categories in the Kodi interface.
    """
    # Set plugin category. It is displayed in some skins as the name
    # of the current section.
    xbmcplugin.setPluginCategory(_handle, 'My Video Collection')
    # Set plugin content. It allows Kodi to select appropriate views
    # for this type of content.
    xbmcplugin.setContent(_handle, 'videos')
    # Get video categories
    categories = get_categories()
    # Iterate through categories
    for category in categories:
        # Create a list item with a text label and a thumbnail image.
        list_item = xbmcgui.ListItem(label=category)
        # Set graphics (thumbnail, fanart, banner, poster, landscape etc.) for the list item.
        # Here we use the same image for all items for simplicity's sake.
        # In a real-life plugin you need to set each image accordingly.
        list_item.setArt({'thumb': thumb,
                          'icon': thumb,
                          'fanart': thumb})
        # Set additional info for the list item.
        # Here we use a category name for both properties for for simplicity's sake.
        # setInfo allows to set various information for an item.
        # For available properties see the following link:
        # http://mirrors.xbmc.org/docs/python-docs/15.x-isengard/xbmcgui.html#ListItem-setInfo
        list_item.setInfo('video', {'title': category, 'genre': category})
        # Create a URL for a plugin recursive call.
        # Example: plugin://plugin.video.example/?action=listing&category=Animals
        url = get_url(action='sublisting', category=category)
        # is_folder = True means that this item opens a sub-list of lower level items.
        is_folder = True
        # Add our item to the Kodi virtual folder listing.
        xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)
    # Add a sort method for the virtual folder items (alphabetically, ignore articles)
    xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    # Finish creating a virtual folder.
    xbmcplugin.endOfDirectory(_handle)
def get_sub_categories(category):
	url="http://localhost:3000/peliculas"
	sub_categories=[]
	response=requests.get(url)
	if response.status_code==200:
		results=response.json()
		for result in results:
			for key,value in result.items():
				if(key==category) and (value not in sub_categories):
					sub_categories.append(value)
	else:
		print "Error code %s" % response.status_code
	return sub_categories
	
def get_best_video(category):
	url="http://localhost:3000/peliculas"
	maxValue=0
	video=dict()
	response=requests.get(url)
	if response.status_code==200:
		results=response.json()
		for result in results:
			for key,value in result.items():
				if (key==category) and (value>maxValue):
					maxValue=value
					video=result
	else:
		print "Error code %s" % response.status_code
	return video
	
def get_original_video(category):
	url="http://localhost:3000/peliculas"
	maxValue=0
	video=dict()
	response=requests.get(url)
	if response.status_code==200:
		results=response.json()
		for result in results:
			for key,value in result.items():
				if (key==category) and (value=="0"):
					video=result
					#xbmc.log(video)
	else:
		print "Error code %s" % response.status_code
	return video
	
def getBandwidth():

	filename = "Launcher.zip"
	curTime = datetime.datetime.now()
		
	u = urllib2.urlopen('http://seasonlegion.ddns.net/downloads/' + filename)
	f = open(filename, 'wb')
	while True:
		buffer = u.read(8192)
		if not buffer:
			break
		f.write(buffer)
	f.close()
	
	elapsedTime = (datetime.datetime.now() - curTime).total_seconds()

	size = os.path.getsize(filename) # en bytes
	os.remove(filename)

	velocidad = size * 8 / (elapsedTime * 1000) # Para que sea en kb/s 
	
	return velocidad
	
def get_best_rate(rate_recomendado,category):

	url="http://localhost:3000/peliculas"
	minValue=1000000
	difValue=0
	video=dict()
	xbmc.log('EL bandwidth es' + str(rate_recomendado))
	
	response=requests.get(url)
	if response.status_code==200:
		results=response.json()
		for result in results:
			for key,value in result.items():
				if (key==category):
					difValue=abs(float(value)-float(rate_recomendado))
					if(difValue<minValue):
						minValue=difValue
						xbmc.log('La diferencia es ' + str(minValue))
						video=result
	else:
		print "Error code %s" % response.status_code
	return video
	
def list_sub_categories(category):
	xbmcplugin.setPluginCategory(_handle,category)
	xbmcplugin.setContent(_handle,'values')
	xbmc.log('ENTRO EN SUB_CATEGORIES')
	
	if category=="calidad":
		video=get_best_video(category)
		list_item=xbmcgui.ListItem(label=video['nombre'])
		list_item.setInfo('video',{'title': video['nombre'], 'genre': video['nombre']})
		list_item.setArt({'thumb': thumb,
			'icon':thumb,
			'fanart':thumb})
		list_item.setProperty('IsPlayable','True')
		url=get_url(action='play',video=video['path'])
		is_folder=False
		xbmcplugin.addDirectoryItem(_handle,url,list_item,is_folder)
		xbmcplugin.endOfDirectory(_handle)
		
	elif category=="original":
	
		#video=get_original_video(category)
		url="http://localhost:3000/peliculas"
		video=dict()
		response=requests.get(url)
		
		if response.status_code==200:
			results=response.json()
			for result in results:
				for key,value in result.items():
					if (key==category) and ((value=="0") or (value==0)):
						video=result
						list_item=xbmcgui.ListItem(label=video['nombre'])
						list_item.setInfo('video',{'title':video['nombre'], 'genre':video['nombre']})
						list_item.setArt({'thumb':thumb,
							'icon':thumb,
							'fanart':thumb})
						list_item.setProperty('IsPlayable','True')
						url=get_url(action='play',video=video['path'])
						is_folder=False
						xbmcplugin.addDirectoryItem(_handle,url,list_item,is_folder)
						
		xbmcplugin.endOfDirectory(_handle)
		
	elif category=="Recomendado":
	
		rate_recomendado=getBandwidth()
		video=get_best_rate(rate_recomendado,"bitrate")
		list_item=xbmcgui.ListItem(label=video['nombre'])
		list_item.setInfo('video',{'title':video['nombre'], 'genre':video['nombre']})
		list_item.setArt({'thumb':thumb,
			'icon':thumb,
			'fanart':thumb})
		list_item.setProperty('IsPlayable','True')
		url=get_url(action='play',video=video['path'])
		is_folder=False
		xbmcplugin.addDirectoryItem(_handle,url,list_item,is_folder)
		xbmcplugin.endOfDirectory(_handle)
	else:
		sub_categories=get_sub_categories(category)
		for sub_category in sub_categories:
			list_item=xbmcgui.ListItem(label=str(sub_category))
			list_item.setInfo('video',{'title':sub_category,'genre':sub_category})
			list_item.setArt({'thumb': thumb,
				'icon': thumb,
				'fanart':thumb})
			url=get_url(action='listing',category=category,sub_category=str(sub_category))
			is_folder=True
			xbmcplugin.addDirectoryItem(_handle,url,list_item,is_folder)
		xbmcplugin.endOfDirectory(_handle)


	

def list_videos(category,sub_category):
    """
    Create the list of playable videos in the Kodi interface.

    :param category: Category name
    :type category: str
    """
    # Set plugin category. It is displayed in some skins as the name
    # of the current section.
    xbmcplugin.setPluginCategory(_handle, category)
    # Set plugin content. It allows Kodi to select appropriate views
    # for this type of content.
    xbmcplugin.setContent(_handle, 'videos')
    # Get the list of videos in the category.
    videos = get_videos(category,sub_category)
    # Iterate through videos.
    for video in videos:
        # Create a list item with a text label and a thumbnail image.
        list_item = xbmcgui.ListItem(label=video['nombre'])
        # Set additional info for the list item.
        list_item.setInfo('video', {'title': video['nombre'], 'genre': video['nombre']})
        # Set graphics (thumbnail, fanart, banner, poster, landscape etc.) for the list item.
        # Here we use the same image for all items for simplicity's sake.
        # In a real-life plugin you need to set each image accordingly.
        list_item.setArt({'thumb': thumb,
                          'icon': thumb,
                          'fanart': thumb})
        # Set 'IsPlayable' property to 'true'.
        # This is mandatory for playable items!
        list_item.setProperty('IsPlayable', 'true')
        # Create a URL for a plugin recursive call.
        # Example: plugin://plugin.video.example/?action=play&video=http://www.vidsplay.com/wp-content/uploads/2017/04/crab.mp4
        url = get_url(action='play', video=video['path'])
        # Add the list item to a virtual Kodi folder.
        # is_folder = False means that this item won't open any sub-list.
        is_folder = False
        # Add our item to the Kodi virtual folder listing.
        xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)
    # Add a sort method for the virtual folder items (alphabetically, ignore articles)
    xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    # Finish creating a virtual folder.
    xbmcplugin.endOfDirectory(_handle)


def play_video(path):
    """
    Play a video by the provided path.

    :param path: Fully-qualified video URL
    :type path: str
    """
    # Create a playable item with a path to play.
    play_item = xbmcgui.ListItem(path=path)
    # Pass the item to the Kodi player.
    xbmcplugin.setResolvedUrl(_handle, True, listitem=play_item)


def router(paramstring):
    """
    Router function that calls other functions
    depending on the provided paramstring

    :param paramstring: URL encoded plugin paramstring
    :type paramstring: str
    """
    # Parse a URL-encoded paramstring to the dictionary of
    # {<parameter>: <value>} elements
    params = dict(parse_qsl(paramstring))
    # Check the parameters passed to the plugin
    if params:
        if params['action'] == 'listing':
            # Display the list of videos in a provided category.
            list_videos(params['category'],str(params['sub_category']))
        elif params['action']== 'sublisting':
        	list_sub_categories(params['category'])    
        elif params['action'] == 'play':
            # Play a video from a provided URL.
            play_video(params['video'])
        else:
            # If the provided paramstring does not contain a supported action
            # we raise an exception. This helps to catch coding errors,
            # e.g. typos in action names.
            raise ValueError('Invalid paramstring: {0}!'.format(paramstring))
    else:
        # If the plugin is called from Kodi UI without any parameters,
        # display the list of video categories
        list_categories()


if __name__ == '__main__':
    # Call the router function and pass the plugin call parameters to it.
    # We use string slicing to trim the leading '?' from the plugin call paramstring
    router(sys.argv[2][1:])
