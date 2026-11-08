#!/usr/bin/env python3
"""Post the day's Reel to TikTok (Content Posting API v2). Used by .github/workflows/tiktok.yml.
  python3 scripts/tiktok.py connect CODE   -> trade the one-time login code for a refresh token; prints ONLY the token (the workflow saves it as a secret)
  python3 scripts/tiktok.py publish        -> post reels/<DATE>[/am]/reel.mp4 with its caption
Env: TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, TIKTOK_REFRESH_TOKEN (publish), DATE/SLOT (optional, like scripts/publish.py),
     OUT_REFRESH (file to write a rotated refresh token to), REDIRECT_URI (connect; must match the app's registered one).
Posting: if TikTok allows public posts for this app (after its audit), it posts publicly ("direct").
Before that, it sends the video to your TikTok inbox as a draft: open TikTok, tap the notification, then Post.
Skips a Reel that is missing, has a HOLD file, or already has tiktok.json.
"""
import datetime, json, os, sys, time, urllib.error, urllib.parse, urllib.request
from zoneinfo import ZoneInfo

API = 'https://open.tiktokapis.com/v2'
REDIRECT = os.environ.get('REDIRECT_URI', 'https://ahmedabdelmageed69.github.io/megoo-reels/tiktok/callback.html')

def http(method, url, data=None, headers=None, raw=None):
    body = raw if raw is not None else (json.dumps(data).encode() if isinstance(data, dict) and headers and 'json' in headers.get('Content-Type', '') else
                                        urllib.parse.urlencode(data).encode() if data else None)
    req = urllib.request.Request(url, data=body, method=method, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            txt = r.read().decode() or '{}'
    except urllib.error.HTTPError as e:
        txt = e.read().decode()
        if not txt.startswith('{'): sys.exit(f'TikTok HTTP {e.code} on {url.split("?")[0]}: {txt[:300]}')
    return json.loads(txt)

def token(grant, **kw):
    r = http('POST', f'{API}/oauth/token/', {'client_key': os.environ['TIKTOK_CLIENT_KEY'], 'client_secret': os.environ['TIKTOK_CLIENT_SECRET'],
                                            'grant_type': grant, **kw}, {'Content-Type': 'application/x-www-form-urlencoded'})
    if 'access_token' not in r: sys.exit(f'TikTok token error: {r.get("error")} {r.get("error_description", "")}')
    return r

def api(path, tok, data):
    r = http('POST', f'{API}{path}', data, {'Authorization': f'Bearer {tok}', 'Content-Type': 'application/json; charset=UTF-8'})
    err = r.get('error', {})
    if err.get('code', 'ok') != 'ok': sys.exit(f'TikTok API error on {path}: {err.get("code")} {err.get("message")}')
    return r.get('data', {})

def connect(code):
    print(token('authorization_code', code=code, redirect_uri=REDIRECT)['refresh_token'])

def publish():
    now = datetime.datetime.now(ZoneInfo('Africa/Cairo'))
    date = os.environ.get('DATE') or now.strftime('%Y-%m-%d'); slot = os.environ.get('SLOT') or ('am' if now.hour < 14 else 'pm')
    d = f'reels/{date}' + ('/am' if slot == 'am' else '')
    if not os.path.isfile(f'{d}/reel.mp4'): print(f'No {slot} reel for {date}; nothing to post.'); return
    if os.path.exists(f'{d}/HOLD'): print(f'{d} is on HOLD; skipping.'); return
    if os.path.exists(f'{d}/tiktok.json'): print(f'{d} already sent to TikTok; skipping.'); return
    t = token('refresh_token', refresh_token=os.environ['TIKTOK_REFRESH_TOKEN'])
    if t.get('refresh_token') and t['refresh_token'] != os.environ['TIKTOK_REFRESH_TOKEN'] and os.environ.get('OUT_REFRESH'):
        open(os.environ['OUT_REFRESH'], 'w').write(t['refresh_token'])          # TikTok rotated it: the workflow saves the new one
    tok = t['access_token']
    cap_file = f'{d}/tiktok.txt' if os.path.exists(f'{d}/tiktok.txt') else f'{d}/caption.txt'
    caption = open(cap_file, encoding='utf-8').read().strip()[:2200]
    video = open(f'{d}/reel.mp4', 'rb').read(); size = len(video)
    chunk = size if size <= 64_000_000 else 10_000_000; count = max(1, size // chunk)   # last chunk takes the remainder
    source = {'source': 'FILE_UPLOAD', 'video_size': size, 'chunk_size': chunk, 'total_chunk_count': count}
    levels = api('/post/publish/creator_info/query/', tok, {}).get('privacy_level_options', [])
    if 'PUBLIC_TO_EVERYONE' in levels:
        mode = 'direct'
        init = api('/post/publish/video/init/', tok, {'post_info': {'title': caption, 'privacy_level': 'PUBLIC_TO_EVERYONE', 'disable_comment': False,
                                                                     'disable_duet': False, 'disable_stitch': False, 'video_cover_timestamp_ms': 3000},
                                                       'source_info': source})
    else:
        mode = 'draft'
        print(f'Public posting not allowed yet for this app (options: {levels}); sending it to your TikTok inbox as a draft instead.')
        init = api('/post/publish/inbox/video/init/', tok, {'source_info': source})
    for k in range(count):
        a = k * chunk; b = size if k == count - 1 else a + chunk
        req = urllib.request.Request(init['upload_url'], data=video[a:b], method='PUT',
                                     headers={'Content-Type': 'video/mp4', 'Content-Length': str(b - a), 'Content-Range': f'bytes {a}-{b - 1}/{size}'})
        try: urllib.request.urlopen(req, timeout=600).read()
        except urllib.error.HTTPError as e: sys.exit(f'TikTok upload failed (chunk {k + 1}/{count}): HTTP {e.code} {e.read().decode()[:300]}')
    pid = init['publish_id']; status = 'UPLOADED'
    for _ in range(40):
        st = api('/post/publish/status/fetch/', tok, {'publish_id': pid}); status = st.get('status', status)
        print('status', status)
        if status in ('PUBLISH_COMPLETE', 'SEND_TO_USER_INBOX'): break
        if status == 'FAILED': sys.exit(f'TikTok could not process the video: {st.get("fail_reason")}')
        time.sleep(15)
    json.dump({'publish_id': pid, 'mode': mode, 'status': status, 'at': now.isoformat(timespec='seconds')}, open(f'{d}/tiktok.json', 'w'), indent=1)
    print('TikTok:', 'posted publicly' if mode == 'direct' else 'draft is waiting in your TikTok inbox (tap Post in the app)', f'({status})')

if __name__ == '__main__':
    connect(sys.argv[2]) if sys.argv[1] == 'connect' else publish()
