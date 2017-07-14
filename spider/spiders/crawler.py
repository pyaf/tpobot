import scrapy
import time
from urllib.request import urlopen
from bs4 import BeautifulSoup
import sys, os, django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tpobot.settings")
django.setup()
from bot.models import Company
from tpobot.settings import username, password 

class LoginSpider(scrapy.Spider):
    name = 'tpo'
    start_urls = ['https://www.placement.iitbhu.ac.in/accounts/login/']

    def parse(self, response):

        return scrapy.FormRequest.from_response(
            response,
            formdata={'login': username, 'password': password},
            callback=self.after_login
        )

    def after_login(self, response):
        # check login succeed before going on
        if str.encode("Invalid username or password combination") in response.body:
            self.logger.error("Login failed")
            print("\nIncorrect credentials\n")
            return
        else: #Logged in Whoohooo
            print("\n\n LOGGED IN, BC!!! \n")
            url = 'https://www.placement.iitbhu.ac.in/company/calendar?page_size=500'
            return scrapy.Request(url=url, callback=self.company_visit_page)

    def company_visit_page(self, response):
        print("Scraping company visit page\n\n")
        soup = BeautifulSoup(response.text, 'html.parser')
        companies = soup.find_all('div',class_='row company')
        for c in companies:
            updated_at = c.find('p', class_='updated_at').get_text()
            company_name = c.find('p', class_='company_name').get_text()
            company_profile = c.find('p', class_='company_profile').get_text()
            purpose = c.find('p', class_='purpose').get_text()
            x = c.find('span', class_='x').get_text()
            xii = c.find('span', class_='xii').get_text()
            depts = c.find('p', class_='dept').findChildren()
            departments = [dept.get_text() for dept in depts]
            cgpa = c.find('span', class_='cgpa').findChildren()[0].get_text()
            course = c.find('span', class_='course').findChildren()
            course = [x.get_text() for x in course]
            a_backlog = c.find('span', class_='a_backlog').findChildren()[0].get_text()
            t_backlog = c.find('span', class_='t_backlog').findChildren()[0].get_text()
            ppt_date = c.find('p', class_='ppt_date').findChildren()[0].get_text()
            exam_date = c.find('p', class_='exam_date').findChildren()[0].get_text()
            status = c.find('p', class_='status').findChildren()[0].get_text()
            branch_issue_dead = c.find('p', class_='branch_issue_dead').findChildren()[1].get_text()
            willingness_dead = c.find('p', class_='willingness_dead').findChildren()[1].get_text()

            btech_ctc = c.find('table').find('td', text='B.Tech')
            if btech_ctc:
                btech_ctc = btech_ctc.findNext('td').get_text()

            idd_imd_ctc = c.find('table').find('td', text='IDD/IMD')
            if idd_imd_ctc:
                idd_imd_ctc = idd_imd_ctc.findNext('td').get_text()

            company, created = Company.objects.get_or_create(company_name=company_name)
            print("\nAha,..", company_name)
            if created or updated_at != company.updated_at:
                print('\n Gotta update this')
                print('created: ',created, "; update ", updated_at!=company.updated_at)
                company.updated_at = updated_at
                company.company_profile = company_profile
                company.purpose = purpose
                company.x = x
                company.xii = xii
                company.cgpa = cgpa
                company.course = course
                company.departments = departments
                company.a_backlog = a_backlog
                company.t_backlog = t_backlog
                company.ppt_date = ppt_date
                company.exam_date = exam_date
                company.status = status
                company.branch_issue_dead = branch_issue_dead
                company.willingness_dead = willingness_dead
                company.btech_ctc = btech_ctc
                company.idd_imd_ctc = idd_imd_ctc
                company.save()
                print("Done")

            # print('company_name: ', company_name)
            # print('updated_at: ', updated_at)
            # print('company_profile: ', company_profile)
            # print('purpose: ', purpose)
            # print(x)
            # print(xii)
            # print('cgpa:', cgpa)
            # print(course)
            # print(departments)
            # print('backlogs:', a_backlog, t_backlog)
            # print('ppt_date: ', ppt_date)
            # print('exam_date', exam_date)
            # print('status:', status)
            # print('branch_issue_dead:', branch_issue_dead)
            # print('willingness_dead', willingness_dead)
            # print('btech_ctc', btech_ctc)
            # print('idd_imd_ctc', idd_imd_ctc)
