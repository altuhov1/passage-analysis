import time
from selenium.webdriver.common.by import By
from selenium import webdriver
import pandas as pd


def request(url: str):
    """
    A function that returns a table with applicants' data
    """
    driver = webdriver.Chrome()

    driver.get(url)
    time.sleep(10)

    driver.find_element(by=By.ID, value='original').click()

    driver.find_element(by=By.ID, value='priority').click()

    # print('Ъ')
    el = driver.find_element(By.CLASS_NAME, value='table-bordered')
    el.get_attribute('innerHTML')
    data = []
    for row in el.find_elements(By.TAG_NAME, 'tr'):
        info = [cell.text for cell in row.find_elements(By.TAG_NAME, 'td')]
        if len(info) == 0 or info[0] == '':
            continue
        data.append(info)
    df = pd.DataFrame(data,
                      columns=['№', 'СНИЛС или код', 'Приоритет №', 'Условия зачисления', 'Конкурсный балл', '∑ балл',
                               'мат', 'инф', 'рус', 'ИД', 'ПП', 'Оригинал', 'ВП по оригиналам'])
    return df
