## Project Description

This project is designed to help individuals strategically plan their leave days to maximize time off by aligning annual leave with public holidays and weekends. The tool analyzes available leave balances, upcoming public holidays, and calendar patterns to suggest optimal leave combinations that provide the longest possible break using the fewest number of leave days. It offers customizable options based on country-specific holidays, work policies, and personal preferences. The goal of the project is to make leave planning smarter, more efficient, and stress-free, ensuring users get the most rest and value out of their available leave days.

## Requirements

- Python 3.x
- `holidays` library

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/Leave-Planner.git
   cd Leave-Planner
   ```

2. Install the required dependency:
   ```bash
   pip install holidays
   ```

## How to Run

1. Run the script from the project directory:
   ```bash
   python leave-planner.py
   ```

2. When prompted, enter the **year** you want to plan leave for:
   ```
   Enter year: 2026
   ```

3. The tool will display all South African public holidays for that year, along with the day of the week each falls on.

4. When prompted, enter your **number of available leave days**:
   ```
   Enter number of leave days available: 5
   ```

5. The tool will display all possible breaks ranked from longest to shortest, showing how many leave days each one requires.

## How the App Calculates the Longest Break

The app works out the true length of the break you would get by taking leave between two public holidays — not just the raw gap, but the full continuous stretch of days off including attached weekends.

### Step-by-step logic

**1. Identify consecutive public holiday pairs**

The app fetches all public holidays for the chosen year and looks at every pair of consecutive holidays. These are the opportunities to "bridge" a gap with leave days.

**2. Count leave days needed**

For each pair, it counts only the weekdays strictly between the two holidays that are not themselves public holidays. These are the days you would need to use as leave to fill the gap.

**3. Extend the break over attached weekends and holidays**

The raw gap between two holidays understates the real break. If a holiday falls on a Wednesday, you also get Tuesday (leave), Monday (leave) — and the Saturday and Sunday before that are free too. The app walks:
- **Backwards** from the first holiday: if the day before is a weekend or another public holiday, include it in the break start.
- **Forwards** from the second holiday: if the day after is a weekend or another public holiday, include it in the break end.

This gives the true `break_start` and `break_end` of the continuous stretch of days off.

**4. Calculate total break length**

```
total_break_days = (break_end - break_start).days + 1
```

**5. Filter by available leave days**

Only breaks that require fewer or equal leave days to the number you entered are shown.

**6. Rank by total break length**

Results are sorted from longest to shortest break, so the best option is always shown first.

### Example

Say there is a public holiday on Thursday 2026-03-19 and another on Monday 2026-03-23:

- Leave days needed: Friday 2026-03-20 = **1 leave day**
- Walk backwards from Thursday: Wednesday is a normal workday, so break starts on Thursday 2026-03-19
- Walk forwards from Monday: Tuesday is a normal workday, so break ends on Monday 2026-03-23
- But Saturday 2026-03-21 and Sunday 2026-03-22 are free anyway
- Total break: Thu 19 → Mon 23 = **5 days** off using just 1 leave day
