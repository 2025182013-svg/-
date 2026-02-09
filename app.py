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

st.title("🌱 AI 습관 트래커 (Studio Ghibli 에디션)")

# =========================
# 세션 상태 초기화
# =========================
if "habits" not in st.session_state:
    st.session_state.habits = ["기상 미션", "물 마시기", "공부/독서"]

if "records" not in st.session_state:
    st.session_state.records = {}

# =========================
# Ghibli API
# =========================
def get_ghibli_character():
    try:
        r = requests.get(
            "https://ghibliapi.vercel.app/people",
            timeout=10
        )
        data = r.json()
        char = random.choice([c for c in data if c.get("image")])
        return char
    except:
        return None

ghibli_char = get_ghibli_character()

# =========================
# 오늘 정보
# =========================
today = datetime.date.today()
year, month = today.year, today.month
cal = calendar.Calendar()
month_days = cal.monthdatescalendar(year, month)

today_key = str(today)
if today_key not in st.session_state.records:
    st.session_state.records[today_key] = {
        h: False for h in st.session_state.habits
    }

# =========================
# 상단 입력 UI
# =========================
st.subheader("😊 오늘 기분")
mood = st.slider("기분 점수", 1, 10, 5)

# =========================
# 습관 관리
# =========================
st.subheader("✏️ 습관 관리")

new_habit = st.text_input("새 습관 추가")
if st.button("➕ 추가") and new_habit:
    if new_habit not in st.session_state.habits:
        st.session_state.habits.append(new_habit)
        for d in st.session_state.records.values():
            d[new_habit] = False

# =========================
# 달력 UI
# =========================
st.markdown("## 🗓️ 이번 달 습관 달력")

cols = st.columns(7)
for i, day in enumerate(["월","화","수","목","금","토","일"]):
    cols[i].markdown(f"**{day}**")

for week in month_days:
    cols = st.columns(7)
    for i, day in enumerate(week):
        with cols[i]:
            if day.month != month:
                st.empty()
                continue

            day_key = str(day)
            st.markdown(f"### {day.day}")

            # 오늘이면 캐릭터 표시
            if day == today and ghibli_char:
                st.image(ghibli_char["image"], width=80)
                st.caption(ghibli_char["name"])

            # 기록 초기화
            if day_key not in st.session_state.records:
                st.session_state.records[day_key] = {
                    h: False for h in st.session_state.habits
                }

            # 습관 체크
            for h in st.session_state.habits:
                checked = st.session_state.records[day_key].get(h, False)
                cb_key = f"{day_key}_{h}"

                new_val = st.checkbox(
                    h,
                    value=checked,
                    key=cb_key
                )

                st.session_state.records[day_key][h] = new_val

                # 취소선
                if new_val:
                    st.markdown(
                        f"<span style='color:gray;text-decoration:line-through'>{h}</span>",
                        unsafe_allow_html=True
                    )

# =========================
# 오늘 요약
# =========================
done = sum(st.session_state.records[today_key].values())
total = len(st.session_state.habits)
rate = int((done / total) * 100) if total else 0

st.markdown("---")
st.subheader("📊 오늘의 요약")

c1, c2, c3 = st.columns(3)
c1.metric("달성률", f"{rate}%")
c2.metric("완료 습관", f"{done}/{total}")
c3.metric("기분", f"{mood}/10")

# =========================
# 안내
# =========================
with st.expander("ℹ️ 안내"):
    st.markdown("""
- 🌱 Studio Ghibli API 사용
- 💾 데이터는 세션 기반 (새로고침 시 초기화)
- 🗓️ 오늘 날짜에만 캐릭터가 표시됩니다
""")
