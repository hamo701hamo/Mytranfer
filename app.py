import os

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


def get_setting(name, default=None):
    # Streamlit Cloud의 Secrets를 먼저 확인하고, 없으면 .env(환경변수)를 사용
    try:
        if name in st.secrets:
            return st.secrets[name]
    except FileNotFoundError:
        pass
    return os.getenv(name, default)


MODEL = get_setting("OPENAI_MODEL", "gpt-4o-mini")

LANGUAGES = {
    "영어 (English)": "English",
    "일본어 (日本語)": "Japanese",
    "베트남어 (Tiếng Việt)": "Vietnamese",
    "러시아어 (Русский)": "Russian",
}


@st.cache_resource
def create_client(api_key):
    return OpenAI(api_key=api_key)


def get_client():
    api_key = get_setting("OPENAI_API_KEY")
    if not api_key:
        return None
    return create_client(api_key)


def translate(client, text, target_language):
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    f"You are a professional translator. Translate the user's text into {target_language}. "
                    "Output only the translation, without explanations or quotation marks. "
                    "Preserve the original meaning, tone, and line breaks."
                ),
            },
            {"role": "user", "content": text},
        ],
        temperature=0.3,
    )
    return response.choices[0].message.content.strip()


st.set_page_config(page_title="번역기", page_icon="🌐")
st.title("🌐 간단 번역기")
st.caption(f"OpenAI `{MODEL}` 모델을 사용합니다.")

client = get_client()
if client is None:
    st.error("OPENAI_API_KEY가 설정되어 있지 않습니다. (.env 파일 또는 Streamlit Secrets)")
    st.stop()

text = st.text_area("번역할 글을 입력하세요", height=200)
language_label = st.radio("번역할 언어", list(LANGUAGES.keys()), horizontal=True)

if st.button("번역하기", type="primary"):
    if not text.strip():
        st.warning("번역할 글을 입력해주세요.")
    else:
        with st.spinner("번역 중..."):
            try:
                result = translate(client, text, LANGUAGES[language_label])
            except Exception as e:
                st.error(f"번역 중 오류가 발생했습니다: {e}")
            else:
                st.subheader(f"번역 결과 — {language_label}")
                st.code(result, language=None, wrap_lines=True)
