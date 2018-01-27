#!/usr/bin/python3
#
# https://en.wikipedia.org/wiki/S.M.A.R.T.#Known_ATA_S.M.A.R.T._attributes
# https://wiki.gentoo.org/wiki/Udisks
# https://github.com/GNOME/d-feet  (useful DBus GUI exploration tool)
#
# Relevant attributes according to Google study:
#  5  Reallocated_Sector_Ct
# 197 Current_Pending_Sector
# 198 Offline_Uncorrectable
#
# Dump Format:
# ID# ATTRIBUTE_NAME  FLAG  VALUE  WORST THRESH VALUE ??? ???
# 3,  'spin-up-time', 39,   206,  179,   21,    6691, 2,   {}
# Note:
# hours returned in milli-sec
# temperatures returned in milli-kelvin

import xml.etree.ElementTree
import dbus

DBUS_IF_PROPERITES = "org.freedesktop.DBus.Properties"
DBUS_IF_INTROSPECTABLE = "org.freedesktop.DBus.Introspectable"
DBUS_IF_DRIVE_ATA = "org.freedesktop.UDisks2.Drive.Ata"

DBUS_SERVICE = "org.freedesktop.UDisks2"
DBUS_PATH = "/org/freedesktop/UDisks2/drives"


def dbus_to_py(v):
    """Convert the dbus subclasses to the proper python base types"""
    if isinstance(v, dbus.Array):
        return [dbus_to_py(x) for x in v]
    elif isinstance(v, dbus.Struct):
        return tuple([dbus_to_py(x) for x in v])
    elif isinstance(v, dbus.Dictionary):
        return {dbus_to_py(a): dbus_to_py(b) for a, b in v.items()}
    elif isinstance(v, str):
        return str(v)
    elif isinstance(v, int):
        return int(v)
    return v

if __name__ == "__main__":
    bus = dbus.SystemBus()
    obj = bus.get_object(DBUS_SERVICE, DBUS_PATH)
    if_intro = dbus.Interface(obj, DBUS_IF_INTROSPECTABLE)
    xml_str = if_intro.Introspect()
    root = xml.etree.ElementTree.fromstring(xml_str)
    for node in root:
        drive_name = node.attrib["name"]
        print ("=" * 50)
        print (drive_name)
        print ("=" * 50)

        obj_drive = bus.get_object(DBUS_SERVICE, DBUS_PATH + "/" + drive_name)

        if_prop = dbus.Interface(obj_drive, DBUS_IF_PROPERITES)
        v = dbus_to_py(if_prop.GetAll(DBUS_IF_DRIVE_ATA))

        for tag, val in v.items():
            print (tag, val)
        if v["SmartEnabled"]:
            if_ata = dbus.Interface(obj_drive, DBUS_IF_DRIVE_ATA)
            v = dbus_to_py(if_ata.SmartGetAttributes({}))
            for row in v:
                print(row)
