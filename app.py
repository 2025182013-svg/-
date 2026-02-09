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
# 세션 상태 초기화
# =========================
if "habits" not in st.session_state:
    st.session_state.habits = [
        "⏰ 기상 미션",
        "💧 물 마시기",
        "📚 공부/독서",
        "🏃 운동하기",
        "😴 수면"
    ]

if "checked_habits" not in st.session_state:
    st.session_state.checked_habits = set()

if "today_pokemon" not in st.session_state:
    st.session_state.today_pokemon = None

# =========================
# 사이드바 - API 키
# =========================
with st.sidebar:
    st.header("🔑 API 설정")
    openai_api_key = st.text_input("OpenAI API Key", type="password")
    weather_api_key = st.text_input("OpenWeatherMap API Key", type="password")

# =========================
# API 함수
# =========================
def get_weather(city, api_key):
    if not api_key:
        return None
    try:
        r = requests.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params={"q": city, "appid": api_key, "units": "metric", "lang": "kr"},
            timeout=10
        )
        r.raise_for_status()
        d = r.json()
        return {
            "city": city,
            "temp": d["main"]["temp"],
            "desc": d["weather"][0]["description"]
        }
    except:
        return None


def get_pokemon():
    try:
        pid = random.randint(1, 151)
        r = requests.get(f"https://pokeapi.co/api/v2/pokemon/{pid}", timeout=10)
        r.raise_for_status()
        d = r.json()
        return {
            "id": pid,
            "name": d["name"].capitalize(),
            "image": d["sprites"]["other"]["official-artwork"]["front_default"],
            "types": [t["type"]["name"] for t in d["types"]],
            "stats": {s["stat"]["name"]: s["base_stat"] for s in d["stats"]}
        }
    except:
        return None

# =========================
# 습관 관리 UI
# =========================
st.subheader("✏️ 습관 관리")

new_habit = st.text_input("새 습관 추가")
if st.button("➕ 추가") and new_habit:
    st.session_state.habits.append(new_habit)
    st.experimental_rerun()

for i, h in enumerate(st.session_state.habits):
    cols = st.columns([6, 1])
    with cols[0]:
        checked = h in st.session_state.checked_habits
        label = f"~~{h}~~" if checked else h
        if st.checkbox(label, value=checked, key=f"habit_{i}"):
            st.session_state.checked_habits.add(h)
        else:
            st.session_state.checked_habits.discard(h)
    with cols[1]:
        if st.button("❌", key=f"del_{i}"):
            st.session_state.habits.pop(i)
            st.session_state.checked_habits.discard(h)
            st.experimental_rerun()

# =========================
# 오늘 상태
# =========================
mood = st.slider("😊 오늘 기분", 1, 10, 5)
city = st.selectbox("🌍 도시", ["Seoul", "Busan", "Incheon", "Daegu", "Jeju"])

rate = int(len(st.session_state.checked_habits) / max(len(st.session_state.habits), 1) * 100)

st.metric("오늘 달성률", f"{rate}%")

# =========================
# 달력 UI
# =========================
st.markdown("### 🗓️ 이번 달 습관 달력")

today = datetime.date.today()
year, month = today.year, today.month
cal = calendar.Calendar(firstweekday=0)

weekdays = ["월", "화", "수", "목", "금", "토", "일"]
cols = st.columns(7)
for i, d in enumerate(weekdays):
    cols[i].markdown(f"**{d}**")

for week in cal.monthdatescalendar(year, month):
    cols = st.columns(7)
    for i, day in enumerate(week):
        with cols[i]:
            if day.month != month:
                st.write("")
            else:
                st.markdown(f"**{day.day}**")
                if day == today:
                    st.markdown(f"📊 {rate}%  😊 {mood}")
                    if st.session_state.today_pokemon:
                        st.image(st.session_state.today_pokemon["image"], width=60)

# =========================
# 결과 생성
# =========================
st.markdown("---")
if st.button("🎮 오늘의 포켓몬 & 리포트 생성"):
    pokemon = get_pokemon()
    st.session_state.today_pokemon = pokemon

    weather = get_weather(city, weather_api_key)

    st.subheader("🧩 오늘의 파트너 포켓몬")
    if pokemon:
        st.image(pokemon["image"], width=200)
        st.write(f"No.{pokemon['id']} {pokemon['name']}")
        st.write("타입:", ", ".join(pokemon["types"]))
        st.bar_chart(pd.DataFrame.from_dict(pokemon["stats"], orient="index"))

    st.subheader("🌦 날씨")
    if weather:
        st.write(f"{weather['city']} | {weather['desc']} | {weather['temp']}℃")
