
from pages.base.base_page import BasePage

class AccountCreationPage(BasePage): 
     # Define selector for the Accounts Page
    def __init__(self, page):
        super().__init__(page)
     
        # Account creation field selection
        self.accountname_input = 'input[name="Name"]'
        self.phone_input = 'input[name="Phone"]'
        self.email_input = 'input[name="VRNA__Email__c"]'
        self.email_input = 'input[name="VRNA__First_Name__c"]'
        self.email_input = 'input[name="VRNA__Last_Name__c"]'
        self.email_input = 'input[name="VRNA__Middle_Name__c"]'
        self.referral_source = 'button[aria-label="Referral Source"]'
        # self.referral_source_type_other = '//lightning-base-combobox-item[@data-value='Others']//span[@title='Other']'









