import requests, time, re
from bs4 import BeautifulSoup
import pandas as pd


INPUT_FILE_NAME = "uspsa.csv"
OUTPUT_FILE_NAME = "himarcel.csv"
ERROR_FILE_NAME = "err.csv"
SLEEP_TIME = 10 # in s between member searches
WRITE_TO_CSV = 10 # write to csv every n pass


def add_to_dict(CompleteDict, first, last, id, division, classification, Index):
    CompleteDict['firstName'][Index] = first
    CompleteDict['lastName'][Index] = last
    CompleteDict['uspsaNumber'][Index] = id
    CompleteDict['division'][Index] = division
    CompleteDict['classification'][Index] = classification 
    return False

def save_to_csv(theDict, ErrorDict):
    df = pd.DataFrame(theDict)
    df.to_csv(OUTPUT_FILE_NAME, index=False)
    df2 = pd.DataFrame(ErrorDict)
    df2.to_csv(ERROR_FILE_NAME, index=False)


StartingPrefix = ["A", "FY", "TY"]
Divisions = ["Open", "Limited", "Limited 10", "Production", "Revolver", "Single Stack", "Carry Optics", "PCC"]

DictFromCSV = pd.read_csv(INPUT_FILE_NAME).to_dict()

CompleteDict = {"firstName": {},
                "lastName": {},
                "uspsaNumber": {},
                "division": {},
                "classification": {}
                }

UnfoundDict = {"firstName": {},
               "lastName": {},
               "index": {}
               }

Index = 0
UnfoundIndex = 0

for i in DictFromCSV['firstName']:

    FoundUser = False
    id = DictFromCSV['uspsaNumber'][i]
    FirstName = DictFromCSV['firstName'][i]
    LastName = DictFromCSV['lastName'][i]

    if not pd.isna(id):
        StrippedID = re.sub('\D', '', id)
        OriginalPrefix = id.strip(StrippedID).upper()
        StartingIndex = 0

        while not FoundUser and StartingIndex < (len(StartingPrefix) + 1):
            Response = requests.get(f"https://uspsa.org/classification/{id}")
            MySoup = BeautifulSoup(Response.text, "html.parser") 

            Error = MySoup.find(name="span", text="Error")    
            if Error is not None:
                save_to_csv(CompleteDict, UnfoundDict)
                input(f"Rate limited at index {i} press enter to continue")

            else:
                Error = MySoup.find(name="strong", text=re.compile("Oops!"))
                FoundUser = Error is None
                if not FoundUser and StartingIndex < len(StartingPrefix):
                    time.sleep(SLEEP_TIME)
                    if StartingPrefix[StartingIndex] == OriginalPrefix:
                        StartingIndex += 1
                    if StartingIndex < len(StartingPrefix):
                        id = f"{StartingPrefix[StartingIndex]}{StrippedID}"
                StartingIndex += 1

    if not FoundUser:
        UnfoundDict["firstName"][UnfoundIndex] = FirstName
        UnfoundDict["lastName"][UnfoundIndex] = LastName
        UnfoundDict["index"][UnfoundIndex] = i
        UnfoundIndex += 1

    else:
        Unclassified = True
        for Division in Divisions:
            Results = MySoup.find(name="th", text=re.compile(Division))
            RawDivision = Results.getText()
            Division = RawDivision.strip()
            RawClass = Results.find_next_sibling("td")
            RealClass = RawClass.getText()[-2:]
            Classification = RealClass.strip()
            if Classification == "X":
                if Unclassified:
                    Unclassified = add_to_dict(CompleteDict, FirstName, LastName, id, "Non-member", "X", Index) 
                    Index += 1   

            elif Classification != "U":
                Unclassified = add_to_dict(CompleteDict, FirstName, LastName, id, Division, Classification, Index)
                Index += 1
        
        if Unclassified:
            Unclassified = add_to_dict(CompleteDict, FirstName, LastName, id, "Unclassified", "U", Index)
            Index += 1    

    if i % WRITE_TO_CSV == 0 and i != 0:
        save_to_csv(CompleteDict, UnfoundDict)

    time.sleep(SLEEP_TIME)

save_to_csv(CompleteDict, UnfoundDict)
