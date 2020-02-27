from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import phrases as p
import time
from random import randint
import words
import globals as gls
import os
import traceback
import random
import heroku3
import requests

import schedule
with open("dictionary/complements.txt") as compfile:
    global COMPLEMENTS
    COMPLEMENTS = [line.strip() for line in compfile]

with open("dictionary/descs.txt") as descfile:
    global DESCS
    DESCS = [line.strip() for line in descfile]

with open("dictionary/static_phrase_list.txt") as phrasefile:
    global STATIC_PHRASES
    STATIC_PHRASES = [line.strip() for line in phrasefile]


class MastodonBot:
    def __init__(self, user_email, password, bot_name):
        self.user_email = user_email
        self.password = password
        self.bot_name = bot_name
        chrome_options = webdriver.ChromeOptions()
        chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
        chrome_options.add_argument("--disable-dev-sgm-usage")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--start-maximized")
        prefs = {"profile.managed_default_content_settings.images": 2}
        chrome_options.add_experimental_option("prefs", prefs)
        # chrome_options.add_argument("--headless")
        # self.driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), options=chrome_options)
        self.driver = webdriver.Chrome("./chromedriver", options=chrome_options)
        self. base_url = "https://mastodon.social/"
        self.login()

    def restart_application(self):
        heroku_conn = heroku3.from_key('b477d2e0-d1ba-48b1-a2df-88d87db973e7')
        app = heroku_conn.apps()[self.bot_name]
        app.restart()

    @staticmethod
    def response_generator():
        n = p.Sentence()
        gend_sentence = f"This is kinda {random.choice(words.ADJECTIVES)}. {n}. Learn more at: {gls.single_lander_source()}"
        random_comp = COMPLEMENTS[randint(0, len(COMPLEMENTS) - 1)]
        random_phrase = STATIC_PHRASES[randint(0, len(STATIC_PHRASES) - 1)]
        random_desc = DESCS[randint(0, len(DESCS) - 1)]

        response_list = [gend_sentence, random_comp, random_phrase, random_desc]

        return response_list[randint(0, len(response_list) - 1)]

    def login(self):
        print("session id at login: ", self.driver.session_id)

        login_btn_xpath = "//button[contains(.,'Log in')]"

        try:

            self.driver.get(f"{self.base_url}auth/sign_in")

            # fill up the credential fields
            gls.sleep_time()
            self.driver.find_element_by_id('user_email').send_keys(self.user_email)
            gls.sleep_time()
            self.driver.find_element_by_id('user_password').send_keys(self.password)
            gls.sleep_time()
            self.driver.find_element_by_xpath(login_btn_xpath).click()

            print("login success...")
        except Exception as e:
            print("the login issue is: ", e)
            print(traceback.format_exc())
            pass

    def profile_link_extractor(self):
        gls.sleep_time()
        sorted_prof_links_list = []

        prof_link_set = set()

        for _ in range(500):
            random_page_num = randint(5, 30000)
            admin_follower_page_link = f'https://mastodon.social/users/Gargron/followers?page={random_page_num}'

            self.driver.get(admin_follower_page_link)
            gls.sleep_time()
            self.driver.execute_script("window.scrollBy(0,500)", "")
            gls.sleep_time()
            results = self.driver.find_elements_by_xpath('//a[@href]')
            print(f"number of profile links extracted in this iteration: {len(results)}")

            for res in results:
                final_link = res.get_attribute('href')
                prof_link_set.add(final_link)

        for single_link in list(prof_link_set):
            if "mastodon.social/@" in single_link:
                sorted_prof_links_list.append(single_link)

        return sorted_prof_links_list

    def user_follower(self, profile_link):
        follow_unfollow_btn_xpath = '//*[contains(@data-method,"post")]'
        gls.sleep_time()
        self.driver.get(profile_link)
        gls.sleep_time()
        follow_unfollow_element = WebDriverWait(self.driver, 15).until(EC.element_to_be_clickable((By.XPATH, follow_unfollow_btn_xpath)))
        gls.sleep_time()
        follow_unfollow_element.click()
        print("user followed or unfollowed!")



if __name__ == '__main__':

    def mastodon_action_sequence():
        mst_bot = MastodonBot("2ksaber@gmail.com", "AWR3A9C7FL$-4n3", 'mastodon-bot-master')

        # final_profile_link_list = mst_bot.profile_link_extractor()
        #
        # random_prof_link = final_profile_link_list[randint(0, len(final_profile_link_list) - 1)]

        mst_bot.user_follower('https://mastodon.social/@mondomike65')





    mastodon_action_sequence()

    def custom_mastodon_scheduler():
        try:
            schedule.every().day.at("01:30").do(mastodon_action_sequence)

            while True:
                schedule.run_pending()
                time.sleep(1)

        except Exception as e:
            print('custom_mastodon_scheduler Error occurred ' + str(e))
            print(traceback.format_exc())
            pass


    # def test_locally():
    #     mastodon_action_sequence()
    #
    # test_locally()
