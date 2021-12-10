# 2019
def Q1_2020():
  time_minutes1 = 36
  time_seconds1 = 25
  time_minutes2 = 57
  time_seconds2 = 51
  
  totalMins = time_minutes1 + time_minutes2
  totalSeconds = time_seconds1 + time_seconds2
  
  carryOverMins = totalSeconds // 60
  totalSeconds = totalSeconds % 60
  totalMins += carryOverMins
  
  totalHours = totalMins // 60
  totalMins = totalMins  % 60
  
  print(f'Total time is {totalHours}h, {totalMins}m, {totalSeconds}s')
  
def Q2_2007():
  creditHours = eval(input())
  if creditHours > 0 and creditHours <= 40:
    print('Tution Fees = 3000')
  elif creditHours > 40 and creditHours <= 70:
    print('Tution Fees = 5000')
  elif creditHours > 70 and creditHours <= 100:
    print('Tution Fees = 6000')
  else:
    print('Student not allowed to take more than 100 Credit Hours')

def Q4_2007():
  firstNum = eval(input())
  secondNum = eval(input())
  seriesLength = eval(input())
  seriesLength -= 2
  
  print('The series is:')
  print(firstNum)
  print(secondNum)
  while seriesLength > 0:  
    product = firstNum * secondNum
    firstNum = secondNum
    secondNum = product
    print(product)
    seriesLength -= 1
    
val1 = 24
val2 = 11
val3 = 33
if val1 >= 12 or val2 < 30:
  if val3 > 40 or val2 > val1 and val1 < val3:
    print("A ")
  else:
    if not (val2 > 8 or val3 == 24):
      print("B ")
    else:
      print("C ")
else:
  print("D ")
