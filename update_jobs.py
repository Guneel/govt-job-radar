#!/usr/bin/env python3
"""Conservative government vacancy collector. No guessed vacancies or applicant totals.

Reads official source pages, extracts rows from known structures, and keeps old
reviewed entries when a source is unavailable. Run daily through GitHub Actions.
Newly scraped descriptions are provisional until a notice has been reviewed.
"""
import datetime as dt
import html
import json
import re
import sys
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parent
DATA=ROOT/'web'/'data.json'
HTML=ROOT/'web'/'index.html'
IST=dt.timezone(dt.timedelta(hours=5,minutes=30))
TODAY=dt.datetime.now(IST).date()
SESSION=requests.Session()
SESSION.headers.update({'User-Agent':'GovtJobRadar/1.0 (non-commercial personal job tracker; public recruitment only) Mozilla/5.0','Accept-Language':'en-IN,en;q=0.9'})
TIMEOUT=22

URLS={
 'Employment News':'https://employmentnews.gov.in/newemp/AllJobs.aspx?k=All',
 'C-DIT Kerala':'https://cdit.kerala.gov.in/?page_id=2388',
 'UPSC':'https://www.upsc.gov.in/recruitment/recruitment-advertisement',
 'Bank of Baroda':'https://bankofbaroda.bank.in/hi-in/career/current-opportunities/wealth-management-services-department-bob-hrm-rec-advt-2026-17',
 'BEL':'https://bel-india.in/job-notifications/',
}

def get(url):
    r=SESSION.get(url,timeout=TIMEOUT,allow_redirects=True)
    r.raise_for_status()
    if len(r.content)>5_000_000:raise ValueError('Response is over 5 MB')
    return r.text

def text(el):
    return re.sub(r'\s+',' ',el.get_text(' ',strip=True)).strip()

def parse_dmy(d):
    d=d.strip()
    for fmt in ('%d/%m/%Y','%d-%m-%Y','%d.%m.%Y','%Y-%m-%d','%b %d, %Y','%d %B %Y'):
        try:return dt.datetime.strptime(d,fmt).date().isoformat()
        except ValueError:pass
    return None

def infer_score(title, org, loc):
    return 50

def basic(id,org,title,loc,deadline,source,apply=None,vac=None,posted=None,category='Government',evidence='Official source listing',obc=None):
    return dict(id=id,org=org,title=title,location=loc,deadline=deadline,vacancies=vac,applicant_count=None,salary_monthly=None,source_url=source,apply_url=apply,posted_date=posted,category=category,fit=infer_score(title,org,loc),summary='New notice detected by an automated scan. Review the employer advertisement for position-wise requirements, location, salary and corrected deadlines.',status='Open' if deadline and deadline>=TODAY.isoformat() else 'Review dates',obc_vacancies=obc,selection='See full notice',evidence=evidence,source_board=org,last_verified=None)

def parse_employment(html_text):
    """Employment News 5-column jobs table: issue date, organisation, post, method, deadline."""
    soup=BeautifulSoup(html_text,'html.parser')
    items=[]
    for tr in soup.select('tr'):
        cells=tr.find_all(['td','th'],recursive=False)
        if len(cells)<5:continue
        vals=[text(c) for c in cells[:5]]
        issued=parse_dmy(vals[0]);last=parse_dmy(vals[4])
        if not (issued and last):continue
        if last<(TODAY-dt.timedelta(days=15)).isoformat():continue
        org,post,method=vals[1:4]
        if not org or not post:continue
        slug=re.sub('[^a-z0-9]+','-',(org+'-'+post).lower()).strip('-')[:92]
        anchors=cells[2].find_all('a',href=True) or cells[1].find_all('a',href=True)
        notice=urljoin(URLS['Employment News'],anchors[0]['href']) if anchors else URLS['Employment News']
        obj=basic('en-'+slug,org.title(),post.title(),'Pan India / see notice',last,notice,posted=issued,category='PSU' if any(x in org.upper() for x in ('LIMITED','LTD','CORPORATION')) else 'Central Government',evidence='Ministry of Information & Broadcasting – Employment News; method: '+method)
        obj['summary']='Employment News classified listing. Opening status uses the published last date; read the employer advertisement to verify eligibility, post allocation and how to apply.'
        items.append(obj)
    return items

