import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import streamlit as st

CLIENT_ID = st.secrets["DB_CLIENT_ID"]
API_KEY = st.secrets["DB_API_KEY"]

STATIONS = {
    "Hamburg Hbf": "8002549",
    "Amsterdam Centraal": "8400058"
}

ALLOWED_ICE_FROM_HAM = {107, 109, 111, 113, 115, 201, 203, 205, 207,
                        575, 519, 521, 523, 527, 581, 787, 789, 927, 228}
ALLOWED_ICE_FROM_AMS = {123, 125, 127, 129, 143, 145, 153, 227, 229, 231, 623, 625, 725}


def get_plan(eva_no, date_str, hour_str):
    url = f"https://apis.deutschebahn.com/db-api-marketplace/apis/timetables/v1/plan/{eva_no}/{date_str}/{hour_str}"
    headers = {
        "DB-Client-Id": CLIENT_ID,
        "DB-Api-Key": API_KEY,
        "accept": "application/xml"
    }
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    return ET.fromstring(r.content)


def find_connections(xml_root, allowed_trains, allowed_types):
    trains = []
    for stop in xml_root.findall('s'):
        dp = stop.find('dp')
        tl = stop.find('tl')
        if dp is None or tl is None:
            continue

        train_type = tl.attrib.get('c')
        train_nr = tl.attrib.get('n')

        if train_type not in allowed_types:
            continue
        try:
            if int(train_nr) not in allowed_trains:
                continue
        except ValueError:
            continue

        planned = dp.attrib.get('pt')
        depart_time = datetime.strptime(planned, "%y%m%d%H%M")
        trains.append({
            "train": f"{train_type} {train_nr}",
            "depart": depart_time.strftime("%H:%M"),
            "ppth": dp.attrib.get('ppth', 'N/A')
        })
    return trains
