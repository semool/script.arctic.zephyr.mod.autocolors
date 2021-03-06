import xbmc, xbmcaddon, xbmcvfs
import simplecache
import json
import xml.etree.ElementTree as ET
import datetime
from resources.lib.astral import LocationInfo
from resources.lib.astral.sun import sun

addon = xbmcaddon.Addon("script.arctic.zephyr.mod.autocolors")
addonName = addon.getAddonInfo("name")
addonVersion = addon.getAddonInfo("version")
cache = simplecache.SimpleCache()

def main():

   # Get Debug Setting
   debug = addon.getSetting("debug")

   # Get active skin name
   activeskin = xbmc.getSkinDir()
   if debug == "true":
      xbmc.log("%s --> Active Skin: %s" % (addonName, activeskin),level=xbmc.LOGINFO)

   if activeskin == "skin.arctic.zephyr.mod":

      # Dont switch when yes/no Dialog is open [id:10100]
      data = json.dumps({"jsonrpc":"2.0","method":"GUI.GetProperties","params":{"properties":["currentwindow"]},"id":1})
      try:
         result = json.loads(xbmc.executeJSONRPC(data))
         windowid = result['result']['currentwindow']['id']
      except:
        windowid = False
      if debug == "true":
         windowname = result['result']['currentwindow']['label']
         xbmc.log("%s --> ActiveWindowID: %s (%s)" % (addonName, windowid, windowname),level=xbmc.LOGINFO)

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

         if player == "false":
            playcheck = xbmc.Player().isPlaying()
         else:
            playcheck = False
         if debug == "true":
            xbmc.log("%s --> Playercheck: %s" % (addonName, playcheck),level=xbmc.LOGINFO)

         # When Player not play anything
         if not playcheck:

            if saver == "true":
               screensaver = False
               if debug == "true":
                  xbmc.log("%s --> Screensavercheck: %s" % (addonName, screensaver),level=xbmc.LOGINFO)
            else:
               #Check if Screensaver is active
               data = json.dumps({'jsonrpc': '2.0', 'method': 'XBMC.GetInfoBooleans', 'params': { "booleans": ["System.ScreenSaverActive"] }, 'id': 1})
               try:
                  result = json.loads(xbmc.executeJSONRPC(data))
                  screensaver = result['result']['System.ScreenSaverActive']
                  if debug == "true":
                     xbmc.log("%s --> Screensaver Status: %s" % (addonName, screensaver),level=xbmc.LOGINFO)
               except:
                  screensaver = False
                  if debug == "true":
                     xbmc.log("%s --> Screensaver Status: unknown" % (addonName),level=xbmc.LOGINFO)

            if not screensaver:

               # Reading skin setting: is autocolor enabled
               try:
                  skinaddon = xbmcaddon.Addon("skin.arctic.zephyr.mod")
                  skinProfile = xbmcvfs.translatePath(skinaddon.getAddonInfo("profile"))
                  skinSettings = skinProfile + "settings.xml"
                  if debug == "true":
                     xbmc.log("%s --> Skin Profile Path: %s" % (addonName, skinSettings),level=xbmc.LOGINFO)
                  tree = ET.parse(skinSettings)
                  searchsetting = tree.find(".//setting[@id='daynight.autocolor']")
                  autocolor = searchsetting.text
                  if debug == "true":
                     xbmc.log("%s --> Autocolor enabled: %s" % (addonName, autocolor),level=xbmc.LOGINFO)
               except:
                  autocolor = "true"
                  if debug == "true":
                     xbmc.log("%s --> Autocolor enabled in Fallback Mode: No Skin Setting Found. Disable this Addon to deactivate automatic color switch: %s" % (addonName , autocolor),level=xbmc.LOGINFO)

               if autocolor == "true":

                  # Get current active Color Theme
                  data = json.dumps({'jsonrpc': '2.0', 'method': 'Settings.GetSettingValue', 'params': {'setting':'lookandfeel.skincolors'}, 'id': 1})
                  try:
                     result = json.loads(xbmc.executeJSONRPC(data))
                     activecolor = result['result']['value']
                  except:
                     activecolor = False
                  if debug == "true":
                     xbmc.log("%s --> Current Theme Color: %s" % (addonName, activecolor),level=xbmc.LOGINFO)

                  # Get current time and timezone
                  current_time = datetime.datetime.now().strftime("%H:%M:%S")
                  try:
                     cachedata = cache.get("timezone")
                     if cachedata:
                        local_timezone = cachedata
                  except:
                     local_timezone = datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo
                     cache.set("timezone", local_timezone)

                  # Calculate Sunrise -> Sunset
                  if sunchange == "true":
                     try:
                        cachedata = cache.get(location)
                        if cachedata:
                           start = cachedata["start"]
                           end = cachedata["end"]
                     except:
                        city = LocationInfo(latitude=latitude, longitude=longitude)
                        sundata = sun(city.observer, tzinfo=local_timezone)
                        start = sundata["sunrise"].strftime("%H:%M:%S")
                        end = sundata["sunset"].strftime("%H:%M:%S")
                        times = {"start": start, "end": end}
                        cache.set(location, times)

                  # Timeframe for Light Theme Color
                  if debug == "true":
                     xbmc.log("%s --> Light Theme Timeframe: %s -> %s (%s)" % (addonName, start, end, local_timezone),level=xbmc.LOGINFO)

                  # Check timeframe and switch Theme Color
                  if current_time > start and current_time < end:
                     # Set Light Theme
                     if activecolor != light:
                        xbmc.log("%s --> Setting Theme Color: %s" % (addonName, light),level=xbmc.LOGINFO)
                        xbmc.executeJSONRPC(json.dumps({"jsonrpc":"2.0","method":"Settings.SetSettingValue","id":1,"params":{"setting":"lookandfeel.skincolors","value":light}}))
                  else:
                     # Set Dark Theme
                     if activecolor != dark:
                        xbmc.log("%s --> Setting Theme Color: %s" % (addonName, dark),level=xbmc.LOGINFO)
                        xbmc.executeJSONRPC(json.dumps({"jsonrpc":"2.0","method":"Settings.SetSettingValue","id":1,"params":{"setting":"lookandfeel.skincolors","value":dark}}))


if __name__ == '__main__':
   xbmc.log("%s v%s --> Start" % (addonName, addonVersion),level=xbmc.LOGINFO)
   monitor = xbmc.Monitor()
   while not monitor.waitForAbort(5):
     main()
   xbmc.log("%s v%s --> Stop" % (addonName, addonVersion),level=xbmc.LOGINFO)