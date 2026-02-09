# app.py
import streamlit as st
import random
import requests
import datetime
import calendar
import uuid

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
        {"id": str(uuid.uuid4()), "name": "⏰ 기상 미션"},
        {"id": str(uuid.uuid4()), "name": "💧 물 마시기"},
        {"id": str(uuid.uuid4()), "name": "📚 공부/독서"},
        {"id": str(uuid.uuid4()), "name": "🏃 운동하기"},
        {"id": str(uuid.uuid4()), "name": "😴 수면"},
    ]

if "checked" not in st.session_state:
    st.session_state.checked = set()  # habit_id 저장

if "today_pokemon" not in st.session_state:
    st.session_state.today_pokemon = None

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
# 오늘의 포켓몬 생성
# =========================
if st.button("🎮 오늘의 포켓몬 생성"):
    try:
        pid = random.randint(1, 151)
        r = requests.get(f"https://pokeapi.co/api/v2/pokemon/{pid}", timeout=10)
        r.raise_for_status()
        d = r.json()
        st.session_state.today_pokemon = {
            "name": d["name"].capitalize(),
            "image": d["sprites"]["other"]["official-artwork"]["front_default"]
        }
    except:
        st.session_state.today_pokemon = None

# =========================
# 📅 달력 UI
# =========================
st.markdown("## 🗓️ 이번 달 습관 달력")

today = datetime.date.today()
year, month = today.year, today.month
cal = calendar.Calendar(firstweekday=0)

weekdays = ["월", "화", "수", "목", "금", "토", "일"]
header = st.columns(7)
for i, d in enumerate(weekdays):
    header[i].markdown(f"**{d}**")

for week in cal.monthdatescalendar(year, month):
    cols = st.columns(7)
    for i, day in enumerate(week):
        with cols[i]:
            if day.month != month:
                st.write("")
                continue

            st.markdown(f"### {day.day}")

            # =========================
            # 오늘 날짜 칸
            # =========================
            if day == today:
                st.markdown(f"📊 **달성률 {rate}%** | 😊 {mood}")

                # 🧩 포켓몬
                if st.session_state.today_pokemon:
                    st.image(
                        st.session_state.today_pokemon["image"],
                        width=80
                    )
                    st.caption(
                        f"파트너: {st.session_state.today_pokemon['name']}"
                    )

                st.markdown("---")

                # ✅ 습관 체크리스트
                for habit in st.session_state.habits:
                    hid = habit["id"]
                    name = habit["name"]

                    checked = hid in st.session_state.checked
                    label = f"~~{name}~~" if checked else name

                    if st.checkbox(
                        label,
                        value=checked,
                        key=f"{day}_{hid}"
                    ):
                        st.session_state.checked.add(hid)
                    else:
                        st.session_state.checked.discard(hid)

                # ➕ 새 습관 추가 (달력 안)
                st.markdown("➕ **새 습관 추가**")
                new_habit = st.text_input(
                    " ",
                    placeholder="예: 🧘 스트레칭",
                    key="new_habit_input"
                )

                if st.button("추가", key="add_habit_btn"):
                    if new_habit.strip():
                        st.session_state.habits.append({
                            "id": str(uuid.uuid4()),
                            "name": new_habit.strip()
                        })
                        st.rerun()

            else:
                st.caption("기록 없음")

# =========================
# 하단 안내
# =========================
st.markdown("---")
st.caption("🎮 오늘 날짜 칸이 하루의 모든 것을 담고 있어요")
