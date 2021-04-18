![](https://raw.githubusercontent.com/semool/script.arctic.zephyr.mod.autocolors/master/icon.png)

## Arctic: Zephyr - Reloaded - Automatic Day/Night Colors

Install first: https://github.com/semool/script.module.astral/releases/

This little Addon switch the Skin Color Theme based on Time

The Time can set manualy or you can set your Location and the Theme will switch based on sunset/sunrise.

Disable the Automatic:
- Turn off this Addon
- Or add a setting "daynight.autocolor" to your Skin Settings. Example:
```
<control type="radiobutton" id="9804" description="Autocolor">
    <width>1310</width>
    <visible>ControlGroup(9100).HasFocus(9101) + System.HasAddon(script.arctic.zephyr.mod.autocolors)</visible>
    <include>DefSettingsButtonGradient</include>
    <label>$LOCALIZE[14078] $LOCALIZE[15111] $LOCALIZE[14013] $LOCALIZE[33027]/$LOCALIZE[33028]</label>
    <selected>Skin.HasSetting(daynight.autocolor)</selected>
    <onclick>Skin.ToggleSetting(daynight.autocolor)</onclick>
</control>
```
