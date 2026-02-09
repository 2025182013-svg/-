# app.py
import streamlit as st
import random
import requests
import datetime
import pandas as pd
import calendar
from typing import Optional

# =========================
# 기본 설정
# =========================
st.set_page_config(
    page_title="AI 습관 트래커 (포켓몬)",
    page_icon="🎮",
    layout="wide"
)

st.title("🎮 AI 습관 트래커 (포켓몬 에디션)")

# =========================
# 사이드바 - API 키
# =========================
with st.sidebar:
    st.header("🔑 API 설정")
    openai_api_key = st.text_input("OpenAI API Key", type="password")
    weather_api_key = st.text_input("OpenWeatherMap API Key", type="password")
    st.caption("API 키는 외부에 저장되지 않습니다.")

# =========================
# API 함수
# =========================
def get_weather(city: str, api_key: str) -> Optional[dict]:
    if not api_key:
        return None
    try:
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": city,
            "appid": api_key,
            "units": "metric",
            "lang": "kr"
        }
        res = requests.get(url, params=params, timeout=10)
        res.raise_for_status()
        data = res.json()
        return {
            "city": city,
            "temp": data["main"]["temp"],
            "desc": data["weather"][0]["description"]
        }
    except Exception:
        return None


def get_pokemon() -> Optional[dict]:
    try:
        poke_id = random.randint(1, 151)
        url = f"https://pokeapi.co/api/v2/pokemon/{poke_id}"
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        data = res.json()

        stats = {s["stat"]["name"]: s["base_stat"] for s in data["stats"]}

        return {
            "id": poke_id,
            "name": data["name"].capitalize(),
            "types": [t["type"]["name"] for t in data["types"]],
            "image": data["sprites"]["other"]["official-artwork"]["front_default"],
            "stats": {
                "HP": stats.get("hp", 0),
                "공격": stats.get("attack", 0),
                "방어": stats.get("defense", 0),
                "특수공격": stats.get("special-attack", 0),
                "특수방어": stats.get("special-defense", 0),
                "스피드": stats.get("speed", 0),
            }
        }
    except Exception:
        return None


def generate_report(habits, mood, weather, pokemon, style, api_key):
    if not api_key:
        return "❌ OpenAI API Key를 입력해주세요."

    system_prompt = {
        "스파르타 코치": "너는 매우 엄격한 코치다. 직설적으로 말한다.",
        "따뜻한 멘토": "너는 따뜻하고 공감하는 멘토다.",
        "게임 마스터": "너는 RPG 게임 마스터다. 퀘스트처럼 말한다."
    }

    weather_text = f"{weather['city']} {weather['desc']} {weather['temp']}℃" if weather else "날씨 정보 없음"
    pokemon_text = f"{pokemon['name']} ({pokemon['types']}, {pokemon['stats']})" if pokemon else "포켓몬 없음"

    prompt = f"""
오늘 습관 달성: {habits}
기분 점수: {mood}/10
날씨: {weather_text}
포켓몬: {pokemon_text}

형식:
- 컨디션 등급(S~D)
- 습관 분석
- 날씨 코멘트
- 내일 미션
- 포켓몬 응원
"""

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    body = {
        "model": "gpt-5-mini",
        "messages": [
            {"role": "system", "content": system_prompt[style]},
            {"role": "user", "content": prompt}
        ]
    }

    try:
        r = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=body,
            timeout=10
        )
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"❌ 리포트 생성 실패: {e}"

# =========================
# 습관 체크인 UI
# =========================
st.subheader("✅ 오늘의 습관 체크인")

habits_list = [
    ("⏰", "기상 미션"),
    ("💧", "물 마시기"),
    ("📚", "공부/독서"),
    ("🏃", "운동하기"),
    ("😴", "수면"),
]

cols = st.columns(2)
checked = []

for i, (emoji, name) in enumerate(habits_list):
    with cols[i % 2]:
        if st.checkbox(f"{emoji} {name}"):
            checked.append(name)

