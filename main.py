import requests, time, re
from bs4 import BeautifulSoup
import pandas as pd

INPUT_FILE_NAME = "Book1.csv"
OUTPUT_FILE_NAME = "out.csv"
SLEEP_TIME = 10 # in s

starting_prefix = ["A", "FY", "TY", "L", "B"]

dict_from_csv = pd.read_csv(INPUT_FILE_NAME).to_dict()

complete_dict = {"firstName": {},
                "lastName": {},
                "uspsaNumber": {},
                "division": {},
                "classification": {}
                }

index = 0

for i in dict_from_csv['firstName']:

    found_user = False
    id = dict_from_csv['uspsaNumber'][i]
    starting_index = 0
    while not found_user:
        response = requests.get(f"https://uspsa.org/classification/{id}")
        my_soup = BeautifulSoup(response.text, "html.parser") 
        error = my_soup.find(name="div", class_="alert")
        found_user = error is None
        if not found_user:
            stripped_id = re.sub('\D', '', id)
            id = f"{starting_prefix[starting_index]}{stripped_id}"
            starting_index += 1

    anchors = my_soup.find_all(name="th", scope="row")

    for j in range(9,15):
        raw_division = anchors[j].getText()
        division = raw_division.strip()
        raw_class = anchors[j].find_next_sibling("td")
        real_class = raw_class.getText()[-2:]
        classification = real_class.strip()
        if "U" not in real_class:
            complete_dict['firstName'][index] = dict_from_csv['firstName'][i]
            complete_dict['lastName'][index] = dict_from_csv['lastName'][i]
            complete_dict['uspsaNumber'][index] = id
            complete_dict['division'][index] = division
            complete_dict['classification'][index] = classification
            index += 1
    time.sleep(SLEEP_TIME)

df = pd.DataFrame(complete_dict)
df.to_csv(OUTPUT_FILE_NAME, index=False)
print("Done!")