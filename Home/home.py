import streamlit as st

def show_home():
    # Title
    title_cols = st.columns([1, 7])
    with title_cols[0]:
        st.image('https://www.mois.go.kr/images/chd/contents/markLang_img1.gif')
    with title_cols[1]:
        st.subheader('🇰🇷 Welcome to **At Korea**!')

    # 외교부 이미지
    image_links = ['https://www.mois.go.kr/images/eng/contents/symbol_photo1.jpg',
                   'https://www.mois.go.kr/images/eng/contents/symbol_photo3.jpg',
                   'https://www.mois.go.kr/images/eng/contents/symbol_photo5.jpg',
                   'https://www.mois.go.kr/images/eng/contents/symbol_photo8.jpg',
                   'https://www.mois.go.kr/images/eng/contents/symbol_photo10.jpg']
    image_captions = ['The National Flag - Taegeukgi',
                      'The National Anthem - Aegukga',
                      'The National Flower - Mugunghwa',
                      'The National Seal - Guksae',
                      'The National Emblem - Nara Munjang']
    cols = st.columns(5)
    for i in range(5):
        with cols[i]:
            st.image(image=image_links[i], caption=image_captions[i], use_column_width=True)

    # 버튼 모음
    st.divider()
    st.write('**바로가기**')
    button_cols = st.columns([1, 1, 2])
    with button_cols[0]:
        st.link_button('대한민국 외교부 누리집', url='https://www.mofa.go.kr/', use_container_width=True)
    with button_cols[1]:
        st.link_button('외교부 독도 누리집', url='https://dokdo.mofa.go.kr/eng/', use_container_width=True)
    with button_cols[2]:
        st.download_button(label="Download Korea Info Book(Korean version).pdf",
                           data=open("./Home/data/대한민국 국가상징 홍보책자.pdf", "rb").read(),
                           file_name="Korea Info Book(Korean version).pdf",
                           mime='application/octet-stream', use_container_width=True)
    
    # 갤러리
    st.divider()
    st.write('**Gallery**')

    gallery_images = ['./Home/data/City of Korea.jpg', './Home/data/Korea_Flag.jpg', './Home/data/Samulnori.jpg',
                      'https://static.cdn.soomgo.com/upload/portfolio/ddbe5253-b25c-42e8-ba8f-a45415a87ac9.jpg?webp=1']
    gallery_captions = ['Night View of Seoul, Korea', 'Taegeukgi 태극기', '사물놀이', '캘리그라피']

    gallery_cols = st.columns(3)
    for i in range(3):
        with gallery_cols[i]:
            st.image(image=gallery_images[i], caption=gallery_captions[i])