# 🗓️ Leave Planner

Strategically plan your leave days to maximise time off by aligning annual leave with public holidays and weekends.

The tool analyses your available leave balance and South African public holidays to suggest the best leave combinations — giving you the longest possible break for the fewest leave days used.

---

## Features

- Ranked list of break opportunities from longest to shortest
- Covers all South African public holidays
- Accounts for weekends automatically attached to the break
- Web UI (Streamlit) and CLI both available

---

## Requirements

- Python 3.8+

---

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/Leave-Planner.git
   cd Leave-Planner
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   ```

   On Windows (PowerShell):
   ```powershell
   .venv\Scripts\Activate.ps1
   ```

   On macOS/Linux:
   ```bash
   source .venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## Usage

### Web UI (recommended)

```bash
streamlit run app.py
```

The app will open in your browser. Select a year, enter your available leave days, and click **Find Best Breaks**.

### CLI

```bash
python leave-planner.py
```

Follow the prompts to enter the year and your available leave days. Results are printed to the terminal.

---

## How It Works

The app finds every pair of consecutive public holidays and calculates how many weekdays you'd need to take as leave to bridge the gap. It then extends each break over any attached weekends or adjacent holidays to give you the true continuous stretch of days off.

### Step-by-step logic

1. **Identify consecutive public holiday pairs** — every pair of holidays is a potential bridge opportunity.
2. **Count leave days needed** — only the weekdays strictly between the two holidays that are not themselves public holidays.
3. **Extend over attached weekends and holidays** — walk backwards from the first holiday and forwards from the second to include any free days on either side.
4. **Calculate total break length** — `(break_end - break_start).days + 1`
5. **Filter by available leave days** — only show breaks you can actually afford.
6. **Rank by total break length** — best option always shown first.

### Example

Public holiday on Thursday 2026-03-19, another on Monday 2026-03-23:

| | |
|---|---|
| Leave days needed | Friday 2026-03-20 = **1 day** |
| Weekend included | Sat 21 + Sun 22 are free |
| Total break | Thu 19 → Mon 23 = **5 days off** |

---

## Project Structure

```
Leave-Planner/
├── app.py              # Streamlit web UI
├── leave-planner.py    # Core logic + CLI entry point
├── version.py          # Version number
├── requirements.txt    # Direct dependencies
└── test_leave_planner.py
```

---

## Running Tests

```bash
python -m unittest test_leave_planner.py
```
