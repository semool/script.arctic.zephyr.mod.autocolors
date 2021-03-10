#!/usr/bin/python
# coding: utf-8

from resources.lib.utils import *
import xbmc, xbmcgui, xbmcaddon
from sys import argv
import simplecache

addon = xbmcaddon.Addon()
addonName = addon.getAddonInfo("name")

location = addon.getSetting("location")
Url = 'https://www.yahoo.com/news/_tdnews/api/resource/WeatherSearch;text=%s'
cache = simplecache.SimpleCache()

# The original Code for Location Select is from the addon weather.multi borrowed
def search_location():
   keyboard = xbmc.Keyboard(location, xbmc.getLocalizedString(14024), False)
   keyboard.doModal()
   dialog = xbmcgui.Dialog()
   if (keyboard.isConfirmed() and keyboard.getText()):
      text = keyboard.getText()
      locs = []
      log("Searching for location: %s" % text)
      url = Url % text
      cachedata = cache.get(url)
      #cachedata = False
      if cachedata:
         usecache = True
         data = cachedata
      else:
         usecache = False
         data = get_data(url)
         cache.set(url, data)
      if data:
         log("Location data: %s (Cache: %s)" % (data, usecache))
         locs = data
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
               # Set Timezones in Settings
               times = suntimes(locs[selected]['city'],locs[selected]['lat'],locs[selected]['lon'])
               addon.setSetting("start_time_sun", times["start"])
               addon.setSetting("end_time_sun", times["end"])
               log("Selected location: %s" % locs[selected])
      else:
         log("No locations found", force=True)
         dialog.ok(addonName, xbmc.getLocalizedString(284))

if __name__ == '__main__':
   if len(argv) > 1:
      search_location()
   else:
      addon.openSettings()
