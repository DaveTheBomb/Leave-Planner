import importlib.util
import sys
from datetime import date
from pathlib import Path

import streamlit as st

# Import core logic from leave-planner.py (hyphen in filename requires importlib)
_spec = importlib.util.spec_from_file_location(
    "leave_planner",
    Path(__file__).parent / "leave-planner.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

find_all_breaks = _mod.find_all_breaks
get_holidays = _mod.get_holidays
validate_leave_days = _mod.validate_leave_days
validate_year = _mod.validate_year

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Leave Planner",
    page_icon="🗓️",
    layout="centered",
)

# ── Header ────────────────────────────────────────────────────────────────────
st.title("🗓️ Leave Planner")
st.caption("Maximise your time off by aligning leave with public holidays.")

st.divider()

# ── Inputs ────────────────────────────────────────────────────────────────────
col1, col2 = st.columns(2)

current_year = date.today().year

with col1:
    year_input = st.selectbox(
        "Year",
        options=list(range(2000, 2101)),
        index=list(range(2000, 2101)).index(current_year),
    )

with col2:
    leave_days_input = st.number_input(
        "Available leave days",
        min_value=0,
        max_value=365,
        value=10,
        step=1,
    )

find_btn = st.button("🔍 Find Best Breaks", use_container_width=True, type="primary")

st.divider()

# ── Validate inputs ───────────────────────────────────────────────────────────
year, year_err = validate_year(year_input)
leave_days, leave_err = validate_leave_days(leave_days_input)

if year_err:
    st.error(year_err)
    st.stop()

if leave_err:
    st.error(leave_err)
    st.stop()

# ── Public holidays table ─────────────────────────────────────────────────────
st.subheader(f"📅 Public Holidays — {year}")

holiday_list = get_holidays(year)

if not holiday_list:
    st.warning("No public holidays found for this year.")
else:
    import pandas as pd
    from calendar import day_name, weekday

    holiday_rows = []
    for d, name in holiday_list:
        day_of_week = day_name[weekday(d.year, d.month, d.day)]
        holiday_rows.append({
            "Day": day_of_week,
            "Date": str(d),
            "Holiday": name,
        })

    holiday_df = pd.DataFrame(holiday_rows)
    st.dataframe(holiday_df, use_container_width=True, hide_index=True)

st.divider()

# ── Best breaks results ───────────────────────────────────────────────────────
st.subheader(f"🏆 Best Breaks with {leave_days} leave day(s)")

if find_btn or True:  # always compute on load; button triggers re-render naturally
    with st.spinner("Calculating best breaks…"):
        best_breaks = find_all_breaks(year, leave_days)

    if not best_breaks:
        st.info("No strategic breaks found for this year with the given leave days. Try increasing your leave days.")
    else:
        st.caption(f"Found **{len(best_breaks)}** break(s), ranked longest first.")

        for i, b in enumerate(best_breaks, start=1):
            with st.container(border=True):
                # Top row: rank + break length metric
                m_col, d_col = st.columns([1, 3])

                with m_col:
                    st.metric(
                        label=f"#{i}",
                        value=f"{b['total_break_days']} days",
                    )

                with d_col:
                    st.markdown(
                        f"**{b['break_start']}** → **{b['break_end']}**"
                    )

                    if leave_days == 0:
                        st.caption("No leave days needed — free break!")
                    else:
                        leave_used = b["leave_days_needed"]
                        leave_start = b.get("leave_start", b["break_start"])
                        leave_end = b.get("leave_end", b["break_end"])
                        st.caption(
                            f"Use **{leave_used}** leave day(s): "
                            f"{leave_start} → {leave_end}"
                        )
