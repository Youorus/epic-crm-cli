import requests
from cli.utils.config import TOKEN_URL, ME_URL

def api_login(username: str, password: str):
    try:
        response = requests.post(TOKEN_URL, data={
            'username': username,
            'password': password
        })
        return response
    except requests.exceptions.RequestException:
        return None

def api_get_current_user(token: str):
    headers = {'Authorization': f'Bearer {token}'}
    try:
        return requests.get(ME_URL, headers=headers)
    except requests.exceptions.RequestException:
        return None