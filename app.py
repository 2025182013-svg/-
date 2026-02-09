import streamlit as st
import datetime
import calendar
import random
import requests
from openai import OpenAI

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
# Sidebar (컨트롤 센터)
# =========================
with st.sidebar:
    st.header("🎮 오늘의 컨트롤")

    mood = st.slider("😊 오늘 기분", 1, 10, 5)

    st.markdown("---")
    st.subheader("➕ 오늘 습관 추가")
    new_habit = st.text_input("습관 이름", placeholder="예: 스트레칭")

    st.markdown("---")
    st.subheader("🔑 OpenAI API")
    openai_key = st.text_input(
        "API Key",
        type="password",
        placeholder="sk-..."
    )

    generate_ai = st.button("🤖 AI 코치 리포트 생성")

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
# 날짜
# =========================
today = datetime.date.today()
today_key = str(today)
year, month = today.year, today.month
month_days = calendar.Calendar().monthdatescalendar(year, month)

if today_key not in st.session_state.records:
    st.session_state.records[today_key] = {"habits": {}}

today_habits = st.session_state.records[today_key]["habits"]

# 사이드바 습관 추가 처리
if new_habit and new_habit not in today_habits:
    today_habits[new_habit] = False

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

            if day == today and film:
                st.image(film["image"], width=70)

            if day_key not in st.session_state.records:
                st.session_state.records[day_key] = {"habits": {}}

            habits = st.session_state.records[day_key]["habits"]

            for h, done in habits.items():
                cb = st.checkbox(
                    h,
                    value=done,
                    key=f"{day_key}_{h}"
                )
                habits[h] = cb

                # 취소선 텍스트
                if cb:
                    st.markdown(
                        f"<span style='color:gray;text-decoration:line-through'>{h}</span>",
                        unsafe_allow_html=True
                    )

# =========================
# 듀오링고 스타일 요약
# =========================
done = sum(today_habits.values())
total = len(today_habits)
rate = int(done / total * 100) if total else 0

st.markdown("---")
st.subheader("🔥 오늘의 진행 상황")

c1, c2, c3 = st.columns(3)
c1.metric("달성률", f"{rate}%")
c2.metric("완료 미션", f"{done}/{total}")
c3.metric("기분", f"{mood}/10")

# =========================
# AI 코치 리포트
# =========================
if generate_ai:
    if not openai_key:
        st.error("OpenAI API Key를 입력해주세요")
    else:
        client = OpenAI(api_key=openai_key)

        prompt = f"""
너는 듀오링고 스타일의 친절하지만 집요한 코치야.

오늘 정보:
- 기분: {mood}/10
- 달성률: {rate}%
- 완료한 습관: {[h for h, v in today_habits.items() if v]}
- 미완료 습관: {[h for h, v in today_habits.items() if not v]}
- 오늘의 지브리 작품: {film['title']}

조건:
- 짧고 동기부여되게
- 이모지 사용
- 내일 행동 1개 제안
"""

        with st.spinner("AI 코치 분석 중..."):
            res = client.chat.completions.create(
                model="gpt-5-mini",
                messages=[{"role": "system", "content": prompt}]
            )

        st.markdown("## 🤖 AI 코치 리포트")
        st.markdown(res.choices[0].message.content)
