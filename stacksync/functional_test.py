import unittest
from selenium import webdriver
import uuid
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class StacksyncWebTests(unittest.TestCase):
    """
    You must have a django server running to run this test
    manage runserver 8000 (just run your regular django dev server and then run the tests)

    IMPORTANT THIS TEST USES THE FOLLOWING USERS.
    al@al.com
    john.doe@yahoo.com
    walter.smith@stacksync.com
    """
    def setUp(self):
        self.password = "testpass"
        self.browser = webdriver.Firefox()
        self.base_url = "http://127.0.0.1:8000"
        self.username = "john.doe@yahoo.com"
        self.browser.implicitly_wait(5)
        self.login_stacksync(self.username, self.password)

    def tearDown(self):
        self.browser.quit()

    def test_stacksync_webapp_starts(self):
        self.browser.get('http://localhost:8000')
        self.assertEquals('StackSync', self.browser.title)

    def login_stacksync(self, login_username, password):
        self.browser.get(self.base_url + "/log_in/")
        self.browser.find_element_by_id("id_username").clear()
        self.browser.find_element_by_id("id_username").send_keys(login_username)
        self.browser.find_element_by_id("id_password").clear()
        self.browser.find_element_by_id("id_password").send_keys(password)
        self.browser.find_element_by_xpath("//button[@type='submit']").click()

    def test_login(self):
        self.assertEquals('Proyecto - Bienvenido', self.browser.title)

    def create_folder(self):
        self.browser.find_element_by_id("folder").click()
        prompt = self.browser.switch_to.alert
        name_of_folder = str(uuid.uuid4())
        prompt.send_keys(name_of_folder)
        prompt.accept()
        return name_of_folder

    def test_create_a_new_folder(self):
        """
        You name a folder like this: 'yy'
        The result in HTML turns out to be: 'Yy'
        """
        name_of_folder = self.create_folder()
        table = self.browser.find_element_by_id('myTable')
        rows = table.find_elements_by_tag_name('tr')
        self.assertTrue(
            any(name_of_folder.lower() in row.text.lower() for row in rows)
        )

    def find_folder(self, name_of_folder):
        """
        Returns the td element of a row, if a returned the whole tr, contextmenu wouldnt show up

        :param name_of_folder:
        :return WebElement:
        """
        table = self.browser.find_element_by_id('myTable')
        columns = table.find_elements_by_tag_name('td')
        return [column for column in columns if name_of_folder.lower() in column.text.lower()]


    def open_folder_context_menu(self):
        element_to_right_click_working = self.find_folder('aa')[0]
        self.show_context_menu(element_to_right_click_working)

    def get_folder_members(self, folder_td_element):
        self.show_context_menu(folder_td_element)
        menu_share_option = self.browser.find_element_by_css_selector('#jqContextMenu > ul > li#share').click()
        folder_members = self.browser.find_elements_by_css_selector('#folder-members option')
        return folder_members

    def test_get_folder_members(self):
        name_of_folder = self.create_folder()
        folder_td_element = self.find_folder(name_of_folder)[0]
        folder_members = self.get_folder_members(folder_td_element)

        self.assertEquals(0, len(folder_members))


    def show_context_menu(self, element_to_right_click):
        actions = ActionChains(self.browser)
        actions.move_to_element(element_to_right_click)
        actions.context_click(element_to_right_click)
        actions.perform()

    def input_members_email_in_folder(self, email):
        input_text = self.browser.find_element_by_css_selector("#folder-members + div > input")
        input_text.send_keys(email)
        input_text.send_keys(Keys.RETURN)

    def test_share_a_folder(self):
        users = ['al@al.com', 'walter.smith@stacksync.com']
        name_of_folder = self.create_folder()
        folder_td_element = self.find_folder(name_of_folder)[0]

        self.show_context_menu(folder_td_element)

        menu_share_option = self.browser.find_element_by_css_selector('#jqContextMenu > ul > li#share')
        menu_share_option.click()
        folder_members=self.browser.find_elements_by_css_selector('#folder-members option')

        for user in users:
            self.input_members_email_in_folder(user)

        # Saves current members
        self.browser.find_element_by_id('save-member-button').click()

        # Closes modal window
        close_button = '#share-folder-modal > div.modal-dialog > div.modal-content > div.modal-footer > button'
        self.browser.find_element_by_css_selector(close_button).click()

        folder_members = self.get_folder_members(folder_td_element)
        self.assertEquals(3, len(folder_members))

        self.browser.find_element_by_css_selector(close_button).click()



