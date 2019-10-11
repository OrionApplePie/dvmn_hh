import os

from dotenv import load_dotenv
import requests

SUPERJOB_API_URL = "https://api.superjob.ru/2.0/user/current/"

AUTHORIZATION_URL = "https://www.superjob.ru/authorize/"
ACCESS_TOKEN_API = "https://api.superjob.ru/2.0/oauth2/access_token/"


def main():
    load_dotenv()
    
    secret_key = os.getenv("SUPERJOB_SECRET_KEY")

    headers = {
        "X-Api-App-Id": secret_key
    }
    response = requests.get(
        url=AUTHORIZATION_URL,
        headers=headers,
        params={"client_id": "1381", "redirect_uri": "https://www.dvmn.org/"}
    )
    # token_resp = requests.get(
    #     url=ACCESS_TOKEN_API
    # )

    print(response.text)
    # print(token_resp.json)


if __name__ == "__main__":
    main()