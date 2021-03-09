#!/usr/bin/python
# coding: utf-8

import xbmc, xbmcaddon, xbmcvfs
import json
import xml.etree.ElementTree as ET
import datetime
from resources.lib.utils import *

addon = xbmcaddon.Addon()
addonName = addon.getAddonInfo("name")
addonId = addon.getAddonInfo("id")
addonVersion = addon.getAddonInfo("version")

def main():

   # Get active skin name
   activeskin = xbmc.getSkinDir()
   log("Active Skin: %s" % activeskin)

   if activeskin == "skin.arctic.zephyr.mod":

      # Dont switch when yes/no Dialog is open [id:10100]
      data = json.dumps({"jsonrpc":"2.0","method":"GUI.GetProperties","params":{"properties":["currentwindow"]},"id":1})
      try:
         result = json.loads(xbmc.executeJSONRPC(data))
         windowid = result['result']['currentwindow']['id']
         windowname = result['result']['currentwindow']['label']
      except:
        windowid = False
        windowname = False
      log("ActiveWindowID: %s (%s)" % (windowid, windowname))

      if not windowid == 10100:

         # Get Service Settings
         sunchange = addon.getSetting("sunchange")
         location = addon.getSetting("location")
         latitude = addon.getSetting("latitude")
         longitude = addon.getSetting("longitude")
         start = addon.getSetting("start_time")
         end = addon.getSetting("end_time")
         light = addon.getSetting("lightmode")
         dark = addon.getSetting("darkmode")
         player = addon.getSetting("player")
         saver = addon.getSetting("saver")

         # Reading skin setting: is autocolor enabled
         try:
            skinaddon = xbmcaddon.Addon("skin.arctic.zephyr.mod")
            skinProfile = xbmcvfs.translatePath(skinaddon.getAddonInfo("profile"))
            skinSettings = skinProfile + "settings.xml"
            log("Skin Profile Path: %s" % skinSettings)
            tree = ET.parse(skinSettings)
            searchsetting = tree.find(".//setting[@id='daynight.autocolor']")
            autocolor = searchsetting.text
            log("Autocolor enabled: %s" % autocolor)
         except:
            autocolor = "true"
            log("Autocolor enabled in Fallback Mode: No Skin Setting Found. Disable this Addon to deactivate automatic color switch: %s" % autocolor, force=True)

         if autocolor == "true":

            if player == "false":
               playcheck = xbmc.Player().isPlaying()
            else:
               playcheck = False
            log("Playercheck: %s" % playcheck)
            if playcheck:
               return

            if saver == "true":
               screensaver = False
               log("Screensavercheck: %s" % screensaver)
            else:
               #Check if Screensaver is active
               data = json.dumps({'jsonrpc': '2.0', 'method': 'XBMC.GetInfoBooleans', 'params': { "booleans": ["System.ScreenSaverActive"] }, 'id': 1})
               try:
                  result = json.loads(xbmc.executeJSONRPC(data))
                  screensaver = result['result']['System.ScreenSaverActive']
                  log("Screensaver Status: %s" % screensaver)
               except:
                  screensaver = False
                  log("Screensaver Status: unknown")
            if screensaver:
               return

            # Get current active Color Theme
            data = json.dumps({'jsonrpc': '2.0', 'method': 'Settings.GetSettingValue', 'params': {'setting':'lookandfeel.skincolors'}, 'id': 1})
            try:
               result = json.loads(xbmc.executeJSONRPC(data))
               activecolor = result['result']['value']
            except:
               activecolor = False
            log("Current Theme Color: %s" % activecolor)

            # Get current time
            current_time = datetime.datetime.now().strftime("%H:%M:%S")

            # Calculate Sunrise -> Sunset
            if sunchange == "true":
               times = suntimes(location,latitude,longitude)
               if not times["timecache"]:
                  addon.setSetting("start_time_sun", times["start"])
                  addon.setSetting("end_time_sun", times["end"])
            else:
               times = {"start": start, "end": end, "local_timezone": False, "zonecache": False, "timecache": False}

            # Timeframe for Light Theme Color
            log("Light Theme Timeframe: %s -> %s (Timezone: %s) [Zonecache: %s, Timecache: %s]" % (times["start"], times["end"], times["local_timezone"], times["zonecache"], times["timecache"]))

            # Check timeframe and switch Theme Color
            if current_time > start and current_time < end:
               # Set Light Theme
               if activecolor != light:
                  log("Setting Theme Color: %s" % light, force=True)
                  xbmc.executeJSONRPC(json.dumps({"jsonrpc":"2.0","method":"Settings.SetSettingValue","id":1,"params":{"setting":"lookandfeel.skincolors","value":light}}))
            else:
               # Set Dark Theme
               if activecolor != dark:
                  log("Setting Theme Color: %s" % dark, force=True)
                  xbmc.executeJSONRPC(json.dumps({"jsonrpc":"2.0","method":"Settings.SetSettingValue","id":1,"params":{"setting":"lookandfeel.skincolors","value":dark}}))


if __name__ == '__main__':
   log("v%s --> Start" % addonVersion, force=True)
   monitor = xbmc.Monitor()
   while not monitor.waitForAbort(5):
     main()
   log("v%s --> Stop" % addonVersion, force=True)
