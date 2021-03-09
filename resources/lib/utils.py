#!/usr/bin/python
# coding: utf-8

import xbmc, xbmcaddon
import datetime
import simplecache
from resources.lib.astral import LocationInfo
from resources.lib.astral.sun import sun

addon = xbmcaddon.Addon()
addonName = addon.getAddonInfo("name")
addonId = addon.getAddonInfo("id")
addonVersion = addon.getAddonInfo("version")

cache = simplecache.SimpleCache()

INFO = xbmc.LOGINFO
WARNING = xbmc.LOGWARNING
DEBUG = xbmc.LOGDEBUG
ERROR = xbmc.LOGERROR

def log(txt,loglevel=DEBUG,force=False):
   if (addon.getSettingBool('debug') or force) and loglevel not in [WARNING, ERROR]:
      loglevel = INFO

   message = u'[%s] %s' % (addonId, txt)
   xbmc.log(msg=message, level=loglevel)

def suntimes(location,latitude,longitude):
   cachename = addonId + ".timezone"
   cachedata = cache.get(cachename)
   #cachedata = False
   if cachedata:
      zonecache = True
      local_timezone = cachedata
   else:
      zonecache = False
      local_timezone = datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo
      cache.set(cachename, local_timezone, expiration=datetime.timedelta(hours=12))

   cachename = addonId + "." + location
   cachedata = cache.get(cachename)
   #cachedata = False
   if cachedata:
      start = cachedata["start"]
      end = cachedata["end"]
      times = {"start": start, "end": end, "local_timezone": local_timezone, "zonecache": zonecache, "timecache": True}
   else:
      city = LocationInfo(latitude=latitude, longitude=longitude)
      sundata = sun(city.observer, tzinfo=local_timezone)
      start = sundata["sunrise"].strftime("%H:%M:%S")
      end = sundata["sunset"].strftime("%H:%M:%S")
      times = {"start": start, "end": end, "local_timezone": local_timezone, "zonecache": zonecache, "timecache": False}
      cache.set(cachename, times, expiration=datetime.timedelta(hours=12))

   return times
