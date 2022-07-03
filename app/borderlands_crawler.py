import logging
import time
from fake_useragent import UserAgent, FakeUserAgentError
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, InvalidSelectorException
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from app.util import decrypt
from app.config import get_config, AppConfig


class BorderlandsCrawler(object):
    name = "borderlands_spider"
    start_url = 'https://google.com'
    GEARBOX_URL = 'https://shift.gearboxsoftware.com/home'
    BORDERLANDS_REWARDS_URL = 'https://shift.gearboxsoftware.com/rewards'

    def __init__(self, user: dict, browser: str = 'firefox', config: AppConfig = get_config()):
        self.user = user
        # Gearbox uses codenames for BL titles.
        self.game_codes = {
            'Borderlands: Game of the Year Edition': 'Mopane',
            'Borderlands 2': 'Willow2',
            'Borderlands: The Pre-Sequel': 'Cork',
            'Borderlands 3': 'Oak',
            'Tiny Tina\'s Wonderlands': 'Daffodil'
        }
        self.config = config

        self.options = FirefoxOptions()
        # self.options.add_argument('-headless')

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

    def login_gearbox(self):
        self.driver.get(self.GEARBOX_URL)
        time.sleep(2)

        try:
            user_email = self.user['gearbox_email']
            user_password = decrypt(self.user['gearbox_password'], self.config.ENCRYPTION_KEY.encode()).decode()
        except Exception:  # todo: raise exceptions when accessing user details
            raise Exception('Issue accessing User information.')

        if user_email and user_password:
            try:
                self.input("user_email", user_email)
                self.input("user_password", user_password)
                self.click('/html/body/div[1]/div[2]/div[2]/div[1]/div/div[1]/form/div[7]/input')
                return self.check_logged_in()
            except InvalidSelectorException as exc:
                logging.debug(exc)
                logging.debug('Error logging into Gearbox')
                raise GearboxLoginError('Error logging into Gearbox')
        else:
            raise Exception('User information not set.')

    def check_logged_in(self) -> bool:
        """Checks page source if login was successful"""
        if "Incorrect email or password." in self.driver.page_source:  # failed login
            print(f"User details for {self.user['gearbox_email']} are incorrect.")
            return False

        try:
            sign_out_btn = self.driver.find_element_by_xpath('/html/body/div[2]/nav/div/div[2]/ul[2]/li[2]/a')
            if 'Sign Out' in sign_out_btn.text:
                return True
        except NoSuchElementException:
            return False

        return False

    def input_shift_code(self, code: str):
        time.sleep(1)
        self.driver.get(self.BORDERLANDS_REWARDS_URL)
        time.sleep(3)
        self.input('shift_code_input', code)
        self.click('//*[@id="shift_code_check"]')
        self.check_code_error(code)

        return True

    def redeem_shift_code(self, code: str, game: str, platform: str) -> bool:
        time.sleep(1)
        game_code = self.game_codes[game].lower()
        # Select redeem button for the game on the platform option in from user_game table.
        if not self.click(f'//input[@value="{game_code}"]/following-sibling::input[@class="submit_button redeem_button"'
                          f' and contains(@value,"{platform}")]'):
            raise PlatformOptionNotFoundException(f'Could not redeem code {code} for '
                                                  f'{game} on {platform}')
        self.check_code_error(code)

        return True

    def get_games_to_redeem_for_code(self, code: str):
        """insert the code and return the games that the code can be redeemed for from the page source"""
        self.input_shift_code(code)
        # Website lists 1 or more games the code can be redeemed for, get parent container
        # then list of child elements containing text for relevant game
        try:
            parent_game_elem = self.driver.find_element_by_xpath('//*[@id="code_results"]')
            return [elem.text for elem in parent_game_elem.find_elements_by_tag_name("h2")]
        except NoSuchElementException as e:
            logging.error(e, exc_info=True)

        return None

    def check_code_error(self, code: str) -> None:
        # check button clicked, checks if code is valid, if not raise exception
        if self.driver.find_element_by_xpath('//*[@id="shift_code_instructions"]').is_displayed():
            raise InvalidCodeException(f"SHiFT code: {code} is not a valid SHiFT code")
        if "This SHiFT code has expired" in self.driver.page_source:
            raise CodeExpiredException(f"SHiFT code: {code}, has expired")
        if "Failed to redeem your SHiFT code" in self.driver.page_source:  # unknown why this happens
            raise CodeFailedException(f'Code {code} failed to be redeemed')
        if 'This SHiFT code has already been redeemed' in self.driver.page_source:
            # success, user has already used this code
            raise ShiftCodeAlreadyRedeemedException(f'Code {code} has already been redeemed')
        if 'This code is not available for your account' in self.driver.page_source:
            # valid, but cannot be redeemed for user
            raise CodeNotAvailableException(f'Code {code} is not available for your account')
        if 'Unexpected Error Occurred' in self.driver.page_source:  # probably a gearbox related issue
            raise GearboxUnexpectedError('Gearbox ran into and unexpected error.')
        if 'To continue to redeem SHiFT codes, please launch a SHiFT-enabled title first!' in \
                self.driver.page_source:  # rate limit hit, cannot continue to redeem codes
            raise GearboxShiftError(f'Cannot continue to input shift codes on this account {self.user[1]}')

    def tear_down(self):
        self.driver.quit()

    def screenshot(self):
        self.driver.save_screenshot("screenshot.png")


class PlatformOptionNotFoundException(Exception):
    pass


class CodeFailedException(Exception):
    pass


class InvalidCodeException(Exception):
    pass


class CodeExpiredException(Exception):
    pass


class ShiftCodeAlreadyRedeemedException(Exception):
    pass


class CodeNotAvailableException(Exception):
    pass


class GameNotFoundException(Exception):
    pass


class GearboxShiftError(Exception):
    pass


class GearboxUnexpectedError(Exception):
    pass


class GearboxLoginError(Exception):
    pass
