from calendar import calendar, day_name, weekday
from datetime import date
import holidays





print("*************************************************************************************")
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
    print(f"{day_of_week:<10} {datei} {name}")
    
print("*************************************************************************************")


list_difference_days = list()

for index in range(len(list_holidays_dates) - 1):
    date_one = list_holidays_dates[index]
    date_two = list_holidays_dates[index + 1]
    day_of_week_one = day_name[weekday(date_one.year, date_one.month, date_one.day)]
    day_of_week_two = day_name[weekday(date_two.year, date_two.month, date_two.day)]
    days_difference = date_two - date_one
    
    print(f"{day_of_week_one:<10} {date_one}  {day_of_week_two:<10}  {date_two}     {days_difference.days} days")
    list_difference_days.append([days_difference.days, f"{day_of_week_one:<10} {date_one}", f"{day_of_week_two:<10} {date_two}"])
    
print("*************************************************************************************")

number_of_leave_days = 0

while(True):
    try:
       number_of_leave_days = int(input("Enter number of leave days available: "))
       break
    except:
      print("Enter a valid year, an integer.")
      continue
      

for potential_days in list_difference_days:
    if potential_days[0] <= number_of_leave_days:  
        print(potential_days)

#print(calendar(year))