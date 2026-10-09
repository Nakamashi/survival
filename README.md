# Survival Island

A static, teacher-operated classroom activity. Open `index.html`, or serve the repository root with `python -m http.server 8000` and visit the local server. No build, package installation, backend, or API is required.

Choose 1–8 groups, click START, and click a group heading to choose up to three items. CONFIRM saves choices in click order. Closing the dialog or pressing Escape discards unconfirmed edits. Activities are saved in this browser's localStorage; refreshing restores the groups view. START SCREEN offers continuing or starting a new activity, with confirmation before replacing an existing activity.

Original JPEGs remain in `media/`. Image paths are relative to the page, including when hosted at `/survival/` on GitHub Pages. The main layout is designed for 1920 × 1080 projection. Smaller screens allow horizontal group scrolling and a two-column item picker.

## GitHub Pages

In repository Settings → Pages, choose **Deploy from a branch**, branch **main**, folder **/ (root)**. Once the completed commit is pushed and Pages deployment succeeds, the expected address is `https://nakamashi.github.io/survival/`. Publication and this URL's availability must be verified separately.

## Browser checks

The regression suite uses Python Playwright, only as a development test tool:

```sh
python -m http.server 8000
# In another terminal, with Python Playwright and Chromium available:
python tests/browser_checks.py
```

The server must serve the repository root on port 8000. Tests exercise selection limits, editing/canceling, storage restoration, new activities, image loading, keyboard access, and the projection layout.
