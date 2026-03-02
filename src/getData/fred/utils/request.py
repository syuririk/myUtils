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

    if res.status_code != 200:
        raise FredAPIError(f"HTTP 오류: {res.status_code}")

    data = res.json()

    err_cd = data.get("error_code")

    if err_cd:
        msg = ERR_DICT.get(err_cd, "알 수 없는 오류")
        raise FisisAPIError(f"[{err_cd}] {msg}")

    return data



