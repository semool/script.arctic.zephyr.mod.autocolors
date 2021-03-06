#!/usr/bin/python
# coding: utf-8

import xbmc, xbmcaddon

addon = xbmcaddon.Addon()
addonName = addon.getAddonInfo("name")
addonId = addon.getAddonInfo("id")
addonVersion = addon.getAddonInfo("version")

INFO = xbmc.LOGINFO
WARNING = xbmc.LOGWARNING
DEBUG = xbmc.LOGDEBUG
ERROR = xbmc.LOGERROR

def log(txt,loglevel=DEBUG,force=False):
   if (addon.getSettingBool('debug') or force) and loglevel not in [WARNING, ERROR]:
      loglevel = INFO

   message = u'[%s] %s' % (addonId, txt)
   xbmc.log(msg=message, level=loglevel)
