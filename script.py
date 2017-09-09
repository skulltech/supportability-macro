from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


driver = webdriver.Firefox()
BASEURL = 'https://{username}:{password}@myhomelivingcare.supportability.com.au/userMenu.php'
httpuser = input('Enter the HTTP Basic Auth username > ')
httppass = input('Enter the HTTP Basic Auth password > ')
username = input('Enter your login username > ')
password = input('Enter your login password > ')
datefrom = input('Enter the fromDate (format: YYYYMMDD) > ')
dateto   = input('Enter the toDate (format: YYYYMMDD) > ')
URL = BASEURL.format(username=httpuser, password=httppass)

driver.get(URL)

'''
Logging in to the admin panel.
'''
driver.find_element_by_id('username').send_keys(username)
pwfield = driver.find_element_by_id('password')
pwfield.send_keys(password)
pwfield.submit()

wait = WebDriverWait(driver, 10)
element = wait.until(EC.title_is('SupportAbility - Activity Schedule Report: '))

'''
Generating report.
'''
driver.get('https://myhomelivingcare.supportability.com.au/system/inc/custom/reports/activityScheduleReport.php')
fromDate = driver.find_element_by_id("fromDate")
toDate = driver.find_element_by_id("toDate")
driver.execute_script("arguments[0].value = '{}000000';".format(datefrom), fromDate)
driver.execute_script("arguments[0].value = '{}000000';".format(dateto), toDate)
driver.find_element_by_xpath("//select[@name='signedOffStatus']/option[@value='not signed off']").click()
driver.find_element_by_id('activityScheduleReportSearchButton').click()

'''
Get IDs
'''
rows = driver.find_elements_by_css_selector('tr.inlineListRow')[:-1]
print('Number of Activities found: {}'.format(len(rows)))
ids = []
for row in rows:
	id = row.find_element_by_css_selector('td:nth-child(1)').text[-5:]
	ids.append(id)


'''
Check and SignOff Activity
'''
activitypage = 'https://myhomelivingcare.supportability.com.au/activityEdit.php?id='

for id in ids:
	url = activitypage + id
	driver.get(url)

	zeroprivatekms = driver.find_element_by_css_selector('input.privateKilometresTravelled').get_attribute('value') == '0.00'
	try:
		driver.find_element_by_css_selector('a.staffTimesheetRemoveSignoffButton')
	except NoSuchElementException:
		signedoff = False
	else:
		signedoff = True
	try:
		driver.find_element_by_css_selector('a[href^="journalEdit.php?id"]')
	except NoSuchElementException:
		hasjournal = False
	else:
		hasjournal = True

	if zeroprivatekms and signedoff and hasjournal:
		print('ID: ' + id  + ' meets all criteria. Signing Off.')
		
		try:
			driver.find_element_by_css_selector('a.activitySignoffButton').click()
			driver.find_element_by_id('confirmModalSuccessButton').click()
			driver.find_element_by_css_selector('btn.btn-danger.activityRemoveSignoffButton').click()
		except NoSuchElementException:
			pass
		
	else:
		print('ID: ' + id + ' does not meet all criteria')