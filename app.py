import streamlit as st
import datetime
import calendar
import random
import requests

# =========================
# 기본 설정
# =========================
st.set_page_config(
    page_title="AI 습관 트래커 (Studio Ghibli)",
    page_icon="🌱",
    layout="wide"
)

st.title("🌱 AI 습관 트래커 (Studio Ghibli 포스터 에디션)")

# =========================
# 세션 상태
# =========================
if "records" not in st.session_state:
    st.session_state.records = {}

if "today_film" not in st.session_state:
    st.session_state.today_film = None

# =========================
# Sidebar (기분)
# =========================
with st.sidebar:
    st.header("😊 오늘 기분")
    mood = st.slider("기분 점수", 1, 10, 5)

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
year, month = today.year, today.month
cal = calendar.Calendar()
month_days = cal.monthdatescalendar(year, month)

# =========================
# 달력
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
                st.image(film["image"], width=70)

            # 날짜 초기화
            if day_key not in st.session_state.records:
                st.session_state.records[day_key] = {"habits": {}}

            habits = st.session_state.records[day_key]["habits"]

            # 🔹 오늘만 습관 추가 가능
            if day == today:
                new_habit = st.text_input(
                    "➕ 습관",
                    key=f"add_{day_key}",
                    placeholder="엔터로 추가"
                )
                if new_habit and new_habit not in habits:
                    habits[new_habit] = False

            # 습관 체크 (줄 바로 그어짐)
            for h, done in habits.items():
                label = f"<span style='text-decoration:line-through;color:gray'>{h}</span>" if done else h

                new_val = st.checkbox(
                    label,
                    value=done,
                    key=f"{day_key}_{h}",
                    label_visibility="visible"
                )

                habits[h] = new_val

# =========================
# 오늘 요약
# =========================
today_key = str(today)
today_habits = st.session_state.records.get(today_key, {}).get("habits", {})
done = sum(today_habits.values())
total = len(today_habits)
rate = int(done / total * 100) if total else 0

st.markdown("---")
c1, c2, c3 = st.columns(3)
c1.metric("오늘 달성률", f"{rate}%")
c2.metric("완료 습관", f"{done}/{total}")
c3.metric("기분", f"{mood}/10")

