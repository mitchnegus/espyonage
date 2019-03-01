"""
Bot script for monitoring consulate schedule.
"""
import argparse
import time
import datetime
import getpass
import smtplib
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.support.ui import Select, WebDriverWait # available since 2.4.0
from selenium.webdriver.support import expected_conditions as EC # available since 2.26.0
from selenium.webdriver.firefox.options import Options

# USER DEFINED VALUES
# -------------------
# Set recipients for email notifications
targets = ['negus@berkeley.edu']
# Set the latest possible date that you can have an appointment
latest_date = '3/2/2019'

# Parse command line options
parser = argparse.ArgumentParser()
parser.add_argument('-v','--verbose', help='increase output verbosity',
                    action='store_true')
parser.add_argument('-n','--notify', help='send notifications',
                    action='store_true')
args = parser.parse_args()

def use_headless_firefox():
    """Set the web driver to Firefox; don't open a new Window."""
    # Run the browser headless (without opening any windows)
    options = Options()
    options.headless = True
    # Create a new instance of the Firefox driver
    driver = webdriver.Firefox(options=options)
    return driver

def click_next_button(driver):
    """Identify buttons on the page and click the "Next" button."""
    # "Back" and "Next" buttons have the HTML name 'Command'
    buttons = driver.find_elements_by_name('Command')
    for button in buttons:
        # Click the "Next" button
        if button.get_attribute('value') == 'Next':
            button.click()
            return

def get_earliest_dates():
    """Navigates through the website and returns the earliest set of dates."""
    # Create a new instance of the Firefox driver
    driver = use_headless_firefox()
    # Go to the consulate home page
    driver.get("https://appointment.bmeia.gv.at/?Office=los-angeles")

    # Find the element that allows you to choose your calendar type
    calendar_selector = Select(driver.find_element_by_id('CalendarId'))
    # Select the option for visas
    calendar_selector.select_by_visible_text('Visa and Residence Permits')

    # Find all the buttons and click next
    click_next_button(driver)
    # Click next again (for 1 person)
    click_next_button(driver)
    # Click next again (to confirm info)
    click_next_button(driver)

    # Find all the labels in the table of times
    dates = [date.text for date in driver.find_elements_by_tag_name('th')]
    times = [time.text for time in driver.find_elements_by_tag_name('label')]
    driver.quit()
    return dates, times

def check_date_earlier_than_other_date(fixed_date, test_date):
    """`True` if the first date is earlier than the second, else `False`."""
    fixed_datetime_object = datetime.datetime.strptime(fixed_date, '%m/%d/%Y')
    test_datetime_object = datetime.datetime.strptime(test_date, '%m/%d/%Y')
    return (test_datetime_object < fixed_datetime_object)

def write_logfile(filename, dates, times):
    """Writes a log of the findings."""
    linediv1 = '\n====================\n'
    linediv2 = '\n–––––––––––––––\n'
    with open(filename, 'a') as logfile:
        timestamp = str(datetime.datetime.now()).split('.')[0]
        logfile.write(linediv1 + '\n' + timestamp + '\n')
        logfile.write('\nDates:' + linediv2)
        for date in dates:
            logfile.write(date + '\n')
        logfile.write('\nTimes:' + linediv2)
        for time in times:
            logfile.write(time + '\n')

def clear_logfile(filename):
    """Clears the logfile for a new run."""
    with open(filename, 'w') as logfile:
        logfile.write('')

def login_to_email_server(login, password):
    """Login to GMail."""
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(login, password)
    return server

def send_email_notice(server, username, target):
    """Send an email through my GMail."""
    msg = "\nCheck the consulate's webpage."
    server.sendmail(username + '@gmail.com', target, msg)

def print_if_verbose(msg):
    """Print the message if verbosity is turned on."""
    if args.verbose:
        print(msg)

print_msgs = {'failure': 'Nada. Waiting 5 minutes before checking again.',
                  'success': 'Hit!!!'}

if __name__ == '__main__':
    # Login to email server
    if args.notify:
        email_login = input('Email username: ')
        email_password = getpass.getpass('Email password: ')
        server = login_to_email_server(email_login, email_password)
    # Create a log file
    log_filename = 'appointments.log'
    clear_logfile(log_filename)
    # Set a default time to avoid pinging the server too much
    time_val = 300
    # Begin searching 
    count = 0
    while count < 1e9: # Max value is arbitary, just to avoid an infinite loop
	try:
            dates, times = get_earliest_dates()
            write_logfile(log_filename, dates, times)
            count += 1
            for date in dates:
                date = date.split()[1]
                if check_date_earlier_than_other_date(latest_date, date):
                    # A date was found. Send an email notice and print success.
                    if args.notify:
                        for target in targets:
                            send_email_notice(server, email_login, target)
                    print_if_verbose(print_msgs['success'])
                    # Reduce the checking frequency
                    time_val = time_val*36
                else:
                    print_if_verbose(print_msgs['failure'] + f' (Trial {count})')
        except WebDriverException:
            pass
        # Wait...
        time.sleep(time_val)
