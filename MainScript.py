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
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument('window-size=2560,1440')
        chrome_options.add_argument("--headless")
        self.driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), options=chrome_options)
        # self.driver = webdriver.Chrome("./chromedriver", options=chrome_options)
        self. base_url = "https://mastodon.social/"
        self.login()

    def restart_application(self):
        heroku_conn = heroku3.from_key('b477d2e0-d1ba-48b1-a2df-88d87db973e7')
        app = heroku_conn.apps()[self.bot_name]
        app.restart()

    @staticmethod
    def response_generator():
        n = p.Sentence()
        gend_sentence = f"This is sorta {random.choice(words.ADJECTIVES)}. {n}. Learn more at: {gls.single_lander_source()}"
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
            gls.sleep_time()
            self.driver.maximize_window()
            gls.sleep_time()

            print(f' current window size: {self.driver.get_window_size()}')
        except Exception as e:
            print("the login issue is: ", e)
            print(traceback.format_exc())
            pass

    def profile_link_extractor(self):
        print("session id at profile_link_extractor: ", self.driver.session_id)

        gls.sleep_time()
        sorted_prof_links_list = []

        prof_link_set = set()

        for _ in range(23):
            random_page_num = randint(5, 30000)
            admin_follower_page_link = f'https://mastodon.social/users/Gargron/followers?page={random_page_num}'
            results = []
            try:
                self.driver.get(admin_follower_page_link)
                gls.sleep_time()
                self.driver.execute_script("window.scrollBy(0,500)", "")
                gls.sleep_time()
                results = self.driver.find_elements_by_xpath('//a[@href]')
                print(f"number of profile links extracted in this iteration: {len(results)}")

            except Exception as em:
                print('profile_link_extractor Error occurred ' + str(em))
                print(traceback.format_exc())

            finally:
                print("profile_link_extractor() done")

            for res in results:
                final_link = res.get_attribute('href')
                prof_link_set.add(final_link)

        for single_link in list(prof_link_set):
            if "mastodon.social/@" in single_link:
                sorted_prof_links_list.append(single_link)

        return sorted_prof_links_list

    def user_follower(self, profile_link):
        print("session id at user_follower: ", self.driver.session_id)

        try:
            follow_unfollow_btn_xpath = '//*[contains(@data-method,"post")]'
            gls.sleep_time()
            self.driver.get(profile_link)
            gls.sleep_time()
            follow_unfollow_element = WebDriverWait(self.driver, 15).until(EC.element_to_be_clickable((By.XPATH, follow_unfollow_btn_xpath)))
            gls.sleep_time()
            follow_unfollow_element.click()
            print("user followed or unfollowed!")

        except Exception as em:
            print('user_follower Error occurred ' + str(em))
            print(traceback.format_exc())

        finally:
            print("user_follower() done")

    def send_toots(self, homepage, user_handle, single_comment):
        print(f' current window size at send toots: {self.driver.get_window_size()}')

        print("session id at send_toots: ", self.driver.session_id)

        toot_text_xpath = '//*[contains(@placeholder,"on your mind?")]'
        toot_btn_xpath = "//button[contains(.,'Toot!')]"

        formatted_toot = f'hi @{user_handle} {single_comment}'
        print(formatted_toot)
        try:
            self.driver.execute_script("window.scrollBy(0,500)", "")
            gls.sleep_time()
            self.driver.get(homepage)
            gls.sleep_time()
            self.driver.find_element_by_xpath(toot_text_xpath).send_keys(formatted_toot)
            gls.sleep_time()
            self.driver.find_element_by_xpath(toot_btn_xpath).click()

            print("toot sent")

        except Exception as em:
            print('send_toots Error occurred ' + str(em))
            print(traceback.format_exc())

        finally:
            print("send_toots() done")

    def status_id_extractor(self):
        print("session id at status_id_extractor: ", self.driver.session_id)

        gls.sleep_time()
        local_timeline_url = f"{self.base_url}web/timelines/public/local"
        status_ids_set = set()

        self.driver.execute_script("window.scrollBy(0,1000)", "")

        try:
            self.driver.get(local_timeline_url)
            gls.sleep_time()

            elements = self.driver.find_elements_by_tag_name('article')
            gls.sleep_time()

            for e in elements:
                status_ids_set.add(e.get_attribute('data-id'))

            gls.sleep_time()

        except Exception as em:
            print('status_id_extractor Error occurred ' + str(em))
            print(traceback.format_exc())

        finally:
            print("status_id_extractor() done")

        return list(status_ids_set)

    def replier_booster_faver(self, status_id_list, reply):
        print(f' current window size at replier_booster_faver : {self.driver.get_window_size()}')

        print("session id at replier_booster_faver: ", self.driver.session_id)

        boost_btn_xpath = '//*[contains(@aria-label,"Boost")]'
        fav_btn_xpath = '//*[contains(@aria-label,"Favourite")]'
        bmk_btn_xpath = '//*[contains(@aria-label,"Bookmark")]'
        reply_btn_xpath = '//*[contains(@aria-label,"Reply")]'
        toot_text_xpath = '//*[contains(@placeholder,"on your mind?")]'
        toot_btn_xpath = "//button[contains(.,'Toot!')]"

        try:
            for _ in range(12):
                random_status_id = status_id_list[randint(0, len(status_id_list) - 1)]
                status_link = f'https://mastodon.social/web/statuses/{random_status_id}'
                self.driver.get(status_link)
                gls.sleep_time()
                reply_btn = self.driver.find_element_by_xpath(reply_btn_xpath)
                gls.sleep_time()
                reply_btn.click()

                formatted_toot = f'yo {reply}'
                print(formatted_toot)
                gls.sleep_time()
                self.driver.find_element_by_xpath(toot_text_xpath).send_keys(formatted_toot)
                gls.sleep_time()
                self.driver.find_element_by_xpath(toot_btn_xpath).click()

                print("reply to status sent")

        except Exception as em:
            print('replier Error occurred ' + str(em))
            print(traceback.format_exc())

        try:
            gls.sleep_time()
            reply_btn = self.driver.find_element_by_xpath(boost_btn_xpath)
            gls.sleep_time()
            reply_btn.click()
            print("reply boosted!")

        except Exception as em:
            print('boost Error occurred ' + str(em))
            print(traceback.format_exc())

        try:
            gls.sleep_time()
            reply_btn = self.driver.find_element_by_xpath(fav_btn_xpath)
            gls.sleep_time()
            reply_btn.click()
            print("reply favd!")

        except Exception as em:
            print('fav Error occurred ' + str(em))
            print(traceback.format_exc())

        try:
            gls.sleep_time()
            reply_btn = self.driver.find_element_by_xpath(bmk_btn_xpath)
            gls.sleep_time()
            reply_btn.click()
            print("reply bookmarked!")

        except Exception as em:
            print('bookmark Error occurred ' + str(em))
            print(traceback.format_exc())


if __name__ == '__main__':

    def mastodon_action_sequence():
        mst_bot = MastodonBot("2ksaber@gmail.com", "AWR3A9C7FL$-4n3", 'mastodon-bot-master')
        while 1:
            final_profile_link_list = mst_bot.profile_link_extractor()

            for i in range(100):
                print(f'loop number {i}')
                random_prof_link = final_profile_link_list[randint(0, len(final_profile_link_list) - 1)]

                mst_bot.user_follower(random_prof_link)

                mst_bot.send_toots("https://mastodon.social/web/timelines/home",  random_prof_link.split('@')[1], mst_bot.response_generator())

                mst_bot.replier_booster_faver(mst_bot.status_id_extractor(), mst_bot.response_generator())

            t = randint(12000, 15000)
            print(f'sleeping for {t} seconds')
            time.sleep(t)

            mst_bot.restart_application()


    mastodon_action_sequence()
