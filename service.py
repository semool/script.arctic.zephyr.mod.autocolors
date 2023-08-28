#!/usr/bin/python
# coding: utf-8

import xbmc, xbmcaddon, xbmcvfs
import datetime
from resources.lib.utils import *
import xml.etree.ElementTree as ET

addon = xbmcaddon.Addon()
addonVersion = addon.getAddonInfo("version")

def dialogcheck():
   try:
      dialogcheck = getJsonRPC({"jsonrpc": "2.0","method": "GUI.GetProperties","params": {"properties": ["currentwindow"]},"id": 1})
      windowid = dialogcheck['result']['currentwindow']['id']
      windowname = dialogcheck['result']['currentwindow']['label']
   except:
     windowid = False
     windowname = False
   log("ActiveWindowID: %s (%s)" % (windowid, windowname))
   return windowid,windowname

def playercheck():
   player = addon.getSetting("player")
   speedstate = False
   if player == "false":
      playcheck = xbmc.Player().isPlaying()
      if playcheck:
         pausecheck = getJsonRPC({"jsonrpc": "2.0","method": "Player.GetProperties","params": { "playerid": 1, "properties": ["speed"] },"id": 1})
         try:
            speedstate = pausecheck['result']['speed']
            if speedstate == 0:
               playcheck = False
         except:
            pass
   else:
      playcheck = False
   log("Player Check: %s" % playcheck)
   log("Player Pause Check: %s" % speedstate)
   return playcheck

def screensavercheck():
   saver = addon.getSetting("saver")
   if saver == "true":
      screensaver = False
   else:
      try:
         savercheck = getJsonRPC({"jsonrpc": "2.0", "method": "XBMC.GetInfoBooleans", "params": { "booleans": ["System.ScreenSaverActive"] }, "id": 1})
         screensaver = savercheck['result']['System.ScreenSaverActive']
      except:
         screensaver = False
   log("Screensaver Check: %s" % screensaver)
   return screensaver


def main():
   # Get active skin name
   activeskin = xbmc.getSkinDir()
   log("Active Skin: %s" % activeskin)
   if not activeskin == "skin.arctic.zephyr.mod":
      log("Current active Skin is not Supportet by this Addon!")
      return

   # Reading skin setting: is autocolor enabled
   # --------------------------------------------
   # Its not working??? Kodi20 Returns Nothing!!! Kodi19 Crashed!!!
   #autocolor = xbmcaddon.Addon(activeskin).getSetting("daynight.autocolor")
   # --------------------------------------------
   SkinPath = xbmcvfs.translatePath(xbmcaddon.Addon(activeskin).getAddonInfo("profile"))
   tree = ET.parse(SkinPath + "settings.xml")
   root = tree.getroot()
   autocolor = root.find('.//setting[@id="daynight.autocolor"]').text

   log("Autocolor enabled: %s" % autocolor)
   if not autocolor:
      return

   # Dont switch when yes/no Dialog is open [id:10100] or Addon Browser [id:10040]
   windowid, windowname = dialogcheck()
   if windowid == 10100 or windowid == 10040:
      return

   #Check if Player is running, stopped or paused
   playcheck = playercheck()
   if playcheck:
      return

   #Check if Screensaver is active
   screensaver = screensavercheck()
   if screensaver:
      return

   # Get current active Color Theme
   try:
      colortheme = getJsonRPC({"jsonrpc": "2.0", "method": "Settings.GetSettingValue", "params": {"setting": "lookandfeel.skincolors"}, "id": 1})
      activecolor = colortheme['result']['value']
   except:
      activecolor = False
   log("Current Theme Color: %s" % activecolor)

   # Calculate Sunrise -> Sunset
   sunchange = addon.getSetting("sunchange")
   if sunchange == "true":
      location = addon.getSetting("location")
      latitude = addon.getSetting("latitude")
      longitude = addon.getSetting("longitude")
      times = suntimes(location,latitude,longitude)
      if not times["timecache"]:
         addon.setSetting("start_time_sun", times["start"])
         addon.setSetting("end_time_sun", times["end"])
   else:
      start = addon.getSetting("start_time")
      end = addon.getSetting("end_time")
      times = {"start": start, "end": end, "local_timezone": False, "zonecache": False, "timecache": False}

   # Timeframe for Light Theme Color
   log("Light Theme Timeframe: %s -> %s (Timezone: %s) [Zonecache: %s, Timecache: %s]" % (times["start"], times["end"], times["local_timezone"], times["zonecache"], times["timecache"]))

   # Check timeframe and switch Theme Color
   current_time = datetime.datetime.now().strftime("%H:%M:%S")
   if current_time > times["start"] and current_time < times["end"]:
      # Set Light Theme
      light = addon.getSetting("lightmode")
      if activecolor != light:
         log("Setting Theme Color: %s" % light, force=True)
         setJsonRPC({"jsonrpc": "2.0","method": "Settings.SetSettingValue","id": 1,"params": {"setting": "lookandfeel.skincolors","value": light}})
   else:
      # Set Dark Theme
      dark = addon.getSetting("darkmode")
      if activecolor != dark:
         log("Setting Theme Color: %s" % dark, force=True)
         setJsonRPC({"jsonrpc": "2.0","method": "Settings.SetSettingValue","id": 1,"params": {"setting": "lookandfeel.skincolors","value": dark}})


if __name__ == '__main__':
   log("Version %s is started" % addonVersion, force=True)
   main()
   monitor = xbmc.Monitor()
   while not monitor.abortRequested():
      monitor.waitForAbort(5)
      main()
   log("Version %s is stopped" % addonVersion, force=True)
