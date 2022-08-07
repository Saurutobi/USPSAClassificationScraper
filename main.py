import requests, time, re
from bs4 import BeautifulSoup
import pandas as pd


INPUT_FILE_NAME = "Book1.csv"
OUTPUT_FILE_NAME = "out.csv"
SLEEP_TIME = 10 # in s between member searches


StartingPrefix = ["A", "FY", "TY", "L", "B"]
Divisions = ["Open", "Limited", "Limited 10", "Production", "Revolver", "Single Stack", "Carry Optics", "PCC"]

DictFromCSV = pd.read_csv(INPUT_FILE_NAME).to_dict()

CompleteDict = {"firstName": {},
                "lastName": {},
                "uspsaNumber": {},
                "division": {},
                "classification": {}
                }

Index = 0

for i in DictFromCSV['firstName']:

    FoundUser = False
    id = DictFromCSV['uspsaNumber'][i]
    StrippedID = re.sub('\D', '', id)
    OriginalPrefix = id.strip(StrippedID).upper()
    StartingIndex = 0
    FirstName = DictFromCSV['firstName'][i]
    LastName = DictFromCSV['lastName'][i]

    while not FoundUser and StartingIndex < len(StartingPrefix):
        Response = requests.get(f"https://uspsa.org/classification/{id}")
        MySoup = BeautifulSoup(Response.text, "html.parser") 

        Error = MySoup.find(name="span", text="Error")    
        if Error is not None:
            print("Rate limited, sleeping for 1 hour")
            time.sleep(3600)

        else:
            Error = MySoup.find(name="strong", text=re.compile("Oops!"))
            FoundUser = Error is None
            if not FoundUser:
                if StartingPrefix[StartingIndex] == OriginalPrefix:
                    StartingIndex += 1
                if StartingIndex < len(StartingPrefix):
                    id = f"{StartingPrefix[StartingIndex]}{StrippedID}"
                    StartingIndex += 1

    if not FoundUser:
        print(f"Unable to find data for {FirstName} {LastName} with uspsa number {OriginalPrefix}{StrippedID}")

    else:
        for Division in Divisions:
            Results = MySoup.find(name="th", text=re.compile(Division))
            RawDivision = Results.getText()
            Division = RawDivision.strip()
            RawClass = Results.find_next_sibling("td")
            RealClass = RawClass.getText()[-2:]
            Classification = RealClass.strip()
            if Classification != "U":
                CompleteDict['firstName'][Index] = FirstName
                CompleteDict['lastName'][Index] = LastName
                CompleteDict['uspsaNumber'][Index] = id
                CompleteDict['division'][Index] = Division
                CompleteDict['classification'][Index] = Classification
                Index += 1
        time.sleep(SLEEP_TIME)

df = pd.DataFrame(CompleteDict)
df.to_csv(OUTPUT_FILE_NAME, index=False)
print("Done!")