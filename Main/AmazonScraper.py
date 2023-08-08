import time
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import StaleElementReferenceException


# Returns a list of department links
def get_departments(driver):
    departments = []
    driver.get('https://www.amazon.com/Best-Sellers/zgbs')
    wait = WebDriverWait(driver, 20)
    for i in range(1, 43):
        xpath = "//div[@role='tree']//div[{}]//a[1]".format(i)
        department_link = wait.until(ec.presence_of_element_located((By.XPATH, xpath))).get_attribute('href')
        if department_link not in departments:
            departments.append(department_link)

    print("Departments found: " + str(len(departments)))
    print(departments)
    print("")
    return departments


# Returns a list of product ASINS
def get_product_asins(driver, department, product_asins, amount):
    new_asins = []
    wait = WebDriverWait(driver, 5)

    print("Opening " + department)
    # Gets first amount number of elements of available products

    # (ActionChains(driver)
    #  .key_down(Keys.CONTROL)
    #  .click(department)
    #  .key_up(Keys.CONTROL)
    #  .perform())
    driver.get(department)

    for attempt2 in range(2):
        try:
            department_name = (wait.until(ec.presence_of_element_located((By.CLASS_NAME, '_cDEzb_card-title_2sYgw')))
                               .text.replace("Best Sellers in ", ""))

            products = wait.until(ec.presence_of_all_elements_located((
                By.CLASS_NAME, 'p13n-sc-uncoverable-faceout')))[:amount]

            for product in products:
                try:
                    product_asin = product.get_attribute('id')
                except StaleElementReferenceException:
                    product_asin = "Product not found"
                    pass
                print(product_asin)
                if product_asin not in product_asins and product_asin != "Product not found":
                    new_asins.append([department_name, product_asin])
                else:
                    print('Duplicate product!')
            break
        except TimeoutException:
            print("Refreshing!")
            driver.refresh()

    return new_asins


# Appends product links to product_links
def build_keepa_links(product_asins):
    product_links = []
    for asin in product_asins:
        product_links.append([asin[0], "https://keepa.com/#!product/1-" + asin[1]])

    print("Product links available: " + str(len(product_links)))
    return product_links


def compile_product_urls(driver):
    product_asins = []

    departments = get_departments(driver)
    time.sleep(2)
    # base_window = driver.current_window_handle
    for department in departments:
        # driver.switch_to.window(base_window)
        new_asins = get_product_asins(driver, department, product_asins, 11)
        for asin in new_asins:
            product_asins.append(asin)
        print("Products found: " + str(len(product_asins)) + '\n')

    product_links = build_keepa_links(product_asins)
    return product_links
