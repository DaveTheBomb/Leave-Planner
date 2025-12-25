from calendar import calendar, day_name, weekday
from datetime import date
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

list_holidays_dates = list()

for datei, name in sorted(south_africa_holidays.items()):
    day_of_week = day_name[weekday(datei.year, datei.month, datei.day)]
    list_holidays_dates.append(date(datei.year, datei.month, datei.day))
    print(f"{day_of_week} - {datei}: {name}")

for index in range(len(list_holidays_dates) - 1):
    print(list_holidays_dates[index], list_holidays_dates[index + 1], list_holidays_dates[index + 1] - list_holidays_dates[index])

print("****************************")
print(list_holidays_dates)
#print(calendar(year))