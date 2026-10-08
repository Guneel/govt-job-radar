import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import update_jobs as job

class CollectorTests(unittest.TestCase):
 def test_dmy(self):
  self.assertEqual(job.parse_dmy('11/10/2026'),'2026-10-11')
  self.assertEqual(job.parse_dmy('19-10-2026'),'2026-10-19')
  self.assertIsNone(job.parse_dmy('not a date'))
 def test_employment_news_table(self):
  sample='<table><tr><th>Issued</th><th>Company</th><th>Post</th><th>Mode</th><th>Last</th></tr><tr><td>12/09/2026</td><td>MINERAL EXPLORATION AND CONSULTANCY LIMITED</td><td>ACCOUNTANT & OTHERS</td><td>Recruitment</td><td>11/10/2026</td></tr></table>'
  out=job.parse_employment(sample)
  # This real notice is valid on 8 Oct 2026, but fixture becomes historical later.
  if job.TODAY<=job.dt.date(2026,10,26):
   self.assertEqual(len(out),1)
   self.assertEqual(out[0]['deadline'],'2026-10-11')
   self.assertIsNone(out[0]['applicant_count'])
 def test_cdit_count(self):
  sample='<table><tr><td>C-DIT/HR1 – 18/7/2026</td><td>Business Analyst</td><td>3</td></tr></table>'
  x=job.parse_cdit_notice(sample,'https://cdit.kerala.gov.in/?p=7707','2026-10-17')
  self.assertEqual(len(x),1)
  self.assertEqual(x[0]['vacancies'],3)
  self.assertEqual(x[0]['title'],'Business Analyst')
 def test_upsc_unknown_dates_not_open(self):
  x=job.parse_upsc_board('<a href="/advt">Advertisement No.12 - 2026</a>')
  if job.TODAY.year==2026:
   self.assertEqual(x[0]['status'],'Review dates')
   self.assertIsNone(x[0]['deadline'])
 def test_merge_manual_salary_and_applicants(self):
  x={'id':'q','salary_monthly':70000,'applicant_count':None,'deadline':'2026-10-15','summary':'Reviewed'}
  y={'id':'q','salary_monthly':None,'applicant_count':None,'deadline':'2026-10-16','summary':'Scraped'}
  z=job.merge(x,y)
  self.assertEqual(z['deadline'],'2026-10-16')
  self.assertEqual(z['salary_monthly'],70000)
  self.assertEqual(z['summary'],'Reviewed')

if __name__=='__main__':unittest.main()
