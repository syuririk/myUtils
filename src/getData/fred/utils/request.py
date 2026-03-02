import requests

ERR_DICT = {
    "400": "Bad Request",
    "404": "Not Found",
    "423": "Locked",
    "429": "Too Many Requests",
    "500": "Internal Server Error"
}

class FredAPIError(Exception):
    pass


def getRequest(url, print_url=True):

    if print_url:
        print(url)

    res = requests.get(url)

    data = res.json()

    err_cd = data.get("error_code")

    if err_cd:
        msg = data.get("error_message")
        raise FisisAPIError(f"[{err_cd}] {msg}")

    return data



