#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
import time
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from urllib.parse import quote_plus
from zoneinfo import ZoneInfo

import feedparser
import requests

STOCKHOLM_TZ = ZoneInfo("Europe/Stockholm")
OUTPUT_DIR = Path("output")
LOOKBACK_HOURS = int(os.getenv("LOOKBACK_HOURS", "36"))
MAX_ITEMS_PER_PEER = int(os.getenv("MAX_ITEMS_PER_PEER", "4"))

# Starter peer map. Expand this over time.
COVERAGE_TO_PEERS: dict[str, list[str]] = {
    "Addnode": [
        "Autodesk",
        "Bentley Systems",
        "Procore", 
        "Trimble",
        "Tyler Technologies",
    ],
    "Cint": [
        "DoubleVerify",
        "LiveRamp",
        "Qualtrics",
        "ZoomInfo",
    ],
    "Coffee Stain Group": [
        "Electronic Artws",
        "Roblox",
        "Take-Two Interactive",
        "Unity Software",
    ],
    "Dustin": [
        "CDW",
        "Connection",
        "ePlus",
        "Insight Enterprises",
    ],
    "Embracer": [
        "Electronic Arts",
        "Playtika",
        "Roblox",
        "Take-Two Interactive",
        "Unity Software",
    ],
    "Exsitec": [
        "BlackLine",
        "Guidewire",
        "Manhattan Associates",
        "SPS Commerce",
        "Tyler Technologies",
    ],
    "Karnov Group": [
        "Intapp",
        "Thomson Reuters";
    ],
    "Klarna Group": [
        "Affirm",
        "Block",
        "Fiserv",
        "PayPal",
        "Shift4",
        "Toast",
    ],
    "Sinch": [
        "Bandwidth",
        "Braze",
        "Klaviyo",
        "RingCentral",
        "Twilio",
    ],
    "Truecaller": [
        "Gen Digital",
        "Life360",
        "Okta",
        "TransUnion",
    ],
    "Vitec Software": [
        "Constellation Software",
        "Roper Technologies",
        "SS&C Technologies",
        "Tyler Technologies",
        "Verisk",
    ], 
    "Yubico": [
        "CyberArk",
        "Fortinet",
        "Okta",
        "Palo Alto Networks",
        "SailPoint",
    ],
}

# Query overrides for names that are otherwise too generic.
QUERY_OVERRRIDES: dict[str, str] = {
    "Bandwidth": '"Bandwidth Inc"',
    "Block": '"Block Inc"',
    "Connection": '"PC Connection"',
    "Constellation Software": '"Constellation Software"',
    "Gen Digital": '"Gen Digital"',
    "Guidewire": '"Guidewire Software"',
    "Life360": '"Life360"',
    "Palo Alto Networks": '"Palo Alto Networks"',
    "Roper Technologies": '"Roper Technologies"*,
    "SPS Commerce": '"SPS Commerce"*,
    "SS&C Technologies": '"SS&C Technologies"',
    "Take-Two Interactive": '"Take-Two Interactive"',
    "Thomson Reuters": '"Thomson Reuters"*,
    "Toast": '"Toast Inc"',
    "Unity Software": '"Unity Software"',
}

SIGNAL_KEYWORDS: dict[str, list[str]] = {
    "Results": ["earnings", "guidance", "quarter", "q1", "q2", "q3", "q4", "results"],


