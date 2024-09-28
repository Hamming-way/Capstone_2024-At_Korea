import streamlit as st
import time
from pymongo.mongo_client import MongoClient

# MongoDB Cloud
id = st.secrets['MONGO_ID']
pw = st.secrets['MONGO_PW']
uri = f"mongodb+srv://{id}:{pw}@board.dasem.mongodb.net/?retryWrites=true&w=majority&appName=Board"
client = MongoClient(uri)
database = client.get_database('Capstone_2024_2')
collection = database.get_collection('posts')
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

# DB 불러오기 - 게시글 리스트 및 총 게시글 수
def get_db():
    posts = collection.find({})
    tot_cnt = collection.count_documents({})
    notice_posts = collection.find({'user':'admin'})
    notice_cnt = collection.count_documents({'user':'admin'})
    
    return posts, tot_cnt, notice_posts, notice_cnt

# 게시글 리스트
def post_list(post, user):
    title = post['title']
    with st.expander(f':blue-background[{title}] | {user}'):
        st.write(post['content'])
        A, E, D = st.columns([5, 1, 1])
        with E:
            if st.button('Edit', key=f'edit{post}', use_container_width=True):
                edit_post(post)
        with D:
            if st.button('Delete', key=f'delete{post}', use_container_width=True, type='primary'):
                delete_post(post)

# 게시글 작성
@st.dialog('Post')
def insert_db(tot_cnt):
    title = st.text_input('Title')
    content = st.text_area('Content')
    user = st.text_input('User ID', value=f'anonymous{tot_cnt+1}')
    pw = st.text_input('Password', type='password')
    if st.button('Submit', key='post_submit'):
        query = {'title': title,
                 'content': content,
                 'user': user,
                 'password': pw}
        with st.spinner('Posting...'):
            collection.insert_one(query)
            time.sleep(2)
            st.success('Completely Posted!')
            time.sleep(1)
        st.rerun()

# 게시글 수정
@st.dialog('Edit')
def edit_post(post):
    id = post['_id']
    old_pw = post['password']

    title = st.text_input('Title', value=post['title'])
    content = st.text_area('Content', value=post['content'])
    user = st.text_input('User ID', value=post['user'], disabled=True)
    pw = st.text_input('Put your password to save', type='password')
    
    if st.button('Save', key='edit_save'):
        if pw == old_pw:
            query = {'title': title,
                    'content': content,
                    'user': user,
                    'password': pw}
            with st.spinner('Saving....'):
                collection.update_one({'_id':id}, {'$set': query})
                time.sleep(2)
                st.success('Completely Updated!')
                time.sleep(1)
            st.rerun()
        else:
            st.error('Wrong Password!! You cannot edit it.')

# 게시글 삭제
@st.dialog('Delete')
def delete_post(post):
    id = post['_id']
    old_pw = post['password']

    st.info('''
            Are you sure to remove this post? It cannot be recovered.\n
            Type DELETE and password to make sure.
            ''')
    del_post = st.text_input("Write 'DELETE'", placeholder='DELETE')
    pw = st.text_input('Put your password.', placeholder='password', key=f'pw_check{post}')

    del_check = True if del_post == 'DELETE' else False
    pw_check = True if pw == old_pw else False

    if st.button('Delete', key='delete'):
        if del_check and pw_check:
            with st.spinner('Progressing...'):
                collection.delete_one({'_id':id})
                time.sleep(2)
                st.error('Compeletly Deleted!')
                time.sleep(1)
            st.rerun()
        else:
            st.error('Something Wrong..Try Again...')

# main
def show_board():
    # DB 호출
    posts, tot_cnt, _, _ = get_db()

    # 검색창 및 글작성
    with st.container(border=True):
        M, F, P = st.columns([2, 3, 1])
        with M:
            st.subheader('Bulletin board')
        with F:
            S, K, B = st.columns([2, 3, 2])
            with S:
                standard = st.selectbox(label='a', label_visibility='collapsed', options=['title', 'content', 'user'])
            with K:
                keyword = st.text_input(label='a', label_visibility='collapsed', placeholder='Find..')
            with B:
                if st.button('Search', use_container_width=True) and keyword:
                    posts = collection.find({standard:{'$regex':keyword}})
                    tot_cnt = collection.count_documents({standard:{'$regex':keyword}})
        with P:
            if st.button('Post', use_container_width=True, type='primary'):
                insert_db(tot_cnt)

    # 공지사항 및 유저 게시판 구분
    tabs = st.tabs(['Notice', 'User Community'])
    # 공지사항
    with tabs[0]:
        if tot_cnt > 0:
            for i in range(tot_cnt):
                post = posts[i]
                user = post['user']
                if user == 'admin':
                    post_list(post, user)
    
    # 유저 게시판
    with tabs[1]:
        if tot_cnt > 0:
            for i in range(tot_cnt):
                post = posts[i]
                user = post['user']
                if user != 'admin':
                    post_list(post, user)