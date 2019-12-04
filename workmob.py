from selenium import webdriver
import unittest
from selenium.common.exceptions import NoSuchElementException
import time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import signal
import psutil
from urllib.request import Request, urlopen
from urllib.error import URLError


url = "https://preprod.workmob.com/"
page_title = "WorkMob - WorkMob is a fun social network that helps you meet, connect and share with people at work."
workmob_logo = "//img[@class='-PRqc']"


class WorkMob(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.PhantomJS(
            service_args=['--ignore-ssl-errors=true', '--ssl-protocol=any', '--local-to-remote-url-access=yes', ],
            executable_path="C:/Users/Sagar/Downloads/phantomjs-2.1.1-windows/bin/phantomjs.exe")
        self.driver.set_window_size(1024, 768)


    def navigate_to_page(self, url):
        self.driver.get(url)
        time.sleep(10)

    # def verify_url_redirection(self, domain):
    #     driver = self.driver
    #     print("VALIDATING URL REDIRECTION TO CHECKOUT ...")
    #     if domain in driver.current_url:
    #         return True
    #     else:
    #         return False

    def verify_page_title(self, title):
        driver = self.driver
        print("VALIDATING PAGE TITLE ...")
        print("page title", driver.title)
        if self.driver.title == title:
            return True
        else:
            return False

    def verify_workmob_logo(self):
        print("VALIDATING WorkMob LOGO ...")
        try:
            self.driver.find_element_by_xpath(workmob_logo)
        except NoSuchElementException:
            return False
        return True


    def verify_httpRequest(self, url):
        print('HTTP REQUESTS ')
        req = Request(url)
        time.sleep(10)
        try:
            response = urlopen(req)
            time.sleep(2)
            print(response)
        except URLError as e:
            if hasattr(e, 'reason'):
                print('We failed to reach a server.')
                print('Reason: ', e.reason)
                print("Sending an email...")
                message = ('Reason: ', e.reason)
                emailto = ["sagar@arcgate.com"]
                config = Config()
                config.send_email(message, emailto, "Urgent - Workmob server Error Notification")

            else:
                print('everything is fine')
                return False


    def kill_phantomJS(self):
        PROCNAME = "phantomjs"
        for proc in psutil.process_iter():
            if proc.name() == PROCNAME:
                proc.kill()

    def quit(self):
        self.driver.close()
        self.driver.service.process.send_signal(signal.SIGTERM)  # kill the specific phantomjs child proc
        self.driver.quit()
        time.sleep(5)
        self.kill_phantomJS()

    def test_checkout_page_load(self):
        self.navigate_to_page(url)
        try:
            if not all([self.verify_page_title(page_title),self.verify_workmob_logo()]):
                print("Sending an email...")
                message = "Workmob Page Validation Script Failed. Unable To Load WorkMob Page OR something has changed on the workmob page.<br><br>Test url - https://preprod.workmob.com/"
                emailto = ["sagar@arcgate.com", "harish@arcgate.com", "deepak@arcgate.com"]
                config = Config()
                config.send_email(message, emailto, "Urgent - Workmob Error Notification")
        except Exception as error:
            print(error)

        #self.verify_httpRequest(url)



class Config(object):

    ENABLED_EMAILS = True
    EMAIL_CONFIG = {
        "SENDER": "sagar dixit",
        "SMTP_HOST": "smtp.gmail.com",
        "SMTP_PORT": 587,
        "SMTP_USERNAME": "sagar.dixit1990@gmail.com",
        "SMTP_PASSWORD": "riskyhbaba@321",
    }

    def send_email(self, message, recipients, subject="WorkMob Notification",
                   attachements=[]):
        """Send an email through SMTP"""
        try:
            mail = (""" From:{}\n""" """ To:{}\n""" """ Subject: {}\n"""
                    """ Email: {}\n""").format(Config.EMAIL_CONFIG["SENDER"],
                                               recipients, subject, message)
            print("Sending email... \n\n{}".format(mail))
            if Config.ENABLED_EMAILS:
                SMTP_HOST = Config.EMAIL_CONFIG["SMTP_HOST"]
                SMTP_PORT = Config.EMAIL_CONFIG["SMTP_PORT"]
                SMTP_USERNAME = Config.EMAIL_CONFIG["SMTP_USERNAME"]
                SMTP_PASSWORD = Config.EMAIL_CONFIG["SMTP_PASSWORD"]

                self.conn = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
                self.conn.ehlo()
                self.conn.starttls()
                self.conn.login(SMTP_USERNAME, SMTP_PASSWORD)
                recipients = [s for s in recipients if s[s.find("@") + 1:]]

                if not recipients:
                    return []
                msg = MIMEMultipart('alternative')
                if subject: subject = subject
                msg['Subject'] = subject
                msg['From'] = Config.EMAIL_CONFIG["SENDER"]
                msg['To'] = ", ".join(recipients)

                part = MIMEText(message, 'html')
                msg.attach(part)
                status = self.conn.noop()[0]
                if status == 250:
                    self.conn.sendmail(Config.EMAIL_CONFIG["SENDER"], recipients,
                                       msg.as_string())
                else:
                    print("Connection to SMTP server failed")
        except Exception as e:
            print("Failed to send an email : {}".format(e), e)
        finally:

            print("quit the connection")


if __name__ == "__main__":
    unittest.main()
