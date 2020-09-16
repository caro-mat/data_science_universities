import requests
import csv
import pandas as pd
from bs4 import BeautifulSoup
import time

def send_request(path):
    response = requests.get(path)
    if response.status_code != 200:
        print("Request failed ")
    else:
        print("Request successful "+path)
        return response

def collect_items(initial_path):
    path = initial_path
    items = []
    eof = False

    # Daten einlesen
    while not eof:
        time.sleep(0.1)
        raw_data = send_request(path)
        html = BeautifulSoup(raw_data.content, 'html.parser')

        # Links lesen
        pagination = html.select_one(".pager-next a", href=True)
        if not pagination:
            eof = True
        else:
            link = pagination["href"].split("?")[1]
            path = initial_path + "?" + link

        # Solange loopen, bis alle Seiten gecrawlt sind
        # List-Items lesen

        page_items = html.select("tr", class_=["odd", "even"])
        items += page_items
    return items

def extract_features(items):
    schools = []

    for item in items:
        try:
            name = item.find("a").text
        except Exception as error:
            name = ""

        try:
            rank_overall = item.select("center")[0].text
        except Exception as error:
            rank_overall = ""

        try:
            rank_presence = item.select("center")[2].text
        except Exception as error:
            rank_presence = ""

        try:
            rank_impact = item.select("center")[3].text
        except Exception as error:
            rank_impact = ""

        try:
            rank_open = item.select("center")[4].text
        except Exception as error:
            rank_open = ""

        try:
            rank_excellence = item.select("center")[5].text
        except Exception as error:
            rank_excellence = ""

        school = [name, rank_overall, rank_presence, rank_impact, rank_open, rank_excellence]
        schools.append(school)

    for item in items:
        try:
            title = item.find('div', class_='title').h4.text
        except Exception as error:
            title = ''


    content_data_frame = pd.DataFrame(schools)
    content_data_frame.columns = \
        ["name", "rank_overall", "rank_presence", "rank_impact", "rank_open", "rank_excellence"]
    return content_data_frame

def export_to_file(data_frame, path, file_name):

    full_path = path + file_name
    with open(full_path, 'w', encoding='utf-8', newline='') as file:
        export = data_frame.to_csv(quoting=csv.QUOTE_NONNUMERIC, index=False, encoding='utf-8')
        file.write(export)

def main():

    items = collect_items("http://www.webometrics.info/en/world")
    content_data_frame = extract_features(items)
    export_to_file(content_data_frame, '../Daten/', 'school_ranking.csv')


if __name__ == '__main__':
    main()

