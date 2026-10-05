#!/usr/bin/env python3
"""Refresh the 60-day Instagram token and print the new one (used by the weekly workflow)."""
import json, os, urllib.parse, urllib.request
q = urllib.parse.urlencode({'grant_type': 'ig_refresh_token', 'access_token': os.environ['IG_ACCESS_TOKEN']})
with urllib.request.urlopen(f'https://graph.instagram.com/refresh_access_token?{q}', timeout=60) as r:
    print(json.load(r)['access_token'])
