import streamlit as st
from streamlit_option_menu import option_menu
from Home.home import show_home
from K_Food.food_classifier import show_food_classifier
from K_Name.name_generator import show_name_generator
from K_Tour.tourism_map import show_tourism_map
from K_Chatbot.chatbot import show_chatbot
from Bulletin_Board.board import show_board

def main():
    st.set_page_config(page_title="At Korea", layout="wide", page_icon="🇰🇷")

    with st.sidebar:
        # st.title("Enjoy Korea")
        selected = option_menu(
            menu_title="At Korea",
            menu_icon="threads-fill",
            options=["Home", "Find K-Food", "Where to Visit?!", "Get your KOREAN NAME!", "Chatbot", "Bulletin Board"],
            icons=["house", "search", "map", "alphabet", "robot", "person"],
            default_index=0
        )

    if selected == "Home":
        show_home()
    elif selected == "Find K-Food":
        show_food_classifier()
    elif selected == "Where to Visit?!":
        show_tourism_map()
    elif selected == "Get your KOREAN NAME!":
        show_name_generator()
    elif selected == "Chatbot":
        show_chatbot()
    elif selected == "Bulletin Board":
        show_board()

if __name__ == "__main__":
    main()