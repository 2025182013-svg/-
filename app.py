# app.py
import streamlit as st
import random
import requests
import datetime
import calendar

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

if "checked" not in st.session_state:
    st.session_state.checked = set()

if "today_pokemon" not in st.session_state:
    st.session_state.today_pokemon = None

# =========================
# 사이드바
# =========================
with st.sidebar:
    st.header("✏️ 습관 관리")

    new_habit = st.text_input("새 습관 추가")
    if st.button("➕ 추가") and new_habit:
        st.session_state.habits.append(new_habit)
        st.experimental_rerun()

    st.markdown("---")
    st.caption("습관은 달력의 오늘 칸에서 체크됩니다")

# =========================
# 오늘 상태
# =========================
mood = st.slider("😊 오늘 기분", 1, 10, 5)

rate = int(
    len(st.session_state.checked)
    / max(len(st.session_state.habits), 1)
    * 100
)

# =========================
# 포켓몬 생성 버튼
# =========================
if st.button("🎮 오늘의 포켓몬 생성"):
    try:
        pid = random.randint(1, 151)
        r = requests.get(f"https://pokeapi.co/api/v2/pokemon/{pid}", timeout=10)
        d = r.json()
        st.session_state.today_pokemon = {
            "name": d["name"].capitalize(),
            "image": d["sprites"]["other"]["official-artwork"]["front_default"]
        }
    except:
        st.session_state.today_pokemon = None

# =========================
# 📅 달력 UI (메인)
# =========================
st.markdown("## 🗓️ 이번 달 습관 달력")

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
                continue

            # 📅 날짜
            st.markdown(f"### {day.day}")

            # 👉 오늘만 상세 표시
            if day == today:
                st.markdown(f"📊 **달성률 {rate}%**  |  😊 {mood}")

                # 🧩 포켓몬
                if st.session_state.today_pokemon:
                    st.image(
                        st.session_state.today_pokemon["image"],
                        width=80
                    )
                    st.caption(
                        f"파트너: {st.session_state.today_pokemon['name']}"
                    )

                # ✅ 습관 체크리스트 (달력 안!)
                for h in st.session_state.habits:
                    checked = h in st.session_state.checked
                    label = f"~~{h}~~" if checked else h

                    if st.checkbox(
                        label,
                        value=checked,
                        key=f"{day}_{h}"
                    ):
                        st.session_state.checked.add(h)
                    else:
                        st.session_state.checked.discard(h)

            else:
                # 다른 날짜는 요약만
                st.caption("기록 없음")

# =========================
# 안내
# =========================
st.markdown("---")
st.caption("🎮 달력의 오늘 칸이 당신의 하루 대시보드입니다")
