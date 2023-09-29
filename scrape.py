import os
import time

from playwright.sync_api import Playwright, sync_playwright


def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://www.solarweb.com/")
    page.get_by_role("button", name="Allow all (incl. US-provider cookies)").click()
    page.get_by_role("button", name="Login").click()
    page.get_by_label("Email").click()
    page.get_by_label("Email").fill(os.environ['fonius_user_email'])
    page.get_by_label("Password").click()
    page.get_by_label("Password").fill(os.environ['fronius_password'])
    page.get_by_role("button", name="Login").click()
    for _ in range(10):
        time.sleep(10)
        loc = page.locator("#pvText")
        print(loc.text_content())
        loc = page.locator("#consumerText")
        print(loc.text_content())
        print('---')

    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)
