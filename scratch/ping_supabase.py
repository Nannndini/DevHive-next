import urllib.request
import json
import os
from dotenv import load_dotenv

load_dotenv("frontend/api/.env")
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

print("Checking Supabase URL:", url)
try:
    req = urllib.request.Request(
        f"{url}/rest/v1/",
        headers={"apikey": key, "Authorization": f"Bearer {key}"}
    )
    with urllib.request.urlopen(req) as res:
        print("Status code:", res.status)
        print("Body:", res.read().decode())
except Exception as e:
    print("Error connecting to Supabase REST API:", e)
    if hasattr(e, "read"):
        print("Detail:", e.read().decode())
