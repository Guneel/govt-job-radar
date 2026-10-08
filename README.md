# Govt Job Radar — daily official-source tracker

**A working, single-page HTML dashboard, with a deployable scheduled data collector.**

The starting snapshot was independently researched on **8 October 2026**. It includes official advertisements from UPSC, Bank of Baroda, C-DIT, BEL and Employment News. Information is deliberately conservative: a blank applicant count **does not** mean zero people applied; a blank vacancy count **does not** mean zero positions.

## Open the dashboard immediately

Open `web/index.html` in a desktop/mobile browser. It contains its own initial data: **no server, account or internet is required to view/search the snapshot**. The original source links and application links do require internet access. Bookmarks and application status are saved to that browser's local storage, so they do not sync between devices.

## Make it refresh automatically every day

You need a **free GitHub account** and a new public repository. Setup takes roughly 5–10 minutes:

1. Create a public repository (e.g. `govt-job-radar`) and upload **all files and folders from this project**, including `.github/workflows/daily-refresh.yml`.
2. In that repository choose **Settings → Pages → Build and deployment → Source: GitHub Actions**.
3. In the **Actions** tab, select **Government Jobs · Daily Refresh → Run workflow** once to test and deploy.
4. Your dashboard opens at `https://YOUR_GITHUB_USERNAME.github.io/govt-job-radar/`. Bookmark that link.
5. The workflow reruns daily at **9:00 AM IST**. GitHub scheduling can run late or be paused on inactive repos. Check the **Actions** run log if a refresh is missed.

The workflow fetches selected recruitment board pages, updates `web/data.json`, writes the same data into the self-contained `web/index.html`, commits changes and publishes GitHub Pages. No paid service or API key is required. You must enable the workflow yourself; merely downloading this project does not activate daily updates.

## Data coverage and guarantees

**Automated collectors today:** Government Employment News vacancy table, C-DIT Kerala notification index and role listings, UPSC recruitment advertisement board, Bank of Baroda recruitment announcement (current 2026/17), and BEL recruitment list (best-effort). Other regulatory, PSU and state portals are displayed as direct official links but are **not yet automatically parsed**. That is why the app does not claim to cover every Indian government employer.

**Notice reading:** The collector parses official HTML pages, published deadlines, role names, and vacancies when the page exposes them. It does not currently perform general-purpose PDF or OCR extraction, so it **does not** claim to have fully extracted every PDF or evaluated eligibility. Some official portals are JavaScript-only, captcha protected or block bots, which can prevent an automated read. Failures appear in `web/data.json → sources → status`; existing notices are preserved instead of being replaced with guesses.

**Application counts:** Usually not available before the employer publishes a statistic. This column is explicitly **Not published** unless a confirmed total is supplied. Published number of vacancies is a different statistic and is never passed off as applicant count.

**Status:** The frontend recalculates deadlines using the current date in India and marks past notices as closed. Corrigenda/early closure cannot be detected perfectly: always check the employer advertisement before paying fees or relying on age relaxations. An official notice is not a verified confirmation that a portal accepts submissions today.

**Salary:** Advertised consolidated salaries and upper bounds are **not take-home salary**; allowances, deductions and posting city can change net pay significantly. Blank salaries are intentionally not guessed. The alignment score is a simple skills/location heuristic, not a guaranteed eligibility check or an exam success probability.

## Local test and manual refresh

```bash
pip install -r requirements.txt
python -m unittest discover -s tests -v
python update_jobs.py
python -m http.server 8000 --directory web
```
Then open `http://localhost:8000/`.

## Add or adjust jobs

- To adjust a role, edit `web/data.json` (not salary/count guesses), then run `python -c "import json; from update_jobs import update_html, DATA; update_html(json.loads(DATA.read_text()))"`.
- Source collectors live in `update_jobs.py`. Add a new official portal parser to `COLLECTORS`, and add its URL to `URLS`.
- Application status and bookmarks live only in browser localStorage, not `data.json`, so no personal application record is published to the repository.
- The source-list shortcuts are managed in `build_seed.py`. **Do not rerun `build_seed.py` after deployment** unless you deliberately want to reset the collected data.

## Expected refresh behaviour

Every day the script tries the five configured collectors. An accessible updated official source may introduce new listings; only dated listings are shown as open. New UPSC records without checked deadlines are retained under 'Review dates' and will be excluded from the default **Open only** view until verified. Older source observations remain as historical entries rather than silently disappearing. This is **partial official-source coverage**, not a promise that all national recruitments will be harvested automatically.

This project is not affiliated with any government department and never requests your government portal password, OTP, payment details, or identity document.
