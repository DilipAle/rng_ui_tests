from pages.base.base_page import BasePage

class AccountPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        
        # Define selectors inside __init__ so they are instance variables
        self.individual_suspect_prospect = 'input[type="radio"][id="012Hn0000017TW2IAM"]'
        self.individual_customer = 'input[type="radio"][id="012Hn0000017TVyIAM"]'
        self.business_suspect_prospect = 'input[type="radio"][id="012Hn0000017TW3IAM"]'
        self.business_customer = 'input[type="radio"][id="012Hn0000017TVxIAM"]'
        self.employee = 'input[type="radio"][id="z012Hn0000017TW0IAM"]'
        self.referral_partner = 'input[type="radio"][id="012Hn000000ZBDlIAO"]'
        self.carrier_brokerbilling = 'input[type="radio"][id="012Hn0000017TVzIAM"]'
        self.vendor_subproducer = 'input[type="radio"][id="012Hn0000017TW1IAM"]'
        self.new_button = 'button:has-text("New")'  # add this if not defined in base

    def click_new_button(self):
        """Clicks on the New button on the Account page"""
        self.click(self.new_button)

    def select_individual_suspect_prospect(self):
        self.click(self.individual_suspect_prospect)

    def select_individual_customer(self):
        self.click(self.individual_customer)

    def select_business_suspect_prospect(self):
        self.click(self.business_suspect_prospect)

    def select_business_customer(self):
        self.click(self.business_customer)

    def select_employee(self):
        self.click(self.employee)

    def select_referral_partner(self):
        self.click(self.referral_partner)

    def select_carrier_broker_billing(self):
        self.click(self.carrier_brokerbilling)

    def select_vendor_sub_producer(self):
        self.click(self.vendor_subproducer)