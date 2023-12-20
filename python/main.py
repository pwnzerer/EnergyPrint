from playwright.sync_api import sync_playwright
import os

def run(playwright):
    # Start browser
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context(accept_downloads=True)
    page = context.new_page()

    # Navigate to the login page URL (Replace with the actual URL of the login page)
    page.goto('https://qa.energyprint.com/login')

    # Fill in the login credentials (Replace with actual credentials)
    email = 'developercandidate@energyprint.com'
    password = 'Energy1234'

    page.fill('input[name="user_session_base[email]"]', email)
    page.fill('input[name="user_session_base[password]"]', password)

    # Submit the form
    page.click('input[type="submit"]')

    # Wait for navigation to complete
    page.wait_for_load_state()


    # Select all rows in the table body
    rows = page.query_selector_all('#main-content tbody tr')

    # Extract account numbers and links
    accounts = []
    for row in rows:
        acct_number = row.query_selector('td:nth-child(1)').text_content()
        view_link = row.query_selector('td:nth-child(2) a').get_attribute('href')
        accounts.append((acct_number, view_link))
    print(accounts)

    base_url = "https://qa.energyprint.com"

    for acct_number, view_link in accounts:
        # Use the main page to navigate to the account page
        main_page = context.new_page()
        main_page.goto(f'{base_url}{view_link}')

        # Extract PDF links and their invoice dates
        pdf_links = main_page.query_selector_all('.bill-table tbody tr')
        for link in pdf_links:
            invoice_date = link.query_selector('td:nth-child(1)').text_content().strip().replace('/', '-')
            pdf_url = link.query_selector('a').get_attribute('href')

            # Ensure the URL is absolute
            if not pdf_url.startswith('http'):
                pdf_url = base_url + pdf_url

            file_name = f"file_source_{acct_number}_{invoice_date}.pdf"  # Adjust the file source as needed

            # Use a separate page for downloading the PDF
            download_page = context.new_page()
            response = download_page.request.get(pdf_url)
            pdf_content = response.body()
            with open(file_name, 'wb') as file:
                file.write(pdf_content)

            # Close the download page
            download_page.close()

        # Close the main page
        main_page.close()

    # Close browser
    context.close()
    browser.close()

with sync_playwright() as playwright:
    run(playwright)
