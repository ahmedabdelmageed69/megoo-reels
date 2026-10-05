#!/usr/bin/env python3
"""Publish today's Reel to Instagram (Instagram API with Instagram Login).
Env: IG_USER_ID, IG_ACCESS_TOKEN, PAGES_BASE (e.g. https://USER.github.io/megoo-reels), DATE (optional, YYYY-MM-DD; default = today in Cairo)
Looks for reels/<DATE>/reel.mp4 + caption.txt. Skips if the folder is missing, has a HOLD file, or was already posted.
"""
import json, os, sys, time, urllib.parse, urllib.request, urllib.error, datetime
from zoneinfo import ZoneInfo
API = 'https://graph.instagram.com'
uid, tok = os.environ['IG_USER_ID'], os.environ['IG_ACCESS_TOKEN']
base = os.environ['PAGES_BASE'].rstrip('/')
date = os.environ.get('DATE') or datetime.datetime.now(ZoneInfo('Africa/Cairo')).strftime('%Y-%m-%d')
d = f'reels/{date}'

def call(method, path, **params):
    params['access_token'] = tok
    data = urllib.parse.urlencode(params).encode()
    url = f'{API}/{path}' + ('' if method == 'POST' else '?' + data.decode())
    req = urllib.request.Request(url, data=data if method == 'POST' else None, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as r: return json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit(f'Instagram API error {e.code} on {path}: {e.read().decode()[:500]}')

if not os.path.isfile(f'{d}/reel.mp4'): print(f'No reel for {date}; nothing to post.'); sys.exit(0)
if os.path.exists(f'{d}/HOLD'): print(f'{date} is on HOLD; skipping.'); sys.exit(0)
if os.path.exists(f'{d}/posted.json'): print(f'{date} already posted; skipping.'); sys.exit(0)
caption = open(f'{d}/caption.txt', encoding='utf-8').read().strip()
video_url = f'{base}/{d}/reel.mp4'
for _ in range(20):  # wait until GitHub Pages serves the file
    try:
        with urllib.request.urlopen(urllib.request.Request(video_url, method='HEAD'), timeout=30) as r:
            if r.status == 200: break
    except Exception: pass
    print('waiting for GitHub Pages...'); time.sleep(30)
else: sys.exit(f'Video not reachable at {video_url}')

c = call('POST', f'{uid}/media', media_type='REELS', video_url=video_url, caption=caption, share_to_feed='true', thumb_offset='3000')
cid = c['id']; print('container', cid)
for _ in range(60):
    st = call('GET', cid, fields='status_code,status')
    print('status', st.get('status_code'))
    if st.get('status_code') == 'FINISHED': break
    if st.get('status_code') in ('ERROR', 'EXPIRED'): sys.exit(f'Instagram could not process the video: {st}')
    time.sleep(10)
else: sys.exit('Timed out waiting for Instagram to process the video')
m = call('POST', f'{uid}/media_publish', creation_id=cid)
info = call('GET', m['id'], fields='permalink,timestamp')
json.dump({'media_id': m['id'], **info}, open(f'{d}/posted.json', 'w'), indent=1)
print('Published:', info.get('permalink'))
