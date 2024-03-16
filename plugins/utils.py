import random
import string
from datetime import datetime, timedelta
from shortzy import Shortzy  # Assuming Shortzy is correctly installed
from plugins.helpers import str_to_b64
from helper.database import db

TOKENS = {}

async def short_link(link):
    current_time = datetime.now() + timedelta(hours=5, minutes=30)  # Getting current time in IST
    hour = current_time.hour
    
    if 6 <= hour < 18:  
        api = "5626d3cf7e6c34f258a340185bf6cc050b7dbb8b"
        site = "publicearn.com"
    else:  
        api = "5syxPtyWqBTLADWqd4jljPras8H3"
        site = "api.shareus.io"
    
    shortzy = Shortzy(api, site) 
    short_link = await shortzy.convert(link)
    return short_link


async def check_token(userid, token):
    if userid in TOKENS:
        user_tokens = TOKENS[userid]
        if token in user_tokens and not user_tokens[token]:
            return True
    return False

async def get_token(userid, link):
    token = ''.join(random.choices(string.ascii_letters + string.digits, k=7))
    TOKENS.setdefault(userid, {})[token] = False
    ids = f"verify-{userid}-{token}"
    idss = str_to_b64(str(ids))
    verification_link = f"{link}{idss}"
    shortened_link = await short_link(verification_link)
    return shortened_link

async def verify_user(userid, token):
    if userid in TOKENS:
        user_tokens = TOKENS[userid]
        if token in user_tokens:
            user_tokens[token] = True
            verifyt = datetime.now() + timedelta(hours=12)
            await db.update_user_info(userid, {"verify": verifyt})  # Corrected user_id to userid

async def check_verification(userid):
    user = await db.get_userdata(userid)
    verifyt = user.get("verify", None)  # Corrected syntax
    if verifyt is not None:
        expiration_date = verifyt
        return expiration_date >= datetime.now()
    return False
