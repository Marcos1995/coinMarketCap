# importing the requests library
import requests
import urllib.request, json
from bs4 import BeautifulSoup
from requests_html import HTMLSession
import pandas as pd

token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsIng1dCI6Imwzc1EtNTBjQ0g0eEJWWkxIVEd3blNSNzY4MCIsImtpZCI6Imwzc1EtNTBjQ0g0eEJWWkxIVEd3blNSNzY4MCJ9.eyJhdWQiOiJodHRwczovL2FuYWx5c2lzLndpbmRvd3MubmV0L3Bvd2VyYmkvYXBpIiwiaXNzIjoiaHR0cHM6Ly9zdHMud2luZG93cy5uZXQvNDY3MWViYjktNTQ0NC00NTdkLWE5ZWYtYzg4ODhhZGFmMDNiLyIsImlhdCI6MTYzNTU5MDM4OSwibmJmIjoxNjM1NTkwMzg5LCJleHAiOjE2MzU1OTU3NTksImFjY3QiOjAsImFjciI6IjEiLCJhaW8iOiJFMlpnWUZDOXVqbGF0YUhndTRXVi9ncVYzVFBGZENTL0ZtLzJmSkhuZi81RzE5RlZuL3NBIiwiYW1yIjpbInB3ZCJdLCJhcHBpZCI6IjdmNTlhNzczLTJlYWYtNDI5Yy1hMDU5LTUwZmM1YmIyOGI0NCIsImFwcGlkYWNyIjoiMiIsImZhbWlseV9uYW1lIjoiVXN1YXJpbyIsImdpdmVuX25hbWUiOiJBZG1pbmlzdHJhY2lvbiBQb3dlckJJIiwiaXBhZGRyIjoiMzcuMTUuMzIuMzAiLCJuYW1lIjoiQWRtaW5pc3RyYWNpb24gUG93ZXJCSSBVc3VhcmlvIiwib2lkIjoiNTg0YmY5NDUtOTk2NS00ZjVlLWFiNzUtNDczNDY3ZDM2NTFkIiwib25wcmVtX3NpZCI6IlMtMS01LTIxLTE4MDE2NzQ1MzEtMTQ1NDQ3MTE2NS03MjUzNDU1NDMtMjU3NTMyIiwicHVpZCI6IjEwMDMyMDAxMjM2NDIxRjYiLCJwd2RfZXhwIjoiNzkxOTczIiwicmgiOiIwLkFUc0F1ZXR4UmtSVWZVV3A3OGlJaXRyd08zT25XWC12THB4Q29GbFFfRnV5aTBRN0FMMC4iLCJzY3AiOiJ1c2VyX2ltcGVyc29uYXRpb24iLCJzdWIiOiJUYVI0TUdMc2dGenZPRXluTkZsNTVKMldYZVZINmhDb3lrUWVObWFEak1BIiwidGlkIjoiNDY3MWViYjktNTQ0NC00NTdkLWE5ZWYtYzg4ODhhZGFmMDNiIiwidW5pcXVlX25hbWUiOiJHMDM0NTEyNUBlcy5uYXR1cmd5LmNvbSIsInVwbiI6IkcwMzQ1MTI1QGVzLm5hdHVyZ3kuY29tIiwidXRpIjoiUGpFd2VLdHNiVVc4SXliMmY0eUVBQSIsInZlciI6IjEuMCIsIndpZHMiOlsiYTllYTg5OTYtMTIyZi00Yzc0LTk1MjAtOGVkY2QxOTI4MjZjIiwiYjc5ZmJmNGQtM2VmOS00Njg5LTgxNDMtNzZiMTk0ZTg1NTA5Il19.U1emRXVy4OQhBO2Hk77SIYx1_sy8Ipxl-QCtaoEoiWw1v6-9OABlJpxR6drBkDKfV-ATGgDglXpgUMGwT1nG580nP_qKT_7cyogaH1BgfwpsnauUGGpr4uwxVvWKXIcBhdr8a-DrkUaakRrNrKn1o64w2LfJwx4iHFHPeySouhaq_4Y8n9vKiYBEnjBdOb6gegcDsmjxZqJwFFMw8dZGH2Dc9OjJdRJM7HU4VJYrjAu7hHY-dgYKiuvNi9IX5R-sj6R_DCFtKBl0_2wnKqovcY0_9i5Op7LvfW0IzjsG5Rifdkp4IDgIrRc5Hiy-pn3_Q7_KjYMFNwnbK5NPXjMUfg"

headers = {}
headers["Accept"] = "application/json"
headers["Authorization"] = f"Bearer {token}"

baseUrl = "https://api.powerbi.com/v1.0/myorg/admin/groups?$top=5000&$expand=users,reports,datasets&$filter=type"
personalGroup = "'PersonalGroup'"

for r in range(3):
    print(r)

    if r == 0:
        url = baseUrl + " ne " + personalGroup
        fileName = "Workspaces_not_equals_PersonalGroup"
    elif r == 1:
        url = baseUrl + " eq " + personalGroup
        fileName = "Workspaces_equals_PersonalGroup"
    else:
        url = baseUrl + " eq " + personalGroup + "&$skip=150"
        fileName = "Workspaces_equals_PersonalGroup_skip_150_rows"

    print(url)

    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        newTokens = json.loads(r.content.decode('utf-8'))

    print(len(newTokens))

    # Serializing json 
    json_object = json.dumps(newTokens, indent = 4)

    print(json_object)
    
    # Writing to sample.json
    with open(fileName + ".json", "w") as outfile:
        outfile.write(json_object)