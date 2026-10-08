import json
from pathlib import Path
ROOT=Path(__file__).parent
D='2026-10-08'
# Date, amounts and counts only included if present on a referenced official notice.
def job(id, org, title, location, close, vacancies=None, salary=None, source='', apply=None, posted=None, category='Government', fit=50, summary='', status='Open', obc=None, mode='Not stated', evidence='Official notice', source_board=None):
    return dict(id=id,org=org,title=title,location=location,deadline=close,vacancies=vacancies,applicant_count=None,salary_monthly=salary,source_url=source,apply_url=apply,posted_date=posted,category=category,fit=50,summary=summary,status=status,obc_vacancies=obc,selection=mode,evidence=evidence,source_board=source_board or org,last_verified=D)
rows=[
job('upsc-12-2026','UPSC','Advertisement 12/2026 – direct recruitment','Pan India','2026-10-16',source='https://www.upsc.gov.in/recruitment/recruitment-advertisement',apply='https://upsconline.nic.in/',posted='2026-09-26',category='Central Government',fit=72,summary='Multiple central-government posts. Read individual post qualifications and locations before applying. PIB confirms the 26 Sep–16 Oct application window.',evidence='UPSC vacancy board + PIB 26 Sep 2026',mode='As specified per post'),
job('bob-wms-2026-17','Bank of Baroda','Wealth Management professionals – regular recruitment','Pan India','2026-10-16',1000,None,'https://bankofbaroda.bank.in/hi-in/career/current-opportunities/wealth-management-services-department-bob-hrm-rec-advt-2026-17','https://ibpsreg.ibps.in/bonwejul26/','2026-09-04','PSU Bank',69,'1,000 advertised vacancies across wealth management positions; individual post eligibility, locations, grade and pay require reading the detailed advertisement.','Open',None,'As per advertisement','Bank of Baroda official advertisement + registration portal'),
job('cdit-18-ba','C-DIT Kerala','Business Analyst','Kerala','2026-10-17',3,40000,'https://cdit.kerala.gov.in/?p=7707','https://careers.cdit.org/','2026-10-03','State Government Institution',75,'B.Tech CSE eligible; BRD, user stories, UAT and stakeholder work. Contract role, ₹30,000–40,000/month consolidated.', 'Open',None,'Written / skill test / interview','C-DIT notice HR1-18/7/2026'),
job('cdit-18-ai','C-DIT Kerala','Senior Software Engineer (AI)','Kerala','2026-10-17',1,70000,'https://cdit.kerala.gov.in/?p=7707','https://careers.cdit.org/','2026-10-03','State Government Institution',63,'RAG, LLM and AI assistant experience relevant; notice prefers minimum 5 years of professional experience. ₹60,000–70,000/month consolidated; contract.', 'Open',None,'Written / skill test / interview','C-DIT notice HR1-18/5/2026'),
job('cdit-18-sejava','C-DIT Kerala','Software Engineer (Java)','Kerala','2026-10-17',6,40000,'https://cdit.kerala.gov.in/?p=7707','https://careers.cdit.org/','2026-10-03','State Government Institution',43,'Requires Java/Spring Boot and API skills; ₹30,000–40,000/month consolidated on contract.', 'Open',None,'Written / skill test / interview','C-DIT notice HR1-18/9/2026'),
job('cdit-19-assistant','C-DIT Kerala','Project Assistant – Bangalore digitisation','Bengaluru','2026-10-19',1,20000,'https://careers.cdit.org/2026Con/DIgitizationBangalore.pdf','https://careers.cdit.org/','2026-10-06','State Government Institution',46,'Six-month or project-length contract in Bangalore at ₹20,000/month. Any bachelor’s degree; English and Malayalam desirable.', 'Open',None,'Online interview','C-DIT official notification HR1-19/2026'),
job('cdit-19-scan','C-DIT Kerala','Scanning Assistant – Bangalore digitisation','Bengaluru','2026-10-19',2,17500,'https://careers.cdit.org/2026Con/DIgitizationBangalore.pdf','https://careers.cdit.org/','2026-10-06','State Government Institution',20,'Temporary Bangalore role paying ₹17,500/month. ', 'Open',None,'Online interview','C-DIT official notification HR1-19/2026'),
job('mecl-accounts-2026','MECL','Accountant & other posts','Pan India','2026-10-11',None,None,'https://employmentnews.gov.in/newemp/AllJobs.aspx?k=All',None,'2026-09-12','PSU',31,'Employment News lists Accountant & Others and 11 October last date; read the employer advertisement to obtain role-wise vacancies and application instructions.','Open',None,'See employer notification','Government Employment News listing'),
job('bel-advisor-2026','Bharat Electronics (BEL)','Advisor – PDIC, Bengaluru','Bengaluru','2026-10-19',None,None,'https://bel-india.in/job-notifications/',None,None,'PSU',33,'BEL confirms a Bengaluru advisor advertisement and 19 October closing. Seniority and experience conditions must be checked in its PDF; application form may be offline.','Open',None,'Check BEL advert','BEL official recruitment board'),
job('upsc-11-ladakh-2026','UPSC','Advertisement 11/2026 – Ladakh posts only','Ladakh','2026-10-09',None,None,'https://www.upsc.gov.in/recruitment/recruitment-advertisement','https://upsconline.nic.in/', '2026-09-12','Central Government',28,'Only the UT of Ladakh subset is still within the 9 October window; other posts under advertisement 11/2026 closed 2 October.','Open',None,'As specified per post','PIB 10 Sep 2026'),
job('ndma-forest-2026','NDMA','Young Consultant – forest fire risk','Pan India','2026-10-18',None,None,'https://employmentnews.gov.in/newemp/AllJobs.aspx?k=All',None,'2026-08-31','Central Government',17,'Employment News lists a deputation engagement. May require existing government employment; verify before applying.','Open',None,'Deputation','Government Employment News listing'),
job('nbems-ed-2026','NBEMS','Executive Director','Pan India','2026-10-30',None,None,'https://employmentnews.gov.in/newemp/AllJobs.aspx?k=All',None,'2026-08-31','Central Government',10,'Senior executive post; selection and eligibility require separate notice.','Open',None,'See notification','Government Employment News listing'),
]
boards=[
 ['UPSC','https://www.upsc.gov.in/recruitment/recruitment-advertisement','Auto notice watch'],
 ['RBI','https://opportunities.rbi.org.in/Scripts/Vacancies.aspx','Board link / watch'],
 ['SEBI','https://www.sebi.gov.in/sebiweb/about/AboutAction.do?doVacancies=yes','Board link / watch'],
 ['IRDAI','https://irdai.gov.in/recruitment','Board link / watch'],
 ['Employment News','https://employmentnews.gov.in/newemp/AllJobs.aspx?k=All','Auto extraction'],
 ['C-DIT Kerala','https://cdit.kerala.gov.in/?page_id=2388','Auto extraction'],
 ['Bank of Baroda','https://bankofbaroda.bank.in/career/current-opportunities','Notice link / watch'],
 ['BEL','https://bel-india.in/job-notifications/','Notice link / watch'],
 ['C-DAC','https://www.cdac.in/index.aspx?id=current_jobs','Board link / watch'],
 ['IBPS','https://www.ibps.in/','Board link / watch'],
 ['SSC','https://ssc.gov.in/','Board link / watch'],
 ['TNPSC','https://www.tnpsc.gov.in/','Board link / watch'],
 ['KPSC Karnataka','https://kpsc.kar.nic.in/','Board link / watch'],
 ['ISRO','https://www.isro.gov.in/Careers.html','Board link / watch'],
 ['SBI Careers','https://sbi.co.in/web/careers/current-openings','Board link / watch'],
 ['NCS Government Jobs','https://www.ncs.gov.in/pages/govt-job-vacancies.aspx','Portal directory'],
]
result={'updated_at':'2026-10-08T07:36:00+05:30','edition':'Initial verified snapshot','jobs':rows,'sources':[{'name':a,'url':b,'coverage':c,'status':'Seed / setup required'} for a,b,c in boards], 'caveat':'Daily cloud updates begin only after GitHub Pages + Actions is set up. Applicants count means submitted applications, not open vacancies, and is normally undisclosed.'}
(ROOT/'web').mkdir(exist_ok=True)
(ROOT/'web'/'data.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
print('seeded',len(rows),'jobs',len(boards),'source portals')
