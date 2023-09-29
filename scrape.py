import argparse
import os
import re
import time

import pandas as pd
from playwright.sync_api import Playwright, sync_playwright

parser = argparse.ArgumentParser()
parser.add_argument('--frequency', default=10, type=int, help='Frequency of data collection in seconds')
parser.add_argument('--outfile', default='data.csv', type=str, help='Output file name')

def standardize_to_kw(power_string):
    """
    Standardize the units of the power string to kilowatts.
    """

    match = re.match(r'(\d+\.?\d*)\s*(\w+)', power_string)
    num = float(match.group(1))
    units = match.group(2)
    if units == 'kW':
        return num
    elif units == 'W':
        return num / 1000
    else:
        raise ValueError(f'Unknown units: {units}')



def run(playwright: Playwright, args) -> None:
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://www.solarweb.com/")
    page.get_by_role("button", name="Allow all (incl. US-provider cookies)").click()
    page.get_by_role("button", name="Login").click()
    page.get_by_label("Email").click()
    page.get_by_label("Email").fill(os.environ['FRONIUS_USER_EMAIL'])
    page.get_by_label("Password").click()
    page.get_by_label("Password").fill(os.environ['FRONIUS_PASSWORD'])
    page.get_by_role("button", name="Login").click()
    df = pd.DataFrame(columns=['timestamp', 'pv', 'consumer', 'grid'])
    while True:
        time.sleep(args.frequency)
        loc = page.locator("#pvText")
        pv = loc.text_content()
        loc = page.locator("#consumerText")
        consumer = loc.text_content()
        loc = page.locator("#gridText")
        grid = loc.text_content()
        row_df = pd.DataFrame({'timestamp': [time.time()], 'pv': [standardize_to_kw(pv)], 'consumer': [standardize_to_kw(consumer)], 'grid': [standardize_to_kw(grid)]})
        df = pd.concat([df, row_df])
        row_df['timestamp'] = pd.to_datetime(row_df['timestamp'], unit='s')
        print(row_df)
        df.to_csv(args.outfile, index=False)


if __name__ == '__main__':
    args = parser.parse_args()
    with sync_playwright() as playwright:
        run(playwright, args)