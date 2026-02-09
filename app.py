import calendar

st.markdown("### 🗓️ 이번 달 습관 달력")

today = datetime.date.today()
year, month = today.year, today.month

# 요일 헤더
weekdays = ["월", "화", "수", "목", "금", "토", "일"]
cols = st.columns(7)
for i, day in enumerate(weekdays):
    cols[i].markdown(f"**{day}**")

# 샘플 + 오늘 데이터 (데모)
sample_history = {
    today - datetime.timedelta(days=6): (2, 6),
    today - datetime.timedelta(days=5): (3, 7),
    today - datetime.timedelta(days=4): (4, 8),
    today - datetime.timedelta(days=3): (2, 5),
    today - datetime.timedelta(days=2): (3, 6),
    today - datetime.timedelta(days=1): (4, 9),
    today: (len(checked), mood)
}

cal = calendar.Calendar(firstweekday=0)
month_days = cal.monthdatescalendar(year, month)

for week in month_days:
    cols = st.columns(7)
    for i, day in enumerate(week):
        with cols[i]:
            if day.month != month:
                st.markdown(" ")
            else:
                habits_done, mood_score = sample_history.get(day, (0, 0))
                rate = int(habits_done / 5 * 100) if habits_done else 0

                if rate >= 80:
                    bg = "🟩"
                elif rate >= 40:
                    bg = "🟨"
                else:
                    bg = "🟥"

                st.markdown(
                    f"""
                    <div style="
                        border-radius: 10px;
                        padding: 8px;
                        background-color: #f8f9fa;
                        text-align: center;
                        font-size: 13px;
                    ">
                        <b>{day.day}</b><br>
                        {bg} {rate}%<br>
                        😊 {mood_score}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
