import xbmc, xbmcgui, xbmcaddon
from sys import argv
import requests
import json
import simplecache

addon = xbmcaddon.Addon("script.arctic.zephyr.mod.autocolors")
addonName = addon.getAddonInfo("name")
debug = addon.getSetting("debug")
location = addon.getSetting("location")
Url = 'https://www.yahoo.com/news/_tdnews/api/resource/WeatherSearch;text=%s'
cache = simplecache.SimpleCache()

# This Code for Location Select is from the addon weather.multi borrowed
def search_location():
   keyboard = xbmc.Keyboard(location, xbmc.getLocalizedString(14024), False)
   keyboard.doModal()
   if (keyboard.isConfirmed() and keyboard.getText()):
      text = keyboard.getText()
      locs = []
      if debug == "true":
         xbmc.log("%s --> searching for location: %s" % (addonName, text),level=xbmc.LOGINFO)
      url = Url % text
      cachedata = cache.get(url)
      if cachedata:
         usecache = True
         data = cachedata
      else:
         usecache = False
         data = get_data(url)
         cache.set(url, data)
      if data:
         if debug == "true":
            xbmc.log("%s --> location data: %s (Cache: %s)" % (addonName, data, usecache),level=xbmc.LOGINFO)
         locs = data
         dialog = xbmcgui.Dialog()
         if locs:
            items = []
            for item in locs:
               listitem = xbmcgui.ListItem(item['qualifiedName'], item['city'] + ' - ' + item['country'] + ' [' + str(item['lat']) + '/' + str(item['lon']) + ']')
               items.append(listitem)
            selected = dialog.select(xbmc.getLocalizedString(396), items, useDetails=True)
            if selected != -1:
               addon.setSetting("location", locs[selected]['city'])
               addon.setSettingNumber("latitude", locs[selected]['lat'])
               addon.setSettingNumber("longitude", locs[selected]['lon'])
               if debug == "true":
                  xbmc.log("%s --> selected location: %s" % (addonName, locs[selected]),level=xbmc.LOGINFO)
         else:
            if debug == "true":
               xbmc.log("%s --> no locations found" % (addonName),level=xbmc.LOGINFO)
            dialog.ok(addonName, xbmc.getLocalizedString(284))

def get_data(url):
   if debug == "true":
      xbmc.log("%s --> get data: %s" % (addonName, url),level=xbmc.LOGINFO)
   headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.72 Safari/537.36'}
   try:
      response = requests.get(url, headers=headers, timeout=10)
      return response.json()
   except:
      return


if __name__ == '__main__':
   if len(argv) > 1:
      search_location()
   else:
      addon.openSettings()
