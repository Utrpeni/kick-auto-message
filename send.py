
import os
import json
import urllib.request
import urllib.parse
import urllib.error

BASE = "https://api.kick.com"
TOKEN_URL = "https://id.kick.com/oauth/token"

def request(url, data=None, headers=None):
    req = urllib.request.Request(url, data=data, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        print("CHYBA HTTP:", e.code)
        print("ADRESA:", url)
        print("ODPOVED KICKU:", e.read().decode(errors="replace"))
        raise
client_id = os.environ["KICK_CLIENT_ID"]
client_secret = os.environ["KICK_CLIENT_SECRET"]
refresh_token = os.environ["KICK_REFRESH_TOKEN"]

# Obnoveni prihlaseni uzivatele
token_data = urllib.parse.urlencode({
    "grant_type": "refresh_token",
    "client_id": client_id,
    "client_secret": client_secret,
    "refresh_token": refresh_token
}).encode()

user_token = request(
    TOKEN_URL,
    token_data,
    {"Content-Type": "application/x-www-form-urlencoded"}
)["access_token"]

# Ziskani pristupu k verejnym udajum kanalu
app_data = urllib.parse.urlencode({
    "grant_type": "client_credentials",
    "client_id": client_id,
    "client_secret": client_secret
}).encode()

app_token = request(
    TOKEN_URL,
    app_data,
    {"Content-Type": "application/x-www-form-urlencoded"}
)["access_token"]

# Vyhledani kanalu Spajkk
channels = request(
    BASE + "/public/v1/channels?slug=spajkk",
    headers={"Authorization": "Bearer " + app_token}
)

if not channels.get("data"):
    raise Exception("Kanal Spajkk nebyl nalezen.")

broadcaster_id = channels["data"][0]["broadcaster_user_id"]

# Odeslani zpravy
message = json.dumps({
    "broadcaster_user_id": broadcaster_id,
    "content": "bodiky",
    "type": "user"
}).encode()

result = request(
    BASE + "/public/v1/chat",
    message,
    {
        "Authorization": "Bearer " + user_token,
        "Content-Type": "application/json"
    }
)

if result.get("data", {}).get("is_sent"):
    print("ZPRAVA BODIKY BYLA USPESNE ODESLANA!")
else:
    print("Kick zpravu nepotvrdil:", result)
