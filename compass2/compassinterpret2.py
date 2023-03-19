# Main CompassBG script
import compass
from json import load, dump
from os import listdir, getenv, path
from types import SimpleNamespace
from fileCodeTranslate import translateDict
from datetime import datetime
from requests import get
from dateutil import tz, parser

appdata = getenv('LOCALAPPDATA') + '\CompassBG'
cfgLoc = appdata + "\cfg.json"

# Load config file as dictionary
tempCfg = load(open(cfgLoc, 'r'))
# Change the names of keys so the code doesn't break
tempCfg = translateDict(tempCfg, "code")
# Convert dictionary to namespace 
cfg = SimpleNamespace(**tempCfg)

# UTC to Local
def compassTimeTo24h(timeStr):
    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()
    utc = parser.parse(timeStr.replace('Z', ''))
    utc = utc.replace(tzinfo=from_zone)
    central = utc.astimezone(to_zone)
    return central.strftime('%H:%M')

# Get time information
now = datetime.now()
todayDate = now.strftime("%Y-%m-%d")
todayDate='2023-03-21'
# print(todayDate)

def getPeriods(unm, pwd):
    c = compass.CompassAPI(unm, pwd)
    events = c.get_calender_events_by_user(todayDate)

    periods = []
    for period in events:
        periodInfo = {}
        periodInfo["title"]=period["title"]
        periodInfo["starttime"]=period["start"]
        periodInfo["finishtime"]=period["finish"]

        instanceId=period["instanceId"]
        lessons = c.get_lessons_by_instance_id(instanceId)
        
        lessonInstanceId=0
        for i in range(len(lessons['Instances'])):
            lessonInstance = lessons['Instances'][i]
            if lessonInstance['st'] == period["start"]:
                lessonInstanceId=i

        periodInfo['location']=lessons['Instances'][lessonInstanceId]['l']

        periods.append(periodInfo)
    return periods

    
(unm, pwd)=(cfg.unm, cfg.pwd)

periods = getPeriods(unm, pwd)

for i in periods:
    i["starttime"]=compassTimeTo24h(i["starttime"])
    i["finishtime"]=compassTimeTo24h(i["finishtime"])
    print(i)