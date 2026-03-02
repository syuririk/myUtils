import requests

ERR_DICT = {
    "INFO-100": "인증키가 유효하지 않습니다. 인증키를 확인하십시오! 인증키가 없는 경우 인증키를 신청하십시오!",
    "INFO-200": "해당하는 데이터가 없습니다.",
    "ERROR-100": "필수 값이 누락되어 있습니다. 필수 값을 확인하십시오! 필수 값이 누락되어 있으면 오류를 발생합니다. 요청 변수를 참고 하십시오!",
    "ERROR-101": "주기와 다른 형식의 날짜 형식입니다.",
    "ERROR-200": "파일타입 값이 누락 혹은 유효하지 않습니다. 파일타입 값을 확인하십시오! 파일타입 값이 누락 혹은 유효하지 않으면 오류를 발생합니다. 요청 변수를 참고 하십시오!",
    "ERROR-300": "조회건수 값이 누락되어 있습니다. 조회시작건수/조회종료건수 값을 확인하십시오! 조회시작건수/조회종료건수 값이 누락되어 있으면 오류를 발생합니다.",
    "ERROR-400": "검색범위가 적정범위를 초과하여 60초 TIMEOUT이 발생하였습니다. 요청조건 조정하여 다시 요청하시기 바랍니다.",
    "ERROR-500": "서버 오류입니다. OpenAPI 호출시 서버에서 오류가 발생하였습니다. 해당 서비스를 찾을 수 없습니다.",
    "ERROR-600": "DB Connection 오류입니다. OpenAPI 호출시 서버에서 DB접속 오류가 발생했습니다.",
    "ERROR-601": "SQL 오류입니다. OpenAPI 호출시 서버에서 SQL 오류가 발생했습니다.",
    "ERROR-602": "과도한 OpenAPI호출로 이용이 제한되었습니다. 잠시후 이용해주시기 바랍니다.",

}

class EcosAPIError(Exception):
    pass


def getRequest(url, print_url=True):

    if print_url:
        print(url)

    res = requests.get(url)

    if res.status_code != 200:
        raise EcosAPIError(f"HTTP Error: {res.status_code}")

    data = res.json()


    if data.get("RESULT"):
        err_cd = data.get("RESULT").get("CODE")
        msg = ERR_DICT.get(err_cd, "API Error")
        raise EcosAPIError(f"[{err_cd}] {msg}")

    return data