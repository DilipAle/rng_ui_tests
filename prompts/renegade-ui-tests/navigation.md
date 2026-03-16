<!-- File: renegade-ui-tests/tests/ui/navigation_tab/test_navigation_tab.py -->

# Renegade : Navigation Tabs

## Before Each Test
- User is already logged in (`login` fixture — pre-authenticated page)
- Viewport is 1920x1080 (set by `setup_browser` fixture — Salesforce requires this for nav tabs to be visible)
- A fresh `NavigationTabPage` instance is created for each test

---

## 1. Navigation Bar (smoke)

Each test below is independent — no shared state between tabs.

### 1.1 Can navigate to the Home tab
- Click `a[title="Home"]`
- Wait for page to load
- Current URL contains `"lightning"`

### 1.2 Can navigate to the Accounts tab
- Click `a[title="Accounts"]`
- Wait for page to load
- Current URL contains `"Account"` OR `"one.app"` OR `"New_Business_Flow"`

### 1.3 Can navigate to the Contacts tab
- Click `a[title="Contacts"]`
- Wait for page to load
- Current URL contains `"Contact"` OR `"lightning"`

### 1.4 Can navigate to the My Partners tab
- Click `a[title="My Partners"]`
- Wait for page to load
- Current URL contains `"lightning"`

### 1.5 Can navigate to the Policies tab
- Click `a[title="Policies"]`
- Wait for page to load
- Current URL contains `"lightning"`

### 1.6 Can navigate to the Dashboards tab
- Click `a[title="Dashboards"]` with `force=True` (Salesforce Lightning overlays can block standard clicks)
- Wait for page to load
- Current URL contains `"Dashboard"` OR `"lightning"`

### 1.7 Can navigate to the Tasks tab
- Click `a[title="Tasks"]` with `force=True`
- Wait for page to load
- Current URL contains `"Task"` OR `"lightning"`
