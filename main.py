import pandas as pd
import time
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def split_students_into_programs(df: pd.DataFrame):
    pass


def request_students_by_url(program_url: str):
    """
    A function that returns a table with applicants' data
    """

    # open browser
    driver = webdriver.Chrome()
    driver.get(program_url)

    # click checkboxes
    WebDriverWait(driver, 360).until(
        EC.element_to_be_clickable((By.ID, 'original')))
    driver.find_element(by=By.ID, value='original').click()

    WebDriverWait(driver, 360).until(
        EC.element_to_be_clickable((By.ID, 'priority')))
    driver.find_element(by=By.ID, value='priority').click()

    # get user data
    table = driver.find_element(By.CLASS_NAME, value='table-bordered')
    table.get_attribute('innerHTML')
    data = []
    for row in table.find_elements(By.TAG_NAME, 'tr'):
        info = row.text.split(" ")
        if len(info) < 6:
            continue

        data.append({
            "student_id": info[1] + " " + info[2],
            "priority": info[3],
            "conditions": info[4],
            "score": info[5],
        })

    driver.quit()
    df = pd.DataFrame(data)
    return df


if __name__ == '__main__':
    students_data = []
    urls_df = pd.read_csv("database/urls", sep=' ')
    for program_code, url in urls_df.values:
        url_students_df = request_students_by_url(url)
        url_students_df["program_code"] = program_code
        students_data.append(url_students_df)
    students_data_df = pd.concat(students_data, axis=0)
