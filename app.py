import streamlit as st
import datetime
import calendar
import random
import requests

# =========================
# 기본 설정
# =========================
st.set_page_config(
    page_title="AI 습관 트래커 (Ghibli Forest)",
    page_icon="🌱",
    layout="wide"
)

st.title("🌱 AI 습관 트래커 (Ghibli Forest Edition)")

# =========================
# 세션 상태 초기화
# =========================
if "records" not in st.session_state:
    st.session_state.records = {}

if "streak" not in st.session_state:
    st.session_state.streak = 0

if "forest_level" not in st.session_state:
    st.session_state.forest_level = 0

if "today_film" not in st.session_state:
    st.session_state.today_film = None

# =========================
# Sidebar (컨트롤 센터)
# =========================
with st.sidebar:
    st.header("🎮 오늘의 컨트롤")

    mood = st.slider("😊 오늘 기분", 1, 10, 5)

    st.markdown("---")
    st.subheader("➕ 오늘 습관 추가")
    new_habit = st.text_input("습관 이름", placeholder="예: 스트레칭")

    st.markdown("---")
    st.subheader("🔥 Streak & Forest")
    st.write(f"연속 달성: 🔥 x {st.session_state.streak}")

# =========================
# Ghibli Film API
# =========================
def get_ghibli_film():
    try:
        r = requests.get("https://ghibliapi.vercel.app/films", timeout=10)
        f = random.choice(r.json())
        return {"title": f["title"], "image": f["image"]}
    except:
        return None

if st.session_state.today_film is None:
    st.session_state.today_film = get_ghibli_film()

film = st.session_state.today_film

# =========================
# 날짜 계산
# =========================
today = datetime.date.today()
today_key = str(today)
year, month = today.year, today.month
month_days = calendar.Calendar().monthdatescalendar(year, month)

if today_key not in st.session_state.records:
    st.session_state.records[today_key] = {"habits": {}}

today_habits = st.session_state.records[today_key]["habits"]

# 습관 추가
if new_habit and new_habit not in today_habits:
    today_habits[new_habit] = False

# =========================
# 달력 UI
# =========================
st.markdown("## 🗓️ 이번 달 습관 달력")

weekdays = ["월", "화", "수", "목", "금", "토", "일"]
cols = st.columns(7)
for i, w in enumerate(weekdays):
    cols[i].markdown(f"**{w}**")

for week in month_days:
    cols = st.columns(7)
    for i, day in enumerate(week):
        with cols[i]:
            if day.month != month:
                st.empty()
                continue

            day_key = str(day)
            st.markdown(f"**{day.day}**")

            # 오늘 포스터
            if day == today and film:
                st.image(film["image"], width=65)

            if day_key not in st.session_state.records:
                st.session_state.records[day_key] = {"habits": {}}

            habits = st.session_state.records[day_key]["habits"]

            for h, done in habits.items():
                c1, c2 = st.columns([1, 5])
                with c1:
                    cb = st.checkbox(
                        "",
                        value=done,
                        key=f"{day_key}_{h}"
                    )
                with c2:
                    label = (
                        f"<span style='color:gray;text-decoration:line-through'>{h}</span>"
                        if cb else h
                    )
                    st.markdown(label, unsafe_allow_html=True)

                habits[h] = cb

# =========================
# 오늘 성과 계산
# =========================
done = sum(today_habits.values())
total = len(today_habits)
rate = int(done / total * 100) if total else 0

# =========================
# 🔥 Streak 로직
# =========================
if total > 0 and done == total:
    st.session_state.streak += 1
else:
    st.session_state.streak = 0

# =========================
# 🌱 Forest 성장 로직
# =========================
if rate >= 80:
    st.session_state.forest_level += 2
elif rate >= 50:
    st.session_state.forest_level += 1

forest_stage = (
    "🌱 새싹" if st.session_state.forest_level < 3 else
    "🌿 관목" if st.session_state.forest_level < 6 else
    "🌳 나무" if st.session_state.forest_level < 10 else
    "🌲 숲"
)

# =========================
# 요약 UI (듀오링고 느낌)
# =========================
st.markdown("---")
st.subheader("🔥 오늘의 성장")

c1, c2, c3 = st.columns(3)
c1.metric("달성률", f"{rate}%")
c2.metric("Streak", f"🔥 x {st.session_state.streak}")
c3.metric("Forest", forest_stage)

# 🔥 불꽃 애니메이션 (이모지 연출)
st.markdown(
    " ".join(["🔥"] * min(st.session_state.streak, 10))
)

# 🌱 숲 성장 연출
st.markdown(f"### {forest_stage}")
