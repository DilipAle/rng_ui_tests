from pages.base.base_page import BasePage

class NavigationTabPage(BasePage):
    # Define selector for the Navigation tab bar items
    home_tab = 'a[title="Home"]'
    accounts_tab = 'a[title="Accounts"]'
    contacts_tab = 'a[title="Contacts"]'
    mypartners_tab = 'a[title="My Partners"]'
    policies_tab = 'a[title="Policies"]'
    dashboards_tab = 'a[title="Dashboards"]'
    tasks_tab = 'a[title="Tasks"]'

    def get_current_url(self):
        """Returns the current page URL"""
        return self.page.url

    def go_to_home(self):
        """Click the 'Home' tab and wait for page to load"""
        self.click(self.home_tab)
        self.page.wait_for_load_state("load")

    def go_to_accounts(self):
        """Click the 'Accounts' tab and wait for page to load"""
        self.click(self.accounts_tab)
        self.page.wait_for_load_state("load")

    def go_to_contacts(self):
        """Click the 'Contacts' tab and wait for page to load"""
        self.click(self.contacts_tab)
        self.page.wait_for_load_state("load")

    def go_to_mypartners(self):
        """Click the 'My Partners' tab and wait for page to load"""
        self.click(self.mypartners_tab)
        self.page.wait_for_load_state("load")

    def go_to_policies(self):
        """Click the 'Policies' tab and wait for page to load"""
        self.click(self.policies_tab)
        self.page.wait_for_load_state("load")

    def go_to_dashboards(self):
        """Click the 'Dashboards' tab and wait for page to load"""
        self.page.locator(self.dashboards_tab).click(force=True)
        self.page.wait_for_load_state("load")

    def go_to_tasks(self):
        """Click the 'Tasks' tab and wait for page to load"""
        self.page.locator(self.tasks_tab).click(force=True)
        self.page.wait_for_load_state("load")
