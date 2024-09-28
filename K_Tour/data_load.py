import requests
import pandas as pd

def load_data(key):
    url = "http://api.data.go.kr/openapi/tn_pubr_public_trrsrt_api?serviceKey=" + key + "&pageNo=1&numOfRows=10000&type=json"

    response = requests.get(url)
    data = response.json()
    items = data['response']['body']['items']

    df = pd.DataFrame(items)
    df.columns = ['Name', '관광지구분', 'Address', '소재지지번주소',
                'Latitude', 'Longitude', '면적', 'Public Facilities', 'Accommodation',
                'Sports and Recreation', 'Rest and Culture', 'Guest Facilities',
                'Support Facilities', '지정일자', '수용인원수', 'Parking Spaces',
                'Introduction', 'Number', 'Management', '데이터기준일자', '제공기관코드']
    
    df = df.map(lambda x: x.strip() if isinstance(x, str) else x)  # 문자열의 앞뒤 공백 제거
    df.replace("", None, inplace=True)  # 빈 값 None으로 채우기
    df['Address'] = df['Address'].fillna(df['소재지지번주소'])
    df = df.drop(['관광지구분', '소재지지번주소', '면적', '지정일자', '수용인원수', '데이터기준일자', '제공기관코드'], axis=1)

    df['Latitude'] = df['Latitude'].astype(float)
    df['Longitude'] = df['Longitude'].astype(float)
    df['Parking Spaces'] = df['Parking Spaces'].astype(int)

    return df