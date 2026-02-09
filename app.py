# app.py
import streamlit as st
import random
import requests
import datetime
import pandas as pd
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
    st.markdown("---")
    st.caption("API 키는 로컬에서만 사용됩니다.")

# =========================
# 유틸 함수
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


def generate_report(
    habits: list,
    mood: int,
    weather: Optional[dict],
    pokemon: Optional[dict],
    coach_style: str,
    api_key: str
) -> str:
    if not api_key:
        return "❌ OpenAI API Key를 입력해주세요."

    system_prompts = {
        "스파르타 코치": "너는 매우 엄격하고 직설적인 코치다. 변명은 용납하지 않는다.",
        "따뜻한 멘토": "너는 공감 능력이 뛰어난 따뜻한 멘토다. 부드럽게 동기부여한다.",
        "게임 마스터": "너는 RPG 게임 마스터다. 퀘스트와 레벨업 개념으로 말한다."
    }

    weather_text = (
        f"{weather['city']}의 날씨는 {weather['desc']}, {weather['temp']}도"
        if weather else "날씨 정보 없음"
    )

    pokemon_text = (
        f"{pokemon['name']} (타입: {', '.join(pokemon['types'])}, 스탯: {pokemon['stats']})"
        if pokemon else "포켓몬 정보 없음"
    )

    user_prompt = f"""
오늘의 습관 달성: {habits}
기분 점수: {mood}/10
날씨: {weather_text}
파트너 포켓몬: {pokemon_text}

아래 형식으로 리포트를 작성해줘:
- 컨디션 등급 (S~D)
- 습관 분석
- 날씨 코멘트
- 내일 미션
- 오늘의 파트너 포켓몬 응원
"""

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "gpt-5-mini",
        "messages": [
            {"role": "system", "content": system_prompts[coach_style]},
            {"role": "user", "content": user_prompt}
        ]
    }

    try:
        res = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=10
        )
        res.raise_for_status()
        return res.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"❌ 리포트 생성 실패: {e}"

# =========================
# 습관 체크인 UI
# =========================
st.subheader("✅ 오늘의 습관 체크인")

habits = [
    ("⏰", "기상 미션"),
    ("💧", "물 마시기"),
    ("📚", "공부/독서"),
    ("🏃", "운동하기"),
    ("😴", "수면"),
]

cols = st.columns(2)
checked = []

for i, (emoji, name) in enumerate(habits):
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
# 달성률 + 차트
# =========================
achievement_rate = int(len(checked) / len(habits) * 100)

st.markdown("### 📊 오늘의 요약")
m1, m2, m3 = st.columns(3)
m1.metric("달성률", f"{achievement_rate}%")
m2.metric("달성 습관 수", f"{len(checked)}/5")
m3.metric("기분", f"{mood}/10")

sample_data = pd.DataFrame({
    "날짜": [
        (datetime.date.today() - datetime.timedelta(days=i)).strftime("%m/%d")
        for i in range(6, 0, -1)
    ],
    "달성률": [40, 60, 80, 50, 70, 90]
})

today_row = pd.DataFrame({
    "날짜": [datetime.date.today().strftime("%m/%d")],
    "달성률": [achievement_rate]
})

chart_df = pd.concat([sample_data, today_row], ignore_index=True)
st.bar_chart(chart_df.set_index("날짜"))

# =========================
# 결과 표시
# =========================
st.markdown("---")
if st.button("🧠 컨디션 리포트 생성"):
    weather = get_weather(city, weather_api_key)
    pokemon = get_pokemon()

    report = generate_report(
        checked, mood, weather, pokemon, coach_style, openai_api_key
    )

    c1, c2 = st.columns(2)

    with c1:
        st.subheader("🌦 날씨 카드")
        if weather:
            st.write(f"**{weather['city']}**")
            st.write(weather["desc"])
            st.write(f"{weather['temp']} ℃")
        else:
            st.warning("날씨 정보를 불러오지 못했습니다.")

    with c2:
        st.subheader("🧩 포켓몬 카드")
        if pokemon:
            st.image(pokemon["image"], use_column_width=True)
            st.write(f"**No.{pokemon['id']} {pokemon['name']}**")
            st.write("타입:", ", ".join(pokemon["types"]))

            stats_df = pd.DataFrame.from_dict(
                pokemon["stats"], orient="index", columns=["스탯"]
            )
            st.bar_chart(stats_df)
        else:
            st.warning("포켓몬 정보를 불러오지 못했습니다.")

    st.subheader("📜 AI 코치 리포트")
    st.write(report)

    share_text = f"""
🎮 AI 습관 트래커 리포트
달성률: {achievement_rate}%
기분: {mood}/10
도시: {city}
파트너 포켓몬: {pokemon['name'] if pokemon else '없음'}
"""
    st.subheader("📤 공유용 텍스트")
    st.code(share_text)

# =========================
# API 안내
# =========================
with st.expander("ℹ️ API 안내"):
    st.markdown("""
- **OpenAI API**: AI 코치 리포트 생성
- **OpenWeatherMap API**: 현재 날씨 정보
- **PokeAPI**: 1세대 랜덤 포켓몬 정보  
모든 API 키는 외부로 저장되지 않습니다.
""")
