import requests

def address2coordinate(
    address:str, 
    apiurl:str = "https://api.vworld.kr/req/address?", 
    apikey:str = "96DC019B-5E26-33AD-B6A9-9B4991045E75", 
    ) -> tuple:
    """주소를 경도(longitude), 위도(latitude)로 변환하는 함수

    Args:
        apiurl (str): v-world 사용 api 주소
        apikey (str): v-world 사용 api 인증키
        address (str): 경도, 위도로 변환하고자하는 주소
    Returns:
        tuple: 경도(longitude), 위도(latitude) 값
    """
    ## 요청파라미터
    params = {
        "service": "address",
        "request": "getcoord",
        "crs": "epsg:4326",
        "address": address,
        "format": "json",
        "type": "road",
        "key": apikey
    }

    ## 결과응답
    response = requests.get(apiurl, params=params)
    
    ## 에러가 없을 경우 결과응답으로부터 경도(longitude), 위도(latitude) 추출
    if response.status_code == 200:
        longitude = response.json()["response"]["result"]["point"]["x"]
        latitude = response.json()["response"]["result"]["point"]["y"]
    else:
        print("Error") 
        
    return longitude, latitude