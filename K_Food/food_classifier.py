import streamlit as st
import time
import torch
import torch.nn as nn
from torchvision import transforms, models
from PIL import Image
from openai import OpenAI
from typing import List, Dict
from .prompt import base_prompt

# OpenAI API KEY
food_client = OpenAI(
    api_key=st.secrets['OPENAI_API_KEY']
)

# Get Info
def get_info(messages: List[Dict[str, str]]) -> str:
    try:
        response = food_client.chat.completions.create(
            model='gpt-4o-mini',
            messages=messages
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Sorry... Something Wrong... \n\n >>> {str(e)}"

# 모델 로드 함수
# @st.cache_resource
def load_model():
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = models.efficientnet_b4(weights=None).to(device)
    model.classifier = nn.Sequential(
        nn.Linear(1792, 512),
        nn.SiLU(),
        nn.Dropout(0.5),
        nn.Linear(512, 150)
    ).to(device)
    model.load_state_dict(torch.load('./K_Food/models/model_2_weights.pth', map_location=torch.device('cpu')))
    model.eval()
    return model

# 이미지 전처리 함수
def transform_image(image):
    my_transforms = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
    ])
    return my_transforms(image).unsqueeze(0)

# 클래스 이름 로드
@st.cache_resource
def get_class_names():
    with open('./K_Food/class_name/class_names.txt', 'r', encoding='utf-8') as f:
        class_names = [line.strip() for line in f.readlines()]
    return class_names

# 상위 3개 예측 함수
def get_top_predictions(image, model, class_names, topk=3):
    # 이미지 전처리
    tensor = transform_image(image)

    # 추론 모드로 모델 사용
    model.eval()
    with torch.no_grad():
        outputs = model(tensor)
        probabilities = nn.functional.softmax(outputs, dim=1)  # 확률로 변환

        # 상위 k개 클래스를 가져옴
        top_probabilities, top_classes = probabilities.topk(topk, dim=1)

    # 각 클래스의 인덱스와 확률을 매핑하여 반환
    top_probabilities = top_probabilities.cpu().numpy()[0]  # 상위 확률
    top_classes = top_classes.cpu().numpy()[0]  # 상위 클래스 인덱스

    top_predictions = []
    for i in range(topk):
        class_idx = top_classes[i]
        class_name = class_names[class_idx]
        probability = top_probabilities[i]
        top_predictions.append((class_name, probability))

    return top_predictions

# main 함수
def show_food_classifier():
    st.title('🥄 Find K-Food')

    # 모델 로드, 세션 설정
    model = load_model()
    if 'fmessages' not in st.session_state:
        st.session_state.fmessages = [{"role": "system", "content": base_prompt()}]

    # 클래스 이름 로드
    class_names = get_class_names()
    
    with st.container(border=True, height=300):
        U, I = st.columns([2, 1])
        with U:
            st.write('Upload your food image below.')
            uploaded_file = st.file_uploader(label='Pic', label_visibility='collapsed', type=["jpg", "jpeg", "png"])
        with I:
            if uploaded_file is not None:
                image = Image.open(uploaded_file).convert('RGB').rotate(270)
                st.image(image, caption='Uploaded Image', use_column_width=True)

    # 분석
    analyze = st.button("Analyze", key='analyze', use_container_width=True)
    result = []
    if uploaded_file is not None:
        try:
            if analyze:
                # 상위 3개 예측 결과
                top_predictions = get_top_predictions(image, model, class_names, topk=3)

                st.write('### This food might be:')
                
                progress_text = "Operation in progress. Please wait."
                status_bar = st.progress(0, text=progress_text)

                col = st.columns(3)
                for i, (class_name, probability) in enumerate(top_predictions):
                    status_bar.progress(15*(i+1), text=progress_text)
                    result.append({'rank':i+1, 'food':class_name})
                    with col[i]:
                        with st.expander(f'{i}. **{class_name}** ({probability * 100:.2f}%)'):
                            st.session_state.fmessages.append({'role':'user', 'content':class_name})
                            food_info = get_info(st.session_state.fmessages)
                            st.write(food_info)
                    status_bar.progress(30*(i+1), text=progress_text)
                time.sleep(.5)
                status_bar.progress(100, text=progress_text)
                time.sleep(.5)
                status_bar.empty()
        except Exception as e:
            st.error('Error while analyzing')
            st.error(e)
    else:
        st.toast('Please upload an image.', icon='🔥')