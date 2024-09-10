import requests
import json

APP_KEY = "PS0zASCEGosvWBkZPk1aC88OmRGIdHhBhG66"
APP_SECRET = "VBKTfcZpHs0rGWIBZPiNQLW2QQ1KsgjmKcCLHFsLboNHFQz7NNAlrW+oTE0weyNtnsco0a/CL8pn9ZyH7qiFR4w/4RbiPd8DaZLf4i9UZi+5Gs0eD2rCOZ696UsnXMt2FSqql10vHqO1ZkdE+/5qXF2KWsmJ3Yp0TdAdnuoO143v6Atp0GE="
URL_BASE = "https://openapi.koreainvestment.com:9443" #https://openapivts.koreainvestment.com:29443:모의 투자.

headers = {"content-type":"application/json"}
body = {"grant_type":"client_credentials",
        "appkey":APP_KEY, 
        "appsecret":APP_SECRET}
PATH = "oauth2/tokenP"#/oauth2/Approval

URL = f"{URL_BASE}/{PATH}"
print(URL)

res = requests.post(URL, headers=headers, data=json.dumps(body))
print(res.text)
#>>> '{"access_token":"ACCESS_TOKEN","token_type":"Bearer","expires_in":86400}'

ACCESS_TOKEN = res.json()["access_token"]
print(ACCESS_TOKEN)
#>>> ACCESS_TOKEN