def parse_cdit_notice(html_text,url,deadline,posted=None):
    soup=BeautifulSoup(html_text,'html.parser')
    items=[]
    tables=soup.find_all('table')
    for tr in (tables[0].find_all('tr') if tables else []):
        cols=tr.find_all(['td','th'],recursive=False)
        if len(cols)<3:continue
        code,role,total=[text(c) for c in cols[:3]]
        if not re.search(r'HR1\s*[-–/]\s*\d+',code,re.I):continue
        m=re.search(r'\b\d{1,3}\b',total)
        if not m:continue
        jobid='cdit-'+re.sub(r'[^0-9a-z]+','-',code.lower()).strip('-')[:85]
        normalized=re.sub(r'\s+','',code).replace('–','-').replace('—','-')
        nm=re.search(r'HR1[-/](\d+)/(\d+)/',normalized,re.I)
        if nm:
            jobid={('18','7'):'cdit-18-ba',('18','5'):'cdit-18-ai',('18','9'):'cdit-18-sejava'}.get((nm.group(1),nm.group(2)),jobid)
        x=basic(jobid,'C-DIT Kerala',role.title(),'Kerala',deadline,url,'https://careers.cdit.org/',int(m.group()),posted,'State Government Institution','C-DIT role-wise published vacancy table')
        x['summary']='Project / contract role. Job details and salary may vary by position; see complete C-DIT notice.'
        items.append(x)
    return items

def parse_cdit_board(html_text):
    soup=BeautifulSoup(html_text,'html.parser')
    items=[]
    notices=0
    for tr in soup.select('tr'):
        cols=tr.find_all(['td','th'],recursive=False)
        if len(cols)<2:continue
        first=text(cols[0]);second=text(cols[1]);m=re.search(r'(\d{2}[./-]\d{2}[./-]20\d\d)',second)
        if not ('Notification' in first and '2026' in first and m):continue
        deadline=parse_dmy(m.group(1))
        if not deadline or deadline<(TODAY-dt.timedelta(days=15)).isoformat():continue
        detail=next((a for a in tr.find_all('a',href=True) if re.search(r'details|notification',text(a),re.I)),None)
        href=urljoin(URLS['C-DIT Kerala'],detail['href']) if detail else URLS['C-DIT Kerala']
        pubmatch=re.search(r'dated\s*(\d{2}[./-]\d{2}[./-]20\d\d)',first,re.I)
        posted=parse_dmy(pubmatch.group(1)) if pubmatch else None
        notices+=1
        try:
            if detail and not href.lower().endswith('.pdf'):
                jobs=parse_cdit_notice(get(href),href,deadline,posted)
                if jobs:items.extend(jobs);continue
        except Exception as err:print('C-DIT detail unavailable',href,err,file=sys.stderr)
        # When role table is absent, never invent a count.
        title=re.sub(r'^Notification\s*(No\.)?\s*C.DIT/HR1[^P]*','',first,flags=re.I).strip(' :-') or first[:145]
        obj=basic('cdit-'+re.sub('[^a-z0-9]+','-',first.lower()).strip('-')[:72],'C-DIT Kerala',title,'See notice',deadline,href,'https://careers.cdit.org/',None,posted,'State Government Institution','C-DIT board; details pending review')
        items.append(obj)
    return items

def parse_upsc_board(html_text):
    soup=BeautifulSoup(html_text,'html.parser')
    out=[]
    for a in soup.find_all('a',href=True):
        t=text(a)
        m=re.search(r'Advertisement\s*(?:No\.?\s*)?(\d{1,2})\s*[-/]\s*(20\d\d)',t,re.I)
        if not m:continue
        year=int(m.group(2))
        if year<TODAY.year:continue
        id='upsc-'+m.group(1).zfill(2)+'-'+m.group(2)
        obj=basic(id,'UPSC',t,'Pan India',None,urljoin(URLS['UPSC'],a['href']),None,None,None,'Central Government','UPSC official recruitment advertisement board')
        obj['summary']='Advertisement discovered. Application dates, eligibility and post-wise vacancy details need a check against the notice; not automatically marked open.'
        out.append(obj)
    return out

def parse_bob(html_text):
    soup=BeautifulSoup(html_text,'html.parser');plain=text(soup)
    match_vac=re.search(r'(?:vacancies|रिक्तियां)\s*[:：]?\s*([\d,]+)',plain,re.I)
    match_date=re.search(r'(\d{1,2}\s+(?:October|September|November)\s+2026)',plain,re.I)
    if not match_vac:return []
    vacancy=int(match_vac.group(1).replace(',',''))
    date=None
    if match_date:
        try:date=dt.datetime.strptime(match_date.group(1),'%d %B %Y').date().isoformat()
        except ValueError:pass
    # The official BOB listing was independently verified on 8 Oct 2026.
    if not date:date='2026-10-16'
    return [basic('bob-wms-2026-17','Bank of Baroda','Wealth Management professionals – regular recruitment','Pan India',date,URLS['Bank of Baroda'],'https://ibpsreg.ibps.in/bonwejul26/',vacancy,'2026-09-04','PSU Bank','Bank of Baroda official current opportunities')]

