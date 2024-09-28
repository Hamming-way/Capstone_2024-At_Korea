import streamlit as st
import time
from openai import OpenAI
from typing import List, Dict
from .prompt import common_name_prompt, special_name_prompt

# OpenAI API KEY
name_client = OpenAI(
    api_key=st.secrets['OPENAI_API_KEY']
)

# Reset name session
def init_session_state():
    if 'kname' not in st.session_state:
        st.session_state.kname = []
    if 'namemode' not in st.session_state:
        st.session_state.namemode = ''

# Get Response
def get_response(messages: List[Dict[str, str]]) -> str:
    try:
        response = name_client.chat.completions.create(
            model='gpt-4o-mini',
            messages=messages
        )
        return response.choices[0].message.content
    except Exception as e:
        return f'Sorry... Something Wrong... \n\n >>> {str(e)}'

# main
def show_name_generator():
    # session setting
    init_session_state()
    
    st.header('📢 Get your KOREAN NAME!')
    # mode setting
    with st.expander('Choose naming MODE'):
        N, S = st.columns([1, 1])
        with N:
            if st.button('I want COMMON names!', use_container_width=True):
                st.session_state.namemode = 'COMMON'
        with S:
            if st.button('I want SPECIAL names!', use_container_width=True):
                st.session_state.namemode = 'SPECIAL'

    # get user info
    with st.container(border=True):
        st.subheader(f'What is your name? You will get {st.session_state.namemode} names!!!')
        
        # get user name
        user_name = st.text_input(label='Name', placeholder='Put your name here.. FULL NAME may get better result!')
        if user_name:
            st.write(f'Hello, **{user_name}**!\nTell us more information for better result :)')
            # more info
            G, C = st.columns(2)
            with G:
                gender = st.radio('Gender', ['Male', 'Female'], horizontal=True, index=0)
            with C:
                country = st.text_input('Country', placeholder='Where are you from?', value=None)
        
            if st.button('Generate', use_container_width=True):
                st.session_state.kname = []
                # show given info
                st.info(f'{user_name},,, {gender},,, {country},,,{st.session_state.namemode},,,')

                # session control
                if st.session_state.namemode == 'COMMON':
                    st.session_state.kname.append({'role': 'system',
                                                   'content': common_name_prompt(user_name, gender, country)})
                else:
                    st.session_state.kname.append({'role': 'system',
                                                   'content': special_name_prompt(user_name, gender, country)})
                st.session_state.kname.append({'role': 'user', 'content': 'Make me Korean Style Names!'})

                name_result = get_response(st.session_state.kname)
                
                # UI
                on_time = 0
                gen_bar = st.progress(on_time, text='Loading..')
                for t in range(30):
                    time.sleep(0.1)
                    on_time += 1
                    gen_bar.progress(on_time, text='Generating...')
                for t in range(40):
                    time.sleep(0.05)
                    on_time += 1
                    gen_bar.progress(on_time, text='Making results...')
                for t in range(10):
                    time.sleep(0.3)
                    on_time += 1
                    gen_bar.progress(on_time, text='Almost done...')
                time.sleep(2)
                gen_bar.progress(100, text='Done!')
                time.sleep(1)
                gen_bar.empty()

                with st.container(border=True):
                    st.info(name_result)