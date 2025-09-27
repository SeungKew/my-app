import streamlit as st

st.title("내 첫 Streamlit 앱!")
st.write("안녕하세요! 이 앱은 GitHub에 배포되었습니다.")

name = st.text_input("이름을 입력하세요:")
if name:
    st.write(f"반갑습니다, {name}님!")


