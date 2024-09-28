import streamlit as st
import pandas as pd
import requests
import folium
from streamlit_folium import folium_static
from .list_archive import *

api_key = st.secrets["PUBLIC_DATA_API_KEY"]

# 데이터 로드 함수
@st.cache_data
def load_data(key):
    url = "http://api.data.go.kr/openapi/tn_pubr_public_trrsrt_api?serviceKey=" + key + "&pageNo=1&numOfRows=10000&type=json"
    response = requests.get(url)
    data = response.json()
    items = data['response']['body']['items']

    df = pd.DataFrame(items)
    df.columns = data_columns()
    
    df = df.map(lambda x: x.strip() if isinstance(x, str) else x)  # 문자열의 앞뒤 공백 제거
    df.replace("", None, inplace=True)  # 빈 값 None으로 채우기
    df['Address'] = df['Address'].fillna(df['소재지지번주소'])
    df = df.drop(['관광지구분', '소재지지번주소', '면적', '지정일자', '수용인원수', '데이터기준일자', '제공기관코드'], axis=1)

    df['Latitude'] = df['Latitude'].astype(float)
    df['Longitude'] = df['Longitude'].astype(float)
    df['Parking Spaces'] = df['Parking Spaces'].astype(int)

    return df

# 지도 생성 함수
def create_map(data):
    if data.empty:
        return folium.Map(location=[36.5, 127.5], zoom_start=7)  # Default to center of Korea
    
    # 위도와 경도의 평균값 계산
    center_lat = data['Latitude'].mean()
    center_lon = data['Longitude'].mean()
    # 위도와 경도의 리스트로부터 최솟값과 최댓값 계산
    lats = data['Latitude']
    lons = data['Longitude']
    min_lat, max_lat = min(lats), max(lats)
    min_lon, max_lon = min(lons), max(lons)

    m = folium.Map(location=[center_lat, center_lon], zoom_start=11)
    m.fit_bounds([[min_lat, min_lon], [max_lat, max_lon]])  # 지도 범위에 맞게 자동 조정

    for idx, row in data.iterrows():
        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            popup=folium.Popup(html=f"""
                               <div style="text-align: center;">
                               <b>{row['Name']}</b><br>
                               {row['Address']}<br>
                               (Call: {row['Number']})<br>
                               </div>""", max_width=300),
            icon=folium.Icon(icon='info-sign', prefix='fa', color='blue', icon_color='white'),
            tooltip=row['Name']
        ).add_to(m)
    
    return m

# # 세부 사항 함수
# def show_details(data):
#     st.subheader(data['Name'])
#     st.write(f"Address: {data['Address']}")
#     st.write(f"Public Facilities: {data['Public Facilities']}")
#     st.write(f"Accommodation: {data['Accommodation']}")
#     st.write(f"Sports and Recreation: {data['Sports and Recreation']}")
#     st.write(f"Rest and Culture: {data['Rest and Culture']}")
#     st.write(f"Guest Facilities: {data['Guest Facilities']}")
#     st.write(f"Support Facilities: {data['Support Facilities']}")
#     st.write(f"Parking Spaces: {data['Parking Spaces']}")
#     st.write(f"Introduction: {data['Introduction']}")
#     st.write(f"Management: {data['Management']} (Tel: {data['Number']})")

# 옵션 리스트
regions = data_regions()
region_detail = data_detailed_regions()
public_facilities = data_public_facilities()
accommodations = data_accommodations()

# main 함수
def show_tourism_map():
    st.title("🚗 Where to Visit?!")
    
    # 데이터 로드
    df = load_data(api_key)

    col1, col2, col3 = st.columns([1, 2, 0.5])
    
    # 데이터 필터링
    with col1:
        with st.container(border=True):
            st.write("Filter")
            name_search = st.text_input("Name", key="name_search")
            selected_region = st.selectbox("지역 선택(필수)", regions, key="region")
            selected_sub_region = st.selectbox("세부 지역(선택)", sorted(region_detail[selected_region]), key="sub_region")
            selected_facilities = st.multiselect("편의시설", sorted(public_facilities), key="facilities")
            selected_accommodations = st.multiselect("숙박시설", sorted(accommodations), key="accommodations")
            parking_available = st.checkbox("주차 가능", key="parking")
    
    # 필터링 데이터프레임 생성
    filtered_df = df[df['Address'].str.contains(selected_region)]

    if name_search:
        filtered_df = filtered_df[filtered_df['Name'].str.contains(name_search, case=False)]
    
    if selected_sub_region == 'ALL':
        pass
    else:
        filtered_df = filtered_df[filtered_df['Address'].str.contains(selected_sub_region, case=False)]
    
    if selected_facilities:
        facility_mask = filtered_df['Public Facilities'].apply(lambda x: any(facility in str(x) for facility in selected_facilities))
        filtered_df = filtered_df[facility_mask]
    
    if selected_accommodations:
        accommodation_mask = filtered_df['Accommodation'].apply(lambda x: any(acc in str(x) for acc in selected_accommodations))
        filtered_df = filtered_df[accommodation_mask]
    
    if parking_available:
        filtered_df = filtered_df[filtered_df['Parking Spaces'] != 0]

    filtered_df = filtered_df.reset_index(drop=True)
    
    # 지도 표시
    with col2:
        map = create_map(filtered_df)
        folium_static(map)
    
    # 검색 결과 없음
    if filtered_df.empty:
        st.error("No tourist attractions match your selection.")

    # 데이터프레임으로 리스트 정리
    st.write('Filtered List')
    st.table(filtered_df[['Name', 'Introduction', 'Address', 'Number']])