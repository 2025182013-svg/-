# app.py
import streamlit as st
import requests
import random
from typing import Optional, Tuple

# -------------------------
# 기본 설정
# -------------------------
st.set_page_config(
    page_title="AI 습관 트래커",
    page_icon="📊",
    layout="wide"
)

st.title("📊 AI 습관 트래커")

# -------------------------
# 사이드바 - API Key 입력
# -------------------------
with st.sidebar:
    st.header("🔑 API 설정")
    openai_api_key = st.text_input("OpenAI API Key", type="password")
    weather_api_key = st.text_input("OpenWeatherMap API Key", type="password")
    st.caption("⚠️ 키는 브라우저에만 사용되며 저장되지 않습니다.")

# -------------------------
# 유틸 함수
# -------------------------
def get_weather(city: str, api_key: str) -> Optional[dict]:
    try:
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": f"{city},KR",  # 🔥 핵심 수정
            "appid": api_key,
            "units": "metric",
            "lang": "kr"
        }
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
        return {
            "temp": data["main"]["temp"],
            "desc": data["weather"][0]["description"]
        }
    except Exception as e:
        st.warning(f"🌧️ 날씨 API 오류: {e}")
        return None


def get_dog_image() -> Optional[Tuple[str, str]]:
    try:
        r = requests.get("https://dog.ceo/api/breeds/image/random", timeout=10)
        r.raise_for_status()
        data = r.json()
        img_url = data["message"]
        breed = img_url.split("/breeds/")[1].split("/")[0]
        return img_url, breed
    except Exception:
        return None


def generate_report(habits, mood, weather, dog_breed, style):
    from openai import OpenAI
    client = OpenAI(api_key=openai_api_key)

    system_prompts = {
        "스파르타 코치": "너는 엄격하고 직설적인 습관 코치다. 변명은 허용하지 않는다.",
        "따뜻한 멘토": "너는 공감과 응원을 잘하는 따뜻한 멘토다.",
        "게임 마스터": "너는 RPG 게임의 마스터다. 퀘스트와 레벨 개념으로 말한다."
    }

    user_prompt = f"""
오늘 체크한 습관: {", ".join(habits)}
기분 점수: {mood}/10
날씨: {weather}
강아지 품종: {dog_breed}

아래 형식으로만 출력:
- 컨디션 등급 (S~D)
- 습관 분석
- 날씨 코멘트
- 내일 미션
- 오늘의 한마디
"""

    res = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[
            {"role": "system", "content": system_prompts[style]},
            {"role": "user", "content": user_prompt}
        ]
    )
    return res.choices[0].message.content


# -------------------------
# Session State 초기화
# -------------------------
if "records" not in st.session_state:
    st.session_state.records = [random.randint(2, 5) for _ in range(6)]

# -------------------------
# 습관 체크인 UI
# -------------------------
st.subheader("✅ 오늘의 체크인")

habits = {
    "🌅 기상 미션": False,
    "💧 물 마시기": False,
    "📚 공부/독서": False,
    "🏃 운동하기": False,
    "😴 수면": False
}

col1, col2 = st.columns(2)
for i, habit in enumerate(habits.keys()):
    with col1 if i % 2 == 0 else col2:
        habits[habit] = st.checkbox(habit)

mood = st.slider("🙂 오늘 기분 점수", 1, 10, 5)

city = st.selectbox(
    "🌍 도시 선택",
    ["Seoul", "Busan", "Incheon", "Daegu", "Daejeon",
     "Gwangju", "Suwon", "Ulsan", "Jeju", "Changwon"]
)

style = st.radio(
    "🎭 코치 스타일",
    ["스파르타 코치", "따뜻한 멘토", "게임 마스터"],
    horizontal=True
)

# -------------------------
# 달성률 계산
# -------------------------
checked = [k for k, v in habits.items() if v]
achievement = int(len(checked) / 5 * 100)

# -------------------------
# 메트릭
# -------------------------
m1, m2, m3 = st.columns(3)
m1.metric("달성률", f"{achievement}%")
m2.metric("완료 습관", f"{len(checked)} / 5")
m3.metric("기분", f"{mood}/10")

# -------------------------
# 차트
# -------------------------
st.subheader("📈 7일 습관 달성 기록")

today_count = len(checked)
data = st.session_state.records + [today_count]
st.bar_chart(data)

# -------------------------
# AI 리포트 생성
# -------------------------
st.subheader("🤖 AI 코치 리포트")

if st.button("컨디션 리포트 생성"):
    weather = get_weather(city, weather_api_key) if weather_api_key else None
    dog = get_dog_image()

    weather_text = (
        f"{weather['temp']}°C, {weather['desc']}"
        if weather else "날씨 정보 없음"
    )

    dog_url, dog_breed = dog if dog else (None, "알 수 없음")

    if openai_api_key:
        report = generate_report(
            checked, mood, weather_text, dog_breed, style
        )
    else:
        report = "⚠️ OpenAI API Key를 입력하세요."

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("### 🌤️ 오늘의 날씨")
        st.write(weather_text)

    with c2:
        st.markdown("### 🐶 오늘의 강아지")
        if dog_url:
            st.image(dog_url, use_container_width=True)
            st.caption(f"품종: {dog_breed}")

    st.markdown("### 📋 AI 코치 리포트")
    st.write(report)

    share_text = f"""
📊 오늘의 AI 습관 리포트
- 달성률: {achievement}%
- 기분: {mood}/10
- 완료 습관: {", ".join(checked)}
"""
    st.code(share_text, language="text")

# -------------------------
# 하단 안내
# -------------------------
with st.expander("ℹ️ API 안내"):
    st.markdown("""
- **OpenAI API**: AI 코치 리포트 생성
- **OpenWeatherMap API**: 실시간 날씨 (섭씨, 한국어)
- **Dog CEO API**: 랜덤 강아지 이미지
""")
