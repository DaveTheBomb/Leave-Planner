from calendar import calendar, day_name, weekday
import holidays

year = 0

while(True):
    try:
       year = int(input("Enter year: "))
       break
    except:
      print("Enter a valid year, an integer.")
      continue

south_africa_holidays = holidays.SouthAfrica(years=year)

for date, name in sorted(south_africa_holidays.items()):
    day_of_week = day_name[weekday(date.year, date.month, date.day)]
    print(f"{day_of_week} - {date}: {name}")

#print(calendar(year))