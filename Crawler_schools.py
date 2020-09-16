import requests
import csv
import pandas as pd
from bs4 import BeautifulSoup
import time

def send_request(path):
    '''Ruft den angegebenen Pfad auf und ruft den html Code ab.
    Gibt aus ob die Anfrage erfolgreich war oder nicht'''

    response = requests.get(path)
    if response.status_code != 200:
        print("Request failed " + path)
    else:
        print("Request successful " + path)
        return response

def collect_items(initial_path):
    '''Ruft über die send_request Funktion den html Code ab.
    Geht durch alle Seiten die unsere Daten beinhaltet.
    Transformiert den html Code mit Beautifulsoup.'''

    path = initial_path
    items = []
    eof = False

    # Daten der Master Studiengänge lesen
    while not eof:
        time.sleep(0.1)
        raw_data = send_request(path)
        html = BeautifulSoup(raw_data.content, 'html.parser')

        # Solange loopen, bis alle Seiten gecrawlt sind
        # List-Items lesen
        page_items = html.find_all(class_="program-listitem")
        items += page_items

        # Links lesen
        pagination = html.find(class_='pagination')
        links = pagination.find_all('a')
        if not links:
            eof = True
        else:
            # Next-Link ermitteln
            link = links[0]
            button = link.find('button')

            # Prüfen ob "Next"-Link vorliegt. Falls nicht, ist es "Previous". Dann nächsten Link...
            if button.text != 'Next':
                if len(links) > 1:
                    link = links[1]
                    button = link.find('button')

                    # Püfen ob der 2. Link jetzt Next ist. Falls nicht break...
                    if button.text != 'Next':
                        break
                else:
                    break
            path = link.get('href')

    return items

def extract_features(items):
    '''Extrahiert die einzelnen Datenfelder aus dem html Code.Speichert pro Element alles in einer Liste.
    Führt alle Elementlisten zu einer Liste zusammen. Generiert ein Pandas Dataframe'''

    content_table = []

    for item in items:
        try:
            title = item.find('div', class_='title').h4.text
        except Exception as error:
            title = ''

        try:
            school = item.find('div', class_='school').text
        except Exception as error:
            school = ''

        try:
            location = item.find('span', class_='location').text
        except Exception as error:
            location = ''

        try:
            description = item.find('p', class_='desc').text
        except Exception as error:
            description = ''

        try:
            degree = item.find('div', class_='degree').find('div', class_='label-item').text
        except Exception as error:
            degree = ''

        try:
            pace = item.find('div', class_='pace').find('div', class_='label-item').text
        except Exception as error:
            pace = ''

        try:
            duration = item.find('div', class_='duration').find('div', class_='label-item').text
        except Exception as error:
            duration = ''

        try:
            languages = item.find('div', class_='languages').find('div', class_='label-item').text
        except Exception as error:
            languages = ''

        try:
            start = item.find('div', class_='start').find('div', class_='label-item').text
        except Exception as error:
            start = ''

        try:
            based = item.find('div', class_='based').find('div', class_='label-item').text
        except Exception as error:
            based = ''

        content_element = [title, school, location, description, degree, pace, duration, languages, start, based]
        content_table.append(content_element)

    content_data_frame = pd.DataFrame(content_table)
    content_data_frame.columns = \
        ['title', 'school', 'location', 'description', 'degree', 'pace', 'duration', 'languages', 'start', 'based']
    return content_data_frame

def cleanse_data(data_frame):
    '''Cleant die Daten mit Pandas, entfernt Leerschläge und Zeilenumbrüche'''

    # Zeilenschaltung und Leerzeichen aus location entfernen
    # test = data_frame['location'][1]
    data_frame['location'] = data_frame['location'].apply(lambda x: x.replace('\n', ''))
    data_frame['location'] = data_frame['location'].apply(lambda x: x.replace(' ', ''))

    # Zeilenschaltung aus description entfernen
    data_frame['description'] = data_frame['description'].apply(lambda x: x.replace('\n', ''))

    # Zeilenschaltung und Leerzeichen aus degree entfernen
    data_frame['degree'] = data_frame['degree'].apply(lambda x: x.replace('\n', ''))
    data_frame['degree'] = data_frame['degree'].apply(lambda x: x.replace(' ', ''))

    # Zeilenschaltung und Leerzeichen aus languages entfernen
    data_frame['languages'] = data_frame['languages'].apply(lambda x: x.replace('\n', ''))
    data_frame['languages'] = data_frame['languages'].apply(lambda x: x.replace(' ', ''))

def export_to_file(data_frame, path, file_name):
    '''Exportiert das Dataframe als csv file'''

    full_path = path + file_name
    with open(full_path, 'w', encoding='utf-8', newline='') as file:
        export = data_frame.to_csv(quoting=csv.QUOTE_NONNUMERIC, index=False, encoding='utf-8')
        file.write(export)

def main():
    ''' Sammelt alle Daten. Extrahiert die notwendigen Elemente und speichert in einem Dataframe.
    Reinigt das Dataframe. Exportiert die Daten'''

    # Master
    items = collect_items('https://www.masterstudies.com/Masters-Degree/Data-Science/')
    data_frame_master = extract_features(items)
    cleanse_data(data_frame_master)
    export_to_file(data_frame_master, '../Daten/', 'school_master.csv')

    # Bachelor
    items = collect_items('https://www.bachelorstudies.com/Bachelor/Data-Science/')
    data_frame_bachelor = extract_features(items)
    cleanse_data(data_frame_bachelor)
    export_to_file(data_frame_bachelor, '../Daten/', 'school_bachelor.csv')


if __name__ == '__main__':
    main()

