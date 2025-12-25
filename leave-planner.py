from calendar import calendar
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
    print(f"{date}: {name}")

print(calendar(year))