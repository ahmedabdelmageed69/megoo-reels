# megoo-reels

Daily AI-tips Reels for Instagram **@_megoo.me**.

- Every morning, a Claude scheduled task writes the post, builds the Reel and the carousel, and pushes them to `reels/YYYY-MM-DD/`.
- GitHub Pages serves the video publicly, so Instagram can fetch it.
- At **17:00 UTC** (8 PM Cairo in summer, 7 PM in winter), `.github/workflows/publish.yml` posts the Reel through the Instagram API.
- Every Monday, `.github/workflows/refresh-token.yml` renews the 60-day Instagram token.

## Stop a post
Add an empty file named `HOLD` inside that day's folder before 8 PM (the GitHub mobile app works).
To post a specific day by hand, go to **Actions → Publish Reel to Instagram → Run workflow** and enter the date.

## One-time setup
1. Keep this repo **public**. Then go to **Settings → Pages → Deploy from a branch → main / (root)**.
2. Go to **Settings → Secrets and variables → Actions** and add these secrets:
   - `IG_USER_ID`: your Instagram user ID, from the Meta app's "API setup with Instagram login" page.
   - `IG_ACCESS_TOKEN`: the long-lived access token from that same page.
   - `GH_PAT`: a fine-grained GitHub token for this repo only, with **Secrets: Read and write**. It lets the weekly job save the renewed Instagram token.
3. **Settings → Actions → General → Workflow permissions:** choose **Read and write**.

## Build a post by hand
```
tools/setup_fonts.sh                       # once
python3 tools/build.py post.json reels/2026-10-05   # needs python3, numpy, scipy, playwright+chromium, ffmpeg
```


<!-- Security scan triggered at 2026-10-07 11:53:32 -->