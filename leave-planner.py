import calendar
import holidays


#year = input("Enter year")
year = 2026
south_africa_holidays = holidays.SouthAfrica(years=year)

for date, name in sorted(south_africa_holidays.items()):
    print(f"{date}: {name}")

print(calendar.calendar(year))