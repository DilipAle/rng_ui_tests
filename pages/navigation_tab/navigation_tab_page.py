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

    def go_to_home(self):
        """Click the 'Home' tab in the navigation bar"""
        self.click(self.home_tab)  
    
    def go_to_accounts(self):
        """Click the 'Accounts' tab in the navigation bar"""
        self.click(self.accounts_tab)
    
    def go_to_contacts(self):
        """Click the 'Contacts' tab in the navigation bar"""
        self.click(self.contacts_tab)
    
    def go_to_mypartners(self):
        """Click the 'My Partners' tab in the navigation bar"""
        self.click(self.mypartners_tab)
    
    def go_to_policies(self):
        """Click the 'Policies' tab in the navigation bar"""
        self.click(self.policies_tab)
    
    def go_to_dashboards(self):
        """Click the 'Dashboards' tab in the navigation bar"""
        self.click(self.dashboards_tab)
    
    def go_to_tasks(self):
        """Click the 'Tasks' tab in the navigation bar"""
        self.click(self.tasks_tab)
