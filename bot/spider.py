import requests
from lxml import html
from bs4 import BeautifulSoup
from tpobot.settings import username, password

def crawl():
    session_requests = requests.session()
    login_url = 'https://www.placement.iitbhu.ac.in/accounts/login/'
    result = session_requests.get(login_url)
    tree = html.fromstring(result.text)
    authenticity_token = list(set(tree.xpath("//input[@name='csrfmiddlewaretoken']/@value")))[0]
    payload = {
        "login": username, 
        "password": password, 
        "csrfmiddlewaretoken": authenticity_token
    }

    session_requests.post(
        login_url, 
        data = payload, 
        headers = dict(referer=login_url)
    )
    url = 'https://www.placement.iitbhu.ac.in/company/calendar?page_size=250'
    result = session_requests.get(
        url, 
        headers = dict(referer = url)
    )
    soup = BeautifulSoup(result.text, 'html.parser')
    companies = soup.find_all('div',class_='row company')

    data = {}

    for index, c in enumerate(companies):
        updated_at = c.find('p', class_='updated_at').get_text()
        company_name = c.find('p', class_='company_name').get_text()
        company_profile = c.find('p', class_='company_profile').get_text()
        purpose = c.find('p', class_='purpose').get_text()
        x = c.find('span', class_='x').get_text()
        xii = c.find('span', class_='xii').get_text()
        cgpa = c.find('span', class_='cgpa').findChildren()[0].get_text()
        depts = c.find('p', class_='dept').findChildren()
        department = [dept.get_text() for dept in depts]
        department = " ".join(map(str, department))
        course = c.find('span', class_='course').findChildren()
        course = [x.get_text() for x in course]
        course = " ".join(map(str, course))
        a_backlog = c.find('span', class_='a_backlog').findChildren()[0].get_text()
        t_backlog = c.find('span', class_='t_backlog').findChildren()[0].get_text()
        ppt_date = c.find('p', class_='ppt_date').findChildren()[0].get_text()
        exam_date = c.find('p', class_='exam_date').findChildren()[0].get_text()
        status = c.find('p', class_='status').findChildren()[0].get_text()
        branch_issue_dead = c.find('p', class_='branch_issue_dead').findChildren()[1].get_text()
        willingness_dead = c.find('p', class_='willingness_dead').findChildren()[1].get_text()
        # jd = c.find('p', class_='jd').findChildren()[1]['href']
        #user's won't be able to see jd anonymously, so not storing in db.
        btech_ctc = c.find('table').find('td', text='B.Tech')
        if btech_ctc:
            btech_ctc = btech_ctc.findNext('td').get_text()

        idd_imd_ctc = c.find('table').find('td', text='IDD/IMD')
        if idd_imd_ctc:
            idd_imd_ctc = idd_imd_ctc.findNext('td').get_text()

        data_dict = {
                'company_name': company_name,
                'updated_at' : updated_at,
                'company_profile' : company_profile,
                'purpose' : purpose,
                'x' : x,
                'xii' : xii,
                'cgpa' : cgpa,
                'course' : course,
                'department' : department,
                'a_backlog' : a_backlog,
                't_backlog' : t_backlog,
                'ppt_date' : ppt_date,
                'exam_date' : exam_date,
                'status' : status,
                'branch_issue_dead' : branch_issue_dead,
                'willingness_dead' : willingness_dead,
                'btech_ctc' : btech_ctc,
                'idd_imd_ctc' : idd_imd_ctc,
        }
        data[index] = data_dict

    return data




# print('company_name: ', company_name)
# print('updated_at: ', updated_at)
# print('company_profile: ', company_profile)
# print('purpose: ', purpose)
# print(x)
# print(xii)
# print('cgpa:', cgpa)
# print(course)
# print(department)
# print('backlogs:', a_backlog, t_backlog)
# print('ppt_date: ', ppt_date)
# print('exam_date', exam_date)
# print('status:', status)
# print('branch_issue_dead:', branch_issue_dead)
# print('willingness_dead', willingness_dead)
# print('btech_ctc', btech_ctc)
# print('idd_imd_ctc', idd_imd_ctc)
