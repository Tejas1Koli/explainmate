from pyairtable import Table
import os

AIRTABLE_TOKEN = "patpLoSfEWoyrWAyb.45db2ed720078b9f23e3d3380c104ed19ae58b47457d725ce40249cd3b3b690f"
BASE_ID = "appbhGziRoDiAjEjP"
TABLE_NAME = "Explainmate"

# Test Airtable API connectivity and permissions using curl from Python
curl_cmd = f"curl https://api.airtable.com/v0/{BASE_ID}/{TABLE_NAME} -H 'Authorization: Bearer {AIRTABLE_TOKEN}'"

print("Running:", curl_cmd)
os.system(curl_cmd)

table = Table(AIRTABLE_TOKEN, BASE_ID, TABLE_NAME)
record = table.create({
    "timestamp": "2025-05-04",
    "query": "test",
    "explanation": "test",
    "feedback": "test"
})
print(record)
