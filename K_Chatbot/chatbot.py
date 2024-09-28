import streamlit as st
from openai import OpenAI
from typing import List, Dict
from .prompt import basic_prompt, travel_prompt, fun_fact_prompt

# Set up OpenAI API KEY
chatbot_client = OpenAI(
    api_key=st.secrets['OPENAI_API_KEY']
)

# Reset session
def init_session_state():
    '''
    # 'messages' : 일반 대화 세션
    # 'tmessages' : 여행 대화 세션
    # 'funfact' : 펀팩트 세션
    # 'promptmode' : 프롬프트 모드 세션
    '''
    if 'messages' not in st.session_state:
        st.session_state.messages = [{'role': 'system', 'content': basic_prompt()}]
    if 'tmessages' not in st.session_state:
        st.session_state.tmessages = [{'role': 'system', 'content': travel_prompt(20, 'Male', 500, 3, '', '')}]
    if 'funfact' not in st.session_state:
        st.session_state.funfact = []
    if 'promptmode' not in st.session_state:
        st.session_state.promptmode = 'normal'

# previous chat
def prev_messages(msg_mode):
    '''
    # 세션에 messages가 있고 값이 있다면
    # system 메세지 제외하고 메세지를 출력할 것임
    # 전체 길이에서 1을 뺀 값 == 마지막 값
    # 마지막 값만 success로 출력
    '''
    msgs = 'tmessages' if msg_mode == 'travel' else 'messages'
    a = 0
    if msgs in st.session_state and len(st.session_state[msgs]) > 1:
        for message in st.session_state[msgs][1:]:
            a += 1
            if a != len(st.session_state[msgs])-1:
                st.chat_message(message['role']).write(message['content'])
            else:
                st.chat_message(message['role']).success(message['content'])

# Get Response
def get_response(mssgs: List[Dict[str, str]]) -> str:
    try:
        response = chatbot_client.chat.completions.create(
            model='gpt-4o-mini',
            messages=mssgs
        )
        return response.choices[0].message.content
    except Exception as e:
        return f'Sorry... Something Wrong... \n\n >>> {str(e)}'
    
# User 입력 및 AI 응답
def chat_box(user_input):
    msg_mode = 'tmessages' if st.session_state.promptmode == 'travel' else 'messages'
    st.chat_message('user').write(user_input)
    st.session_state[msg_mode].append({'role':'user', 'content':user_input})
    with st.chat_message('assistant'):
        with st.spinner('Let me see...'):
            ai_response = get_response(st.session_state[msg_mode])
            st.session_state[msg_mode].append({'role':'assistant', 'content':ai_response})
            st.rerun()  # 다시 실행해서 대화 표시 -> 가장 최근 답변 success

def fun_fact_kor():
    st.session_state.funfact.append({'role': 'system',
                                     'content': fun_fact_prompt()})
    st.session_state.funfact.append({'role': 'user',
                                     'content': 'Tell me Fun Fact of Korea!'})
    with st.spinner("What's new~~?"):
        fun_fact = get_response(st.session_state.funfact)
    return fun_fact

# main 함수
def show_chatbot():
    # session setting
    init_session_state()

    st.title('🤖 Kobot')

    col1, col2 = st.columns([5, 2])

    # 채팅창
    with col1:
        # 채팅 메시지를 표시할 컨테이너
        chat_container = st.container(border=True, height=535)
        Q, W = st.columns([5, 1])
        with Q:
            user_input = st.chat_input('Say something here...')
        with W:
            if st.button('Reset', use_container_width=True, type='primary'):
                if st.session_state.promptmode == 'travel':
                    reset_msgs = 'tmessages'
                    reset_prompt = travel_prompt(20, 'Male', 500, 3, '', '')
                else:
                    reset_msgs = 'messages'
                    reset_prompt = basic_prompt()
                st.session_state[reset_msgs] = [{'role': 'system', 'content': reset_prompt}]
    
    with col2:
        travel_mode = st.toggle('Travel Planning Mode')
        if travel_mode:
            st.session_state.promptmode = 'travel'
        else:
            st.session_state.promptmode = 'normal'

    with col1:
        with chat_container:
            st.warning(st.session_state.promptmode)
            if travel_mode:
                prev_messages(st.session_state.promptmode)
                if user_input:
                    chat_box(user_input)
            else:
                prev_messages(st.session_state.promptmode)
                if user_input:
                    chat_box(user_input)
    
    with col2:
        if travel_mode:
            with st.container(border=True):
                # Get info
                st.write('More information for better plans!')
                A, G = st.columns(2)
                B, D = st.columns(2)
                with A:
                    st.number_input('Age', value=20, key='age')
                with G:
                    st.radio('Gender', ['Male', 'Female'], index=0, key='gender')
                with B:
                    st.slider('Budget($)', value=500, max_value=1000, step=10, key='budget')
                with D:
                    st.slider('Stay for...(days)', value=3, max_value=30, key='days')
                st.text_input('Which cities do you wanna visit?',
                              placeholder='e.g. Seoul, Busan, Jeju, Gangnam, Suwon...', value=None, key='cities')
                st.text_area('Tell more!', value=None, key='etc',
                             placeholder='Put your additional needs! I can only make a plan to Korea!')
            M, N = st.columns(2)
            with M:
                if st.button('Start!', use_container_width=True):
                    prompt = travel_prompt(st.session_state.age, st.session_state.gender,
                                           st.session_state.budget, st.session_state.days,
                                           st.session_state.cities, st.session_state.etc)
                    st.session_state.tmessages = [
                        {'role': 'system', 'content': prompt},
                        {'role': 'user',
                         'content': 'Based on the information I provided, can you suggest a detailed travel itinerary for me?'}
                    ]
                    with N:
                        with st.spinner('Generating..'):
                            travel_result = get_response(st.session_state.tmessages)
                            st.session_state.tmessages.append({'role': 'assistant', 'content': travel_result})
                    with col1:
                        with chat_container:
                            prev_messages(st.session_state.promptmode)                
    
    # Fun Fact 기능 구현
    button_area, response_area = st.columns([2, 8])
    with button_area:
        if st.button('Fun Fact:smile:', use_container_width=True, key='ff'):
            with response_area:
                st.info(fun_fact_kor())