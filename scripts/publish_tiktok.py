#!/usr/bin/env python3
"""Publish a Reel to TikTok (Content Posting API, direct post, file upload).
Env: TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, TIKTOK_REFRESH_TOKEN, DATE (optional, YYYY-MM-DD; default = today in Cairo), SLOT (optional, am|pm), TIKTOK_PRIVACY (default SELF_ONLY: an unaudited TikTok app can only post private; set PUBLIC_TO_EVERYONE once the app is audited)
Same folders and rules as publish.py (HOLD skips, tiktok.json marks it as posted). Prints the new refresh token on the last line as NEW_REFRESH_TOKEN=... so the workflow can save it.
"""
import json, os, sys, time, urllib.parse, urllib.request, urllib.error, datetime
from zoneinfo import ZoneInfo
API = 'https://open.tiktokapis.com'
now = datetime.datetime.now(ZoneInfo('Africa/Cairo'))
date = os.environ.get('DATE') or now.strftime('%Y-%m-%d')
slot = os.environ.get('SLOT') or ('am' if now.hour < 14 else 'pm')
d = f'reels/{date}' + ('/am' if slot == 'am' else '')

def req(url, data=None, headers=None, method='POST'):
    r = urllib.request.Request(url, data=data, headers=headers or {}, method=method)
    try:
        with urllib.request.urlopen(r, timeout=300) as resp: return resp.status, resp.read()
    except urllib.error.HTTPError as e:
        sys.exit(f'TikTok API error {e.code} on {url.split("?")[0]}: {e.read().decode()[:500]}')

def refresh():
    body = urllib.parse.urlencode({'client_key': os.environ['TIKTOK_CLIENT_KEY'], 'client_secret': os.environ['TIKTOK_CLIENT_SECRET'],
                                   'grant_type': 'refresh_token', 'refresh_token': os.environ['TIKTOK_REFRESH_TOKEN']}).encode()
    _, b = req(f'{API}/v2/oauth/token/', body, {'Content-Type': 'application/x-www-form-urlencoded'})
    j = json.loads(b)
    if 'access_token' not in j: sys.exit(f'TikTok token refresh failed: {j}')
    return j['access_token'], j.get('refresh_token')

access, new_refresh = refresh()
if new_refresh: print('::add-mask::' + new_refresh); print('NEW_REFRESH_TOKEN=' + new_refresh)
if not os.path.isfile(f'{d}/reel.mp4'): print(f'No {slot} reel for {date}; nothing to post.'); sys.exit(0)
if os.path.exists(f'{d}/HOLD'): print(f'{date} {slot} is on HOLD; skipping.'); sys.exit(0)
if os.path.exists(f'{d}/tiktok.json'): print(f'{date} {slot} already on TikTok; skipping.'); sys.exit(0)
title = open(f'{d}/caption.txt', encoding='utf-8').read().strip()[:2200]
video = open(f'{d}/reel.mp4', 'rb').read(); size = len(video)   # Reels are ~10 MB: one chunk
H = {'Authorization': f'Bearer {access}', 'Content-Type': 'application/json; charset=UTF-8'}
init = {'post_info': {'title': title, 'privacy_level': os.environ.get('TIKTOK_PRIVACY', 'SELF_ONLY'), 'disable_duet': False, 'disable_comment': False, 'disable_stitch': False},
        'source_info': {'source': 'FILE_UPLOAD', 'video_size': size, 'chunk_size': size, 'total_chunk_count': 1}}
_, b = req(f'{API}/v2/post/publish/video/init/', json.dumps(init).encode(), H)
j = json.loads(b)
if j.get('error', {}).get('code') != 'ok': sys.exit(f'TikTok init failed: {j}')
pid, up = j['data']['publish_id'], j['data']['upload_url']
req(up, video, {'Content-Type': 'video/mp4', 'Content-Length': str(size), 'Content-Range': f'bytes 0-{size-1}/{size}'}, 'PUT')
for _ in range(60):
    _, b = req(f'{API}/v2/post/publish/status/fetch/', json.dumps({'publish_id': pid}).encode(), H)
    st = json.loads(b)['data']; print('status', st.get('status'))
    if st.get('status') == 'PUBLISH_COMPLETE': break
    if st.get('status') == 'FAILED': sys.exit(f'TikTok could not publish: {st}')
    time.sleep(10)
else: sys.exit('Timed out waiting for TikTok to publish')
json.dump({'publish_id': pid, **st}, open(f'{d}/tiktok.json', 'w'), indent=1)
print('Published on TikTok:', pid)
