#!/usr/bin/python
# coding: utf-8

import xbmc, xbmcaddon
import datetime
from resources.lib.utils import *

addon = xbmcaddon.Addon()
addonVersion = addon.getAddonInfo("version")

def main():

   # Get active skin name
   activeskin = xbmc.getSkinDir()
   log("Active Skin: %s" % activeskin)

   if activeskin == "skin.arctic.zephyr.mod":

      # Dont switch when yes/no Dialog is open [id:10100] or Addon Browser [id:10040]
      try:
         dialogcheck = getJsonRPC({"jsonrpc": "2.0","method": "GUI.GetProperties","params": {"properties": ["currentwindow"]},"id": 1})
         windowid = dialogcheck['result']['currentwindow']['id']
         windowname = dialogcheck['result']['currentwindow']['label']
      except:
        windowid = False
        windowname = False
      log("ActiveWindowID: %s (%s)" % (windowid, windowname))

      if not windowid == 10100 and not windowid == 10040:

         # Reading skin setting: is autocolor enabled
         try:
            skinSettings, tree = parseSkinSettings("skin.arctic.zephyr.mod")
            log("Skin Profile Path: %s" % skinSettings)
            searchsetting = tree.find(".//setting[@id='daynight.autocolor']")
            autocolor = searchsetting.text
            log("Autocolor enabled: %s" % autocolor)
         except:
            autocolor = "true"
            log("Autocolor enabled in Fallback Mode: No Skin Setting Found. Disable this Addon to deactivate automatic color switch: %s" % autocolor, force=True)

         if autocolor == "true":

            player = addon.getSetting("player")
            if player == "false":
               playcheck = xbmc.Player().isPlaying()
            else:
               playcheck = False
            log("Playercheck: %s" % playcheck)
            if playcheck:
               return

            saver = addon.getSetting("saver")
            if saver == "true":
               screensaver = False
               log("Screensavercheck: %s" % screensaver)
            else:
               #Check if Screensaver is active
               try:
                  savercheck = getJsonRPC({"jsonrpc": "2.0", "method": "XBMC.GetInfoBooleans", "params": { "booleans": ["System.ScreenSaverActive"] }, "id": 1})
                  screensaver = savercheck['result']['System.ScreenSaverActive']
                  log("Screensaver Status: %s" % screensaver)
               except:
                  screensaver = False
                  log("Screensaver Status: unknown")
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
               times = suntimes(addon.getSetting("location"),addon.getSetting("latitude"),addon.getSetting("longitude"))
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
   log("v%s --> Start" % addonVersion, force=True)
   main()
   monitor = xbmc.Monitor()
   while not monitor.waitForAbort(5):
     main()
   log("v%s --> Stop" % addonVersion, force=True)
