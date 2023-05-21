# USPSAClassificationScraper
The main.py uses "uspsa.csv" to scrape uspsa.com classifications for the competitors in the file

Use <code>python main.py</code> to run

Will output to "classifications.csv" and errors go to "Errors.csv"

# Requirements
- Use <code>pip3 install -r requirements.txt</code> to install the requirements before running main.py
- Add "uspsa.csv" file to base directory

# Uspsa.csv file
You'll need to add this file. Format is

<code>firstname,lastname,uspsaNumber
[firstnamehere],[lastnamehere][uspsanumberhere]</code>