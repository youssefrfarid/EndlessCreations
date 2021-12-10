x = '(Tsi auto)'
y = 'TSI-AUTO'

import re
xNew = re.sub('[^a-zA-Z]', '', x).lower()
yNew = re.sub('[^a-zA-Z]', '', y).lower()

print(xNew)
print(yNew)


birthYear = eval(input())
age = 2006 - birthYear
lucky = (age/4) + 2
print(age)
print(lucky)