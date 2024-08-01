import pandas as pd
import time
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests


DIMA_ID = "175-199-309 03"


def make_tg_post(title, body):
    tg_api_token = "7060682166:AAFAjE8y8BDGikZ7otEoXC7MdnxmEtHGcEk"
    post_text = f"""<strong>{title}</strong>\n{body}"""

    response = requests.get(f"https://api.telegram.org/bot{tg_api_token}/sendMessage",
                            params={"chat_id": "@dimon_admission",
                                    "text": post_text,
                                    "parse_mode": "HTML"})
    if response.status_code == 200:
        return post_text


def split_students_into_programs(sdf_: pd.DataFrame, pdf_: pd.DataFrame) -> pd.DataFrame:
    """
    Split students into programs using priorities

    sdf - students dataframe
    pdf - programs dataframe
    """
    sdf = sdf_.copy()
    pdf = pdf_.copy()

    free_places = pdf[["program_code", "places"]].set_index("program_code").to_dict()["places"]
    split_result = []

    sdf = sdf.sort_values(by=["score", "priority"], ascending=(False, True))

    while (len(sdf) > 0) and (sum(free_places.values()) > 0):
        top = sdf.head(1).to_dict("records")[0]

        if free_places[top["program_code"]] > 0:
            free_places[top["program_code"]] -= 1
            top["free_places_after"] = free_places[top["program_code"]]
            split_result.append(top)
            sdf = sdf.loc[sdf.student_id != top["student_id"]]
        else:
            sdf = sdf.iloc[1:]

    return pd.DataFrame(split_result)


def request_students_by_url(program_url: str):
    """
    A function that returns a table with applicants' data
    """
    free_places = []

    # open browser
    driver = webdriver.Chrome()
    driver.get(program_url)

    # click checkboxes
    WebDriverWait(driver, 360).until(
        EC.element_to_be_clickable((By.ID, 'original')))

    places = driver.find_element(By.CSS_SELECTOR, ".col-lg-3.d-flex.justify-content-center.align-items-center.places-list").text
    places = int(places.split(": ")[-1])
    places_dict = {
        "url": program_url,
        "places": places,
    }

    driver.find_element(by=By.ID, value='original').click()
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
    return df, places_dict


def scrap_data(df: pd.DataFrame) -> [pd.DataFrame, pd.DataFrame]:
    """
    Return students data for all programs
    """
    st_df = []
    places_list = []
    for program_code, url in df[["program_code", "url"]].values:
        url_students_df, places_dict = request_students_by_url(url)
        url_students_df["program_code"] = program_code
        st_df.append(url_students_df)
        places_list.append(places_dict)
    students_data_df = pd.concat(st_df, axis=0)
    places_df = pd.concat(places_list, axis=0)
    return students_data_df, places_df


if __name__ == '__main__':
    programs_df = pd.read_csv("database/urls_fkti.csv")
    students_df, places_df = scrap_data(programs_df)  # to get new info
    # students_df = pd.read_csv("database/test_students.csv")  # to get mocked data

    programs_df = pd.merge(programs_df, places_df, on=["url"])
    result_df = split_students_into_programs(students_df, programs_df)

    # get dima position by DIMA_ID
    dima_program_info = result_df.loc[result_df.student_id == DIMA_ID].to_dict("records")[0]

    # send info to tg chat
    program_name, program_code, all_places = programs_df.loc[
        programs_df.program_code == dima_program_info["program_code"],
        ["program_name", "program_code", "places"]
    ].values[0]
    
    position_num = all_places - dima_program_info["free_places_after"]
    
    title = f'{program_name} ({program_code})'
    body = f'{position_num}/{all_places}'
    make_tg_post(title=title, body=body)
