from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
import datetime as dt
import pandas as pd
import time

year = 2023
previous_date = dt.datetime.today()


def parse_date(s_date):
    global year
    global previous_date
    date_split = s_date.split(' ')
    day_of_week = date_split[0]
    month = date_split[1]
    day = date_split[2]
    time = date_split[3]
    if len(day) < 2:
        day = '0' + day
    if len(time) < 5:
        time = '0' + time

    s_date = day_of_week + ' ' + month + ' ' + day + ', ' + str(year) + ' ' + time
    date = dt.datetime.strptime(s_date, '%a, %b %d, %Y %H:%M')
    if date > previous_date:
        year -= 1
        s_date = day_of_week + ' ' + month + ' ' + day + ', ' + str(year) + ' ' + time
        date = dt.datetime.strptime(s_date, '%a, %b %d, %Y %H:%M')

    previous_date = date
    return date


def click_useless_lines(driver):
    amazon = driver.find_element(By.CSS_SELECTOR, 'td[data-type="0"]')
    amazon.click()
    used = driver.find_element(By.CSS_SELECTOR, 'td[data-type="2"]')
    used.click()
    buy_box = driver.find_element(By.CSS_SELECTOR, 'td[data-type="18"]')
    buy_box.click()
    warehouse = driver.find_element(By.CSS_SELECTOR, 'td[data-type="9"]')
    warehouse.click()


def click_all_range(driver):
    graph_range = driver.find_elements(By.CSS_SELECTOR, '.legendRange')[-1]
    graph_range.click()


def parse_product_name(wait):
    unmodified_name = (wait.until(ec.presence_of_element_located((By.CLASS_NAME, 'productTableDescriptionTitle'))).text
                       .replace("  ", " ||| ").replace(" ", " ||| "))
    name_parts = unmodified_name.split(' ||| ', 2)
    name = name_parts[0]
    print(name)
    rating = float(name_parts[1])
    s_reviews = ''
    for char in name_parts[2]:
        if char.isdigit():
            s_reviews += str(char)
    reviews = int(s_reviews)
    return name, rating, reviews


def get_single_product_data(driver, link):
    # TEMPORARY DATA STORAGE
    data = [[], [], [], [], [], [], [], []]
    data_points_collected = 0

    # Open KEEPA page
    driver.get(link)
    wait = WebDriverWait(driver, 10)
    action = webdriver.ActionChains(driver)

    # Graph info
    time.sleep(2)
    graph = wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, 'canvas.flot-overlay')))
    name, rating, reviews = parse_product_name(wait)

    # Set range to YEAR or ALL
    click_all_range(driver)

    # Move to right most part of graph
    width = graph.size['width']
    action.move_to_element_with_offset(graph, width / 2 - 6, 0).perform()
    # TESTER
    # action.move_to_element_with_offset(graph, -500, 0).perform()

    wait = WebDriverWait(driver, 10)
    # Set pace of cursor movement
    pace = -1
    while True:
        # Get the date
        s_date = wait.until(ec.presence_of_element_located((By.ID, 'flotTipDate'))).text

        # Split the date | Make day of month have 2 digits | Add year
        if s_date:
            date = parse_date(s_date)
            s_date = dt.datetime.strftime(date, '%a, %b %d, %Y %H:%M')
        else:
            break

        # Get the price
        try:
            s_new_price = driver.find_element(By.ID, 'flotTip1').text
            new_price = float(s_new_price.split('$ ')[1]) if '$' in s_new_price else None
        except NoSuchElementException:
            new_price = None

        try:
            s_amazon_price = driver.find_element(By.ID, 'flotTip0').text
            amazon_price = float(s_amazon_price.split('$ ')[1]) if '$' in s_amazon_price else None
        except NoSuchElementException:
            amazon_price = None

        try:
            s_used_price = driver.find_element(By.ID, 'flotTip2').text
            used_price = float(s_used_price.split('$ ')[1]) if '$' in s_used_price else None
        except NoSuchElementException:
            used_price = None

        # Add name, date, price to list
        if date in data[1]:
            pass
        else:
            data[0].append(name)
            data[1].append(rating)
            data[2].append(reviews)
            data[3].append(link)
            data[4].append(date)
            data[5].append(new_price)
            data[6].append(amazon_price)
            data[7].append(used_price)
            print(s_date + ' | ' + str(new_price) + " | " + str(amazon_price) + " | " + str(used_price))
            data_points_collected += 1

        # Move cursor left
        action.move_by_offset(pace, 0).perform()

    print(data_points_collected)
    return data


def convert_to_df(department, data):
    df = pd.DataFrame({"Product Name": data[0],
                       "Rating": data[1],
                       "# of Reviews": data[2],
                       "Department": department,
                       "Link": data[3],
                       "Date": data[4],
                       "$ New": data[5],
                       "$ Amazon": data[6],
                       "$ Used": data[7]})
    return df


def get_single_product_data_df(driver, link, department):
    global year
    global previous_date
    year = 2023
    previous_date = dt.datetime.today()
    data = get_single_product_data(driver, link)
    df = convert_to_df(department, data)
    return df