mood = st.slider("😊 오늘 기분 점수", 1, 10, 5)

city = st.selectbox(
    "🌍 도시 선택",
    ["Seoul", "Busan", "Incheon", "Daegu", "Daejeon",
     "Gwangju", "Suwon", "Ulsan", "Jeju", "Sejong"]
)

coach_style = st.radio(
    "🎤 코치 스타일",
    ["스파르타 코치", "따뜻한 멘토", "게임 마스터"]
)

# =========================
# 요약 카드
# =========================
achievement_rate = int(len(checked) / 5 * 100)

m1, m2, m3 = st.columns(3)
m1.metric("달성률", f"{achievement_rate}%")
m2.metric("달성 습관", f"{len(checked)}/5")
m3.metric("기분", f"{mood}/10")

# =========================
# 📅 달력 UI
# =========================
st.markdown("### 🗓️ 이번 달 습관 달력")

today = datetime.date.today()
year, month = today.year, today.month

sample_history = {
    today - datetime.timedelta(days=6): (2, 6),
    today - datetime.timedelta(days=5): (3, 7),
    today - datetime.timedelta(days=4): (4, 8),
    today - datetime.timedelta(days=3): (2, 5),
    today - datetime.timedelta(days=2): (3, 6),
    today - datetime.timedelta(days=1): (4, 9),
    today: (len(checked), mood)
}

weekdays = ["월", "화", "수", "목", "금", "토", "일"]
header = st.columns(7)
for i, d in enumerate(weekdays):
    header[i].markdown(f"**{d}**")

cal = calendar.Calendar(firstweekday=0)

for week in cal.monthdatescalendar(year, month):
    cols = st.columns(7)
    for i, day in enumerate(week):
        with cols[i]:
            if day.month != month:
                st.markdown(" ")
            else:
                habits_done, mood_score = sample_history.get(day, (0, 0))
                rate = int(habits_done / 5 * 100) if habits_done else 0

                color = "🟩" if rate >= 80 else "🟨" if rate >= 40 else "🟥"
                highlight = "border:2px solid #ff4b4b;" if day == today else ""

                st.markdown(
                    f"""
                    <div style="
                        border-radius:12px;
                        padding:8px;
                        text-align:center;
                        background:#f8f9fa;
                        {highlight}
                    ">
                        <b>{day.day}</b><br>
                        {color} {rate}%<br>
                        😊 {mood_score}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

# =========================
# 결과 영역
# =========================
st.markdown("---")
if st.button("🧠 컨디션 리포트 생성"):
    weather = get_weather(city, weather_api_key)
    pokemon = get_pokemon()
    report = generate_report(checked, mood, weather, pokemon, coach_style, openai_api_key)

    c1, c2 = st.columns(2)

    with c1:
        st.subheader("🌦 날씨 카드")
        if weather:
            st.write(f"{weather['city']} | {weather['desc']} | {weather['temp']}℃")
        else:
            st.warning("날씨 정보 없음")

    with c2:
        st.subheader("🧩 포켓몬 카드")
        if pokemon:
            st.image(pokemon["image"], use_column_width=True)
            st.write(f"No.{pokemon['id']} {pokemon['name']}")
            st.write("타입:", ", ".join(pokemon["types"]))
            st.bar_chart(pd.DataFrame.from_dict(pokemon["stats"], orient="index"))
        else:
            st.warning("포켓몬 정보 없음")

    st.subheader("📜 AI 코치 리포트")
    st.write(report)

    st.subheader("📤 공유용 텍스트")
    st.code(
        f"🎮 오늘 달성률 {achievement_rate}% | 기분 {mood}/10 | 포켓몬 {pokemon['name'] if pokemon else '없음'}"
    )

# =========================
# 안내
# =========================
with st.expander("ℹ️ API 안내"):
    st.markdown("""
- OpenAI API: AI 코치 리포트
- OpenWeatherMap API: 날씨
- PokeAPI: 포켓몬 정보
""")
