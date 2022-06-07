import logging
import time
from fake_useragent import UserAgent, FakeUserAgentError
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, InvalidSelectorException
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from app.database_controller import decrypt
from config import get_config, AppConfig


class BorderlandsCrawler(object):
    name = "borderlands_spider"
    start_url = 'https://google.com'
    GEARBOX_URL = 'https://shift.gearboxsoftware.com/home'
    BORDERLANDS_REWARDS_URL = 'https://shift.gearboxsoftware.com/rewards'

    def __init__(self, user: tuple, browser: str = 'firefox', config: AppConfig = get_config()):
        self.user = user
        self.config = config

        self.options = FirefoxOptions()
        self.options.add_argument('-headless')

        binary = FirefoxBinary(f'/usr/bin/{browser}')  # firefox for laptop, firefox-esr for pi
        # self.options.add_argument('--proxy-server=%s' % PROXY)

        try:
            ua = UserAgent()
            useragent = ua.random
            self.options.add_argument(f'user-agent={useragent}')
        except FakeUserAgentError:
            pass

        self.driver = webdriver.Firefox(firefox_binary=binary, firefox_options=self.options,
                                        executable_path='/usr/local/share/gecko_driver/geckodriver')
        self.driver.set_window_size(1500, 1000)
        self.driver.get(self.start_url)

    def click(self, xpath: str) -> bool:
        try:
            # find elem using xpath
            next_url = self.driver.find_element_by_xpath(xpath)
            # click the button to go to next page
            next_url.click()
            return True
        except NoSuchElementException as e:
            logging.error(e, exc_info=True)
            return False
        except Exception as e:
            # Just print(e) is cleaner and more likely what you want,
            # but if you insist on printing message specifically whenever possible...
            if hasattr(e, 'message'):
                print(e.message)
            else:
                print(e)

    def input(self, elem_id: str, input_str: str) -> None:
        input_element = self.driver.find_element_by_id(elem_id)
        try:
            # click the button to go to next page
            input_element.send_keys(input_str)
        except Exception as e:
            print(e)

    def login_gearbox(self) -> None:
        self.driver.get(self.GEARBOX_URL)
        time.sleep(1)

        try:
            user_email = self.user[1]
            user_password = decrypt(self.user[2], self.config.KEY.encode()).decode()
        except Exception:  # todo: raise exceptions when accessing user details
            raise Exception('Issue accessing User information.')

        if user_email and user_password:
            try:
                self.input("user_email", user_email)
                self.input("user_password", user_password)
                self.click('/html/body/div[1]/div[2]/div[2]/div[1]/div/div[1]/form/div[7]/input')
            except InvalidSelectorException as exc:
                logging.debug(exc)
                logging.debug('Error logging into Gearbox')
        else:
            raise Exception('User information not set.')

    def input_code_gearbox(self, code: str) -> bool:
        time.sleep(1)
        self.driver.get(self.BORDERLANDS_REWARDS_URL)
        time.sleep(1)

        self.input('shift_code_input', code)
        self.click('//*[@id="shift_code_check"]')

        # check button clicked, checks if code is valid, if not raise exception
        hidden_div = self.driver.find_element_by_xpath('//*[@id="shift_code_instructions"]')
        if hidden_div.is_displayed():
            raise CodeFailedException(f"SHiFT code: {code} is not a valid SHiFT code")

        if "This SHiFT code has expired" in self.driver.page_source:
            raise CodeFailedException(f"SHiFT code: {code}, has expired")

        # Website lists 1 or more games the code can be redeemed for, get parent container
        # then list of child elements containing text for relevant game
        parent_game_elem = self.driver.find_element_by_xpath('//*[@id="code_results"]')
        time.sleep(1)
        child_games_set = set(elem.text for elem in parent_game_elem.find_elements_by_tag_name("h2"))

        self.check_code_error(code)

        # Select game to redeem code for
        if 'Tiny Tina\'s Wonderlands' in child_games_set:
            if not self.click('//*[@class="submit_button redeem_button" and @value="Redeem for Epic"]'):
                raise ConsoleOptionNotFoundException(f'Could not redeem Tiny Tina\'s Wonderlands'
                                                     f' code {code} for Epic Games')
        elif 'Borderlands 3' in child_games_set:
            if not self.click('//*[@class="submit_button redeem_button" and @value="Redeem for Epic"]'):
                if not self.click('//*[@class="submit_button redeem_button" and @value="Redeem for Steam"]'):
                    raise ConsoleOptionNotFoundException(f'Could not redeem Borderlands 3 code'
                                                         f' {code} for Epic Games or Steam')
        elif 'Borderlands: The Pre-Sequel' in child_games_set:
            if not self.click('//*[@class="submit_button redeem_button" and @value="Redeem for Xbox Live"]'):
                raise ConsoleOptionNotFoundException(f'Could not redeem Borderlands: The Pre-Sequel '
                                                     f'code {code} for Xbox')
        elif 'Borderlands 2' in child_games_set:
            if not self.click('//*[@class="submit_button redeem_button" and @value="Redeem for Steam"]'):
                raise ConsoleOptionNotFoundException(f'Could not redeem Borderlands 2 code {code} for Steam')
        elif 'Borderlands: Game of the Year Edition' in child_games_set:
            if not self.click('//*[@class="submit_button redeem_button" and @value="Redeem for Steam"]'):
                raise ConsoleOptionNotFoundException(f'Could not redeem Borderlands 2 code {code} for Steam')
        else:
            raise GameNotFoundException(child_games_set)

        if 'To continue to redeem SHiFT codes, please launch a SHiFT-enabled title first!' in self.driver.page_source:
            raise GearBoxError

        self.check_code_error(code)

        return True

    def check_code_error(self, code: str) -> None:
        if "Failed to redeem your SHiFT code" in self.driver.page_source:
            raise CodeFailedException(f'Code {code} failed to be redeemed')
        if 'This SHiFT code has already been redeemed' in self.driver.page_source:
            raise CodeFailedException(f'Code {code} has already been redeemed')
        if 'This code is not available for your account' in self.driver.page_source:
            raise CodeFailedException(f'Code {code} has not available for your account')

    def tear_down(self):
        self.driver.quit()

    def screenshot(self):
        self.driver.save_screenshot("screenshot.png")


class ConsoleOptionNotFoundException(Exception):
    pass


class CodeFailedException(Exception):
    pass


class GameNotFoundException(Exception):
    pass


class GearBoxError(Exception):
    pass