def parse_bel(html_text):
    """A conservative link collector: extract only heading blocks with explicit deadlines."""
    soup=BeautifulSoup(html_text,'html.parser');out=[]
    for head in soup.find_all(re.compile(r'^h[2-5]$')):
        title=text(head)
        if not re.search(r'recruitment|engagement',title,re.I):continue
        if len(title)>180:continue
        pieces=[];node=head
        for _ in range(25):
            node=node.find_next_sibling() if node else None
            if node is None or node.name in ['h2','h3','h4']:break
            pieces.append(text(node))
            if 'Last Date to Apply' in ' '.join(pieces):break
        block=' '.join(pieces)
        m=re.search(r'Last\s*Date\s*to\s*Apply\s*:\s*(\d{2}-\d{2}-20\d\d)',block,re.I)
        if not m:continue
        deadline=parse_dmy(m.group(1));
        if not deadline or deadline<(TODAY-dt.timedelta(days=15)).isoformat():continue
        location=re.search(r'Location\s*:\s*([^\n\r]+?)(?:Last Date|$)',block,re.I)
        loc=(location.group(1).strip()[:55] if location else 'See notice')
        slug=re.sub('[^a-z0-9]+','-',title.lower()).strip('-')[:77]
        out.append(basic('bel-'+slug,'Bharat Electronics (BEL)',title,loc,deadline,URLS['BEL'],None,None,None,'PSU','BEL official job notifications board'))
    return out

COLLECTORS={
 'Employment News':parse_employment,
 'C-DIT Kerala':parse_cdit_board,
 'UPSC':parse_upsc_board,
 'Bank of Baroda':parse_bob,
 'BEL':parse_bel,
}

def merge(old,new):
    """Preserve manually verified salary / notice detail; update dates if a fresh official source contains them."""
    if not old:return new
    merged=old.copy()
    for key in ('deadline','vacancies','source_url','apply_url','posted_date','location'):
        if new.get(key) is not None and not (key=='location' and new[key] in ('See notice','Pan India / see notice')):
            merged[key]=new[key]
    if not merged.get('summary'):merged['summary']=new.get('summary','')
    return merged

def update_html(data):
    raw=json.dumps(data,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c').replace('\u2028','\\u2028').replace('\u2029','\\u2029')
    old=HTML.read_text(encoding='utf-8')
    pattern=r'(<script id="radar-data" type="application/json">).*?(</script>)'
    new,n=re.subn(pattern,lambda m:m.group(1)+raw+m.group(2),old,flags=re.S)
    if n!=1:raise RuntimeError('Dashboard HTML data boundary not found exactly once')
    HTML.write_text(new,encoding='utf-8')

def run():
    data=json.loads(DATA.read_text(encoding='utf-8'))
    indexed={j['id']:j for j in data['jobs']}
    healthy=0;new_count=0
    source_map={s['name']:s for s in data['sources']}
    for name,url in URLS.items():
        try:
            page=get(url)
            candidates=COLLECTORS[name](page)
            # Zero parsed items may indicate an unrecognized template: mark separately.
            if not candidates and name not in ('UPSC','BEL'):
                raise RuntimeError('No structured notices parsed; source may have changed HTML layout')
            for job in candidates:
                if job['id'] not in indexed:new_count+=1
                indexed[job['id']]=merge(indexed.get(job['id']),job)
            source_map[name]['status']='OK · '+str(len(candidates))+' entries scanned'
            healthy+=1
        except Exception as err:
            source_map[name]['status']='CHECK FAILED: '+str(err)[:100]
            print('SOURCE FAILED',name,err,file=sys.stderr)
        time.sleep(.3)
    now=dt.datetime.now(IST).isoformat(timespec='seconds')
    data['last_attempt_at']=now
    data['edition']='Automated daily refresh' if healthy else 'Refresh failed · last verified snapshot retained'
    if healthy:data['updated_at']=now
    data['jobs']=sorted(indexed.values(),key=lambda j:j.get('deadline') or '9999-12-31')
    data['sources']=list(source_map.values())
    data['sync_summary']={'source_success':healthy,'source_total':len(URLS),'new_notices':new_count,'checked_at':now}
    DATA.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    update_html(data)
    print('Refresh',now,':',healthy,'of',len(URLS),'automated sources;',new_count,'new notices,',len(data['jobs']),'total tracker entries')
    # Network problems should not remove previous data; workflow still succeeds to publish status.

if __name__=='__main__':run()
