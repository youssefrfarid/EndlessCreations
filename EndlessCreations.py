from pprint import pprint
import re
from numpy import nancumsum

# Connection Imports
import pandas as pd
from pandas.io.sql import pandasSQL_builder
import pymysql 
import pyodbc
import logging
import sshtunnel
from sshtunnel import SSHTunnelForwarder

# Timing Program
import time
start_time = time.time()

# VTiger Config
vtiger_ssh_host = '134.122.89.44'
vtiger_ssh_username = 'root'
vtiger_ssh_password = 'u376e9pqtwq5'
vtiger_database_username = 'vtiger'
vtiger_database_password = 'EndC_stv@E'
vtiger_database_name = 'vtigercrm720'
# WolfApp Config
wolfapp_host = '192.241.153.160'
wolfapp_port = 3306
wolfapp_database_name = 'endlessc_endless'
wolfapp_database_password = 'J0j0T0ny'
wolfapp_database_username = 'endlessc_ramy'
localhost = '127.0.0.1'

ArabicToEng = {
  '٠': '0',
  '١': '1',
  '٢': '2',
  '٣': '3',
  '٤': '4',
  '٥': '5',
  '٦': '6',
  '٧': '7',
  '٨': '8',
  '٩': '9',
}

SoftexCity = {
  '0': '',
  '1': 'القاهرة',
  '2': 'بورسعيد',
  '3': 'الاسكندرية',
  '4': 'الاقصر',
  '5': 'الغردقه',
  '6': 'المنزلة',
  '7': 'طنطا',
  '8': 'دمياط',
  '11': 'شبين الكوم',
  '12': 'اسيوط',
  '13': 'العين السخنة',
  '14': 'الاسماعيليه',
  '15': 'السويس',
  '16': 'اسوان',
  '17': 'الشرقية',
  '18': 'البحيرة',
  '19': 'المنيا',
  '20': 'المنصورة',
  '21': 'مرسى مطروح',
  '23': 'القليوبية'
}

SoftexArea = {
  '0': '',
  '4': 'المنطقة السابعة',
  '36': 'المنطقة الاولى',
  '40': 'المنطقة الثانية',
  '41': 'الحرفيين',
  '42': 'السلام',
  '44': 'العبور',
  '45': 'شارع دمشق',
  '46': 'سفير',
  '47': 'الماظة',
  '48': 'النزهة الجديدة',
  '49': 'شيراتون',
  '50': 'المنطقة الثالثة',
  '51': 'العجوزة',
  '52': 'الدقي',
  '53': 'المهندسين',
  '54': 'امبابة',
  '55': 'بولاق',
  '56': 'أرض اللواء',
  '57': 'المنطقة الرابعة',
  '58': 'الرحاب',
  '59': 'التجمع الخامس',
  '60': 'مدينة نصر',
  '61': 'المنطقة الخامسة',
  '62': 'شبرا',
  '63': 'شارع الجمهورية',
  '64': 'شارع بورسعيد',
  '65': 'شارع أحمد سعيد',
  '66': 'التوفيقية',
  '67': 'المنطقة السادسة',
  '68': 'عين شمس',
  '69': 'ترعة اسماعيلية',
  '70': 'الزيتون',
  '71': 'المطرية', 
  '72': 'الزمالك',
  '73': '6 اكتوبر',
  '75': 'شارع الهرم',
  '76': 'شارع فيصل',
  '77': 'المريوطية',
  '78': 'المنصورية',
  '79': 'النعام',
  '80': 'المنطقة الثامنة',
  '81': 'المعادي', 
  '82': 'العباسية',
  '83': 'الدراسة',
  '84': 'الاوتوستراد',
  '85': 'ابو رواش',
  '86': 'الهرم',
  '87': 'القطامية',
  '88': 'الجيزة',
  '89': 'مصر الجديدة',
  '90': 'حلوان',
  '91': 'العاشر من رمضان', 
  '92': 'نادى السكة',
  '93': 'الحى العاشر',
  '94': 'حدائق الاهرام',
  '95': 'السيدة زينب',
  '97': 'الزاوية الحمراء',
  '98': 'جسر السويس',
  '99': 'بنها',
}

SoftexCtype = {
  '0': '',
  '6': '',
  '4': 'Delivery',
  '7': 'Corporate General',
  '10': 'Quick Oil Center',
  '11': 'Motorcycle',
  '12': 'Corporate Speed Limiter',
  '16': 'Retail',
  '17': 'Distributor',
  '18': 'PCMO-Service Center',
  '19': 'Diesel-Service Center',
  '20': 'Diesel Service Center (Not Active)',
  '21': 'Distributor (Not Active)',
  '22': 'Motorcycle (Not Active)',
  '23': 'PCMO -Service Center (Not Active)',
  '24': 'Retail (Not Active)',
  '26': 'Corporate General ( Not Active )',
  '27': 'Corporate GPS',
  '28': 'Corporate GPS ( Not Active )',
  '29': 'Corporate Wolf',
  '30': 'Corporate Wolf ( Not Active )',
  '31': 'Corporate Speed Limiter (Not Active )',
  '32': 'Corporate Filters',
  '33': 'Corporate Filters (Not Active )',
  '34': 'Retail Filters',
  '35': 'Retail Filters ( Not Active )',
  '36': 'Change Delivery',
  '37': 'Corporate G.B',
  '38': 'Corporate G.B ( Not Active )',
  '39': 'Corporate OSA',
  '41': 'Corporate OSA (Not Active)',
  '42': 'Distributor Filters',
  '44': 'Distributor Filters (Not Active)',
  '45': 'CIAK',
  '48': 'Suppported by Sara',
  '50': 'Supported by Yasmin',
  '51': 'Bosch',
  '52': 'Coolection by Bahaa',
  '53': 'Coolection by Saber',
  '54': 'Coolection by Nabil',
  '1053': 'Collection by Merna',
  '1054': 'Lagence',
  '1055': 'Supported by Alaa'
}

SoftexBranch = {
  '-1': '',
  '0': '',
  '2': 'Head Office',
  '3': 'Ef7as, Nasr City',
  '6': 'Installations',
  '7': 'Collections#1',
  '8': 'Collections#2',
  '9': 'El mohandseen',
}

SoftexSalesman = {
  '0': '',
  '2': 'Samer Ayoub',
  '3': 'Hany Alfy',
  '4': 'Mohamed Said',
  '5': 'Nader Neamatalla',
  '6': 'Office General',
  '7': 'QOC General',
  '8': 'Technical Team',
  '9': 'Youssef Emile',
  '10': 'George Barsom',
  '11': 'Mohamed Dosuky',
  '12': 'Nady Naim',
  '13': 'Ahmed El Gohry',
  '16': 'Salma Tarek',
  '17': 'Customer Service',
  '23': 'Nabil Lamie',
  '24': 'Stavro Seif',
  '25': 'Marina Adel',
  '28': 'Adham Ziad',
  '30': 'QOC Corporate',
  '31': 'Office Corporate',
  '33': 'Tony Ramzy',
  '34': 'Nader Nabil',
  '35': 'Nail Nabil',
  '36': 'Shareef',
  '37': 'Mohamed Samir',
  '38': 'Maged Samir',
  '39': 'David John',
  '40': 'Marco Nabil',
  '42': 'Lagence',
  '43': 'ElKtalog',
}
WolfCity = {
  'nan': '',
  
  '1': 'Cairo',
  '2': 'Giza',
  '3': 'Alex',
  '4': 'Suez',
  '5': 'Ismailia',
  '6': 'Port Said',
  '7': 'Qalyobia',
  '8': 'Minoufiya',
  '9': 'Sharqia',
  '10': 'Gharbiya',
  '11': 'Daqahlya',
  '12': 'Kafr El-Shiekh',
  '13': 'Damietta',
  '14': 'Behaira',
  '15': 'Fayuom',
  '16': 'Miniya',
  '17': 'Assuit',
  '18': 'Sohag',
  '19': 'Beni-Suef',
  '20': 'Qena',
  '21': 'Aswan',
  '22': 'Luxor',
  '23': 'Red Sea',
  '24': 'South Sinaa',
  '25': 'North Coast and Matrouh',
  '26': 'New Valley',
  '27': 'North Sinai',
  '28': 'Abu Simbel',
  '29': 'Marsa Allam',
  '30': 'Salloum',
  '31': 'Halayb And Shalatin',
  '32': 'Oasis and other towns and vllages outside min city limits in zone 4 and 5'
}

template = {
  '10': '',
  '11': '',
  '12': '',
  '13': '',
  '14': '',
  '15': '',
  '16': '',
  '17': '',
  '18': '',
  '19': '',
}
# Create a SSH Tunnel
def open_ssh_tunnel(verbose=False):
    """Open an SSH tunnel and connect using a username and password.
    
    :param verbose: Set to True to show logging
    :return tunnel: Global SSH tunnel connection
    """
    
    if verbose:
        sshtunnel.DEFAULT_LOGLEVEL = logging.DEBUG
    
    global tunnel
    tunnel = SSHTunnelForwarder(
        (vtiger_ssh_host, 22),
        ssh_username = vtiger_ssh_username,
        ssh_password = vtiger_ssh_password,
        remote_bind_address = ('127.0.0.1', 3306)
    )
    
    tunnel.start()
    
def mysql_connect():
    """Connect to a MySQL server using the SSH tunnel connection
    
    :return connection: Global MySQL database connection
    """
    
    global connection
    
    connection = pymysql.connect(
        host='127.0.0.1',
        user=vtiger_database_username,
        passwd=vtiger_database_password,
        db=vtiger_database_name,
        port=tunnel.local_bind_port
    )
    
def run_query(sql):
    """Runs a given SQL query via the global database connection.
    
    :param sql: MySQL query
    :return: Pandas dataframe containing results
    """
    
    return pd.read_sql_query(sql, connection)
  
def mysql_disconnect():
    """Closes the MySQL database connection.
    """
    
    connection.close()

def close_ssh_tunnel():
    """Closes the SSH tunnel connection.
    """
    
    tunnel.close

# Connecrt to SOFTEX
def softex():
  conn = pyodbc.connect('Driver={SQL Server};'
                     'Server=YOUSSEF-PC\SQLEXPRESS;'
                     'Database=Endless-mc;'
                     'Trusted_Connection=yes;')

  cursor = conn.cursor()
  cursor.execute('SELECT phone, serial FROM dbo.clients')
  softexPhone = cursor.fetchall()
  
  cursor.execute('SELECT mobile, serial FROM dbo.clients')
  softexMobile = cursor.fetchall()
  
  cursor.execute('SELECT serial, name, phone, mobile, climit, city, area, ctype, branch, salesman, taxesno, commercialno, email, freedays, scode, status, paymenttype, allowcoin, person, address FROM dbo.clients')
  softexData = cursor.fetchall()
   
  return softexPhone, softexMobile, softexData

# Conntect to VTiger
def vtiger():
  open_ssh_tunnel()
  mysql_connect()
  
  dfContactDetailsMobile = run_query("SELECT mobile, contactid FROM vtiger_contactdetails")
  dfContactDetailsPhone = run_query("SELECT phone, contactid FROM vtiger_contactdetails")
  dfContactsData = run_query("SELECT contactid, firstname, lastname, mobile, phone, email, contact_no, salutation, vehicle_type, contact_brand, year_of_made, client_point, add_point FROM vtiger_contactdetails")
  dfContactsExtraData = run_query('SELECT contactid, cf_751, cf_753, cf_757, cf_845, cf_881, cf_883, cf_885, cf_932, cf_936, cf_1567, cf_2079, cf_2081, cf_2083, cf_2085, cf_2087, cf_2089, cf_2109, cf_2113, cf_2530 FROM vtiger_contactscf')
  # id, Name in Arabic,  Landline, Cllient Type, District, StreetDetails, Country, City, Mobile 2, Mobile 2, Model, Call Feedback, Vehicle Service Tracker, App User Experience, Order, Points Awareness, Other Comments, Client Case, Next Action Date, Converted Lead ID
  
  dfAccountsPhone = run_query('SELECT phone, accountid FROM vtiger_account')
  dfAccountsOtherPhone = run_query('SELECT otherphone, accountid FROM vtiger_account')
  dfAccountsData = run_query('SELECT accountid, accountname, phone, otherphone, isconvertedfromlead, account_no FROM vtiger_account')
  dfAccountsExtraData = run_query('SELECT accountid, cf_893, cf_895, cf_899, cf_942, cf_956, cf_1599, cf_2027, cf_2057, cf_2137, cf_2177, cf_2209, cf_2455, cf_2457, cf_2528 FROM vtiger_accountscf')
  # id, Street Details, Building No, Country, ClientType, WayOfPayment, Contact Person, 2nd Contact Person, Organization Type, Sales Man, Location Link, Area, Brands, State محافظة, Converted Lead ID 
  
  mysql_disconnect()
  close_ssh_tunnel()
  
  return dfContactDetailsMobile.values, dfAccountsPhone.values, dfContactDetailsPhone.values, dfAccountsOtherPhone.values, dfAccountsData.values, dfContactsData.values, dfAccountsExtraData.values, dfContactsExtraData.values

# Connnect to WolfApp
def wolfapp():
  connection = pymysql.connect(
        host=wolfapp_host,
        user=wolfapp_database_username,
        passwd=wolfapp_database_password,
        db=wolfapp_database_name,
        port=wolfapp_port
  )
  dfWolfClients = pd.read_sql_query('SELECT ClientPhone, IDClient FROM endlessc_endless.clients;', connection)
  dfWolfData = pd.read_sql_query('SELECT IDClient, ClientName, ClientPhone, ClientEmail, IDCity, ClientPasswordPlain, ClientStatus, ClientPoints FROM endlessc_endless.clients;', connection)
  
  return dfWolfClients.values, dfWolfData.values

# Exporting Patterns
namePattern = '[^a-zA-Zء-ي\s]'
# Clean Numbers
onlyNumbersPattern = '[^+\d]'
arabicPattern = '[٠-٩]'
# Egy Numbers
correctPattern = '^[0][1][0-9]{9}'
egyCodePattern = '^[+][2][0][1][0-9]{9}'
oldNumPattern = '^[0][1][0-9]{8}'
oldEgyCodePattern = '^[+][2][0][1][0-9]{8}'
twentyNewNumber = '^[2][0][1][0-9]{9}'
zeroZeroTwo = '^[0][0][2][0][1][0-9]{9}'
# Iraq Numbers
iraqPattern = '^[9][6][4][7][3-9][0-9]{8}'
iraqPatternZeros = '^[0][0][9][6][4][7][3-9][0-9]{8}'
# Jordan Numbers
jordanPattern = '^[9][6][2][7][7-9][0-9]{7}'
jordanPatternZeros = '^[0][0][9][6][2][7][7-9][0-9]{7}'
# Saudi Arabia Numbers
saPattern = '^[9][6][6][5][^2][0-9]{7}'
saPatternZeros = '^[0][0][9][6][6][5][^2][0-9]{7}'

# Clean strange characters and spaces
def phoneCleaner(phoneNumbers):
  correctNumbers = []
  for number in phoneNumbers:
    num = number[0]
    id = number[1]
    # Replaces all non-digit or + with an empty string
    correctNumbers.append((re.sub(onlyNumbersPattern,'', num), id))
    
  return formatNumbers(correctNumbers)


def formatNumbers(phoneNumbers):
  correctedNumbers = []
  brokenNumbers = []
  
  for number in phoneNumbers:
    num = number[0]
    id = number[1]
    
    # Check if number is Arabic and translate it
    result = re.match(arabicPattern, num)
    if result != None:
      # Translate Number
      translated = ''
      for n in num:
        translated += ArabicToEng[n]
      num = translated

    # Checks the length of the number (NEW)
    if (len(num) == 13 and num[0] == '+') or len(num) == 11:
      # Check if the number is correct
      result = re.fullmatch(correctPattern, num)
      
      if result != None:
        correctedNumbers.append((num, id))
        continue

      # Check if the number is correct but has +20 and fix it
      result = re.fullmatch(egyCodePattern, num)
      
      if result != None:
        correctedNumbers.append((num[2:], id))
        continue
    
    # Checks the length of the number (OLD)
    elif (len(num) == 12 and num[0] == '+') or len(num) == 10:
      # Check if it has a Code or not
      result = re.fullmatch(oldNumPattern, num)
      
      if result != None:
        # Check which old number it is and assign the correct new one
        oldRange = num[:3]
        # Etisalat
        if oldRange == '011' or oldRange == '014':
          correctedNumbers.append(('011' + num[2:], id))
          continue
        # Vodafone
        elif oldRange == '010' or oldRange == '019' or oldRange == '016': 
          correctedNumbers.append(('010' + num[2:], id))
          continue
        # Mobinil / Orange
        elif oldRange == '012' or oldRange == '018' or oldRange == '017':
          correctedNumbers.append(('012' + num[2:], id))
          continue
        
      # fix numbers with code
      result = re.fullmatch(oldEgyCodePattern, num)
      
      if result != None:
        # Check which old number it is and assign the correct new one
        oldRange = num[2:5]
        # Etisalat
        if oldRange == '011' or oldRange == '014':
          correctedNumbers.append(('011' + num[4:], id))
          continue
        # Vodafone
        elif oldRange == '010' or oldRange == '019' or oldRange == '016': 
          correctedNumbers.append(('010' + num[4:], id))
          continue
        # Mobinil / Orange
        elif oldRange == '012' or oldRange == '018' or oldRange == '017':
          correctedNumbers.append(('012' + num[4:], id))
          continue
      
      # Check if number is missing a zero at the start
      if len(num) == 10 and num[0] != '0':
        if num[0] == '1':
          numStart = '0' + num[:2]
          if numStart in ['010','011','012','015']:
            correctedNumbers.append(('0' + num, id))
            continue
      
    # Check if number starts with 20 instead of +20 
    result = re.fullmatch(twentyNewNumber, num)
    if result != None:
      correctedNumbers.append((num[1:], id))
      continue      
    
    #Check if number starts with 002
    result = re.fullmatch(zeroZeroTwo, num)
    if result != None:
      correctedNumbers.append((num[3:], id))
      continue
    
    # Check if number is Iraq
    result = re.fullmatch(iraqPattern, num)
    if result != None:
      correctedNumbers.append((num, id))
      continue
    else:
      result = re.fullmatch(iraqPatternZeros, num)
      if result != None:
        correctedNumbers.append((num[2:], id))
        continue
    
    # Check if number is Jordan
    result = re.fullmatch(jordanPattern, num)
    if result != None:
      correctedNumbers.append((num, id))
      continue
    else:
      result = re.fullmatch(jordanPatternZeros, num)
      if result != None:
        correctedNumbers.append((num[2:], id))
        continue
    
    # Check if number is Saudi Arabia
    result = re.fullmatch(saPattern, num)
    if result != None:
      correctedNumbers.append((num, id))
      continue
    else:
      result = re.fullmatch(saPatternZeros, num)
      if result != None:
        correctedNumbers.append((num[2:], id))
        continue
      
    # Check if number is illogical or empty and replace with 11 0s
    brokenNumbers.append((num, id))
  return correctedNumbers, brokenNumbers

# Merge Primary and Secondary numbers
def merge(phones, mobiles):
  merged = []
  pSerials = [] 
  mSerials = [] 
  pNums = []
  mNums= []
  
  for phone in phones:
    pNums.append(phone[0])
    pSerials.append(phone[1])
    
  for mobile in mobiles:
    mNums.append(mobile[0])
    mSerials.append(mobile[1])

  for i, pSerial in enumerate(pSerials):
    if pSerial in mSerials:
      mIndex = mSerials.index(pSerial)
      if pNums[i] == mNums[mIndex]:
        merged.append((str(pSerial), str(pNums[i]), '0'))
      else:
        merged.append((str(pSerial), str(pNums[i]), str(mNums[mIndex])))
    else:
      merged.append((str(pSerial), str(pNums[i]), '0'))

  for i, mSerial in enumerate(mSerials):
    if mSerial not in pSerials:
      merged.append((str(mSerial), '0', str(mNums[i])))    
  return merged

# Compare if data is already added
def shouldAdd(dataToAdd, data):
  cleanData = data.split('|')
  cleanData.remove('')
  cleanData.remove('')
  add = True
  dataToAdd = re.sub(namePattern, '', dataToAdd).lower()
  
  for data in cleanData:
    dataToCompare = re.sub(namePattern, '', data).lower()
    if dataToAdd in dataToCompare:
      add = False
      break
  
  return add
  
# Combining all Contacts
def getAllContacts(
  softexPhones,
  vtigerContactDetailsMobile,
  vtigerAccountPhone,
  wolfmobiles,
  softexMobiles,
  vtigerContactDetailsPhone,
  vtigerAccountOtherPhone,
  softexData,
  vtigerAccountsData,
  vtigerContactsData,
  wolfData,
  vtigerAccountsExtraData,
  vtigerContactsExtraData
):
  
  allContacts = []
  '''
  ['myID', 'numbers | separeted', 'CompanyID', 'softexSerials', 'vtigerAccountID', 'vtigerContactID', 'wolfID']
  ['myID','Names', 'isCompany (1,0)', 'Customer]
  Select first name from softex w add el ba2y f field tany  Sharekat
  Select first name from vtigerContact w add el ba2y f field tany Contacts
  Add Related Company (Name)
  Delete CompanyID w MyID
  ''' 
  # Initializing myID
  myID = 1
  
  # Start filling the dictionary with softex numbers take duplicates in mind
  mergedSoftex = merge(softexPhones, softexMobiles)
  for i in range(len(mergedSoftex)):
    # Check if the number isnt in allContacts
    if allContacts == []: # First Entry
      if mergedSoftex[i][1] != '0' and mergedSoftex[i][2] != '0':
        # Check if record has primary and secondary numbers
        allContacts.append([f'{myID}', '|' + mergedSoftex[i][1] + '|' + mergedSoftex[i][2] + '|', '', '|' + mergedSoftex[i][0] + '|', '|', '|', '|'])
      elif mergedSoftex[i][1] != '0':
        # Check if record has primary number only
        allContacts.append([f'{myID}', '|' + mergedSoftex[i][1] + '|', '', '|' + mergedSoftex[i][0] + '|', '|', '|', '|'])
      else:
        # Check if record has secondary number only
        allContacts.append([f'{myID}', '|' + mergedSoftex[i][2] + '|', '', '|' + mergedSoftex[i][0] + '|', '|', '|', '|'])
      
      myID += 1
    else: # Not first entry
      j = 0
      end = len(allContacts) 
      found = False
      while j < end:
        numbers = allContacts[j][1]
        # Check if record has primary number
        if mergedSoftex[i][1] != '0':
          # Check if primary number is in the numbers of this record
          if mergedSoftex[i][1] in numbers:
            # Check if unique id is already added
            if mergedSoftex[i][0] not in allContacts[j][3]:
              allContacts[j][3] += f'{mergedSoftex[i][0]}|'
            # Check if the secondary of the primary is in the numbers
            if mergedSoftex[i][2] not in numbers:
              allContacts[j][1] += f'{mergedSoftex[i][2]}|'
            found = True
        
        # Check if record has secondary number    
        if mergedSoftex[i][2] != '0':
          # Check if secondary number is in the numbers of this record
          if mergedSoftex[i][2] in numbers: 
            # Check if unique id is already added
            if mergedSoftex[i][0] not in allContacts[j][3]:
              allContacts[j][3] += f'{mergedSoftex[i][0]}|'
            # Check if the primary of the secondary is in the numbers
            if mergedSoftex[i][1] not in numbers:
              allContacts[j][1] += f'{mergedSoftex[i][1]}|'
            found = True
            
        j += 1
      
      # Check if the number wasnt found == NO DUPELICATE
      if not found:
        if mergedSoftex[i][1] != '0' and mergedSoftex[i][2] != '0':
          allContacts.append([f'{myID}', '|' + mergedSoftex[i][1] + '|' + mergedSoftex[i][2] + '|', '', '|' + mergedSoftex[i][0] + '|', '|', '|', '|'])
        elif mergedSoftex[i][1] != '0':
          allContacts.append([f'{myID}', '|' + mergedSoftex[i][1] + '|', '', '|' + mergedSoftex[i][0] + '|', '|', '|', '|'])
        else:
          allContacts.append([f'{myID}', '|' + mergedSoftex[i][2] + '|', '', '|' + mergedSoftex[i][0] + '|', '|', '|', '|'])
        myID += 1
  
  # Start filling the dictionary with VTigerAccount numbers take duplicates in mind
  mergedVTigerAccount = merge(vtigerAccountPhone, vtigerAccountOtherPhone)
  for i in range(len(mergedVTigerAccount)):
    # Check if the number isnt in allContacts
    j = 0
    end = len(allContacts)
    found = False
    while j < end:
      numbers = allContacts[j][1]
      # Check if record has primary number
      if mergedVTigerAccount[i][1] != '0':
        # Check if primary number is in the numbers of this record
        if mergedVTigerAccount[i][1] in numbers:
          # Check if unique id is already added
          if mergedVTigerAccount[i][0] not in allContacts[j][4]:
            allContacts[j][4] += f'{mergedVTigerAccount[i][0]}|'
          # Check if the secondary of the primary is in the numbers
          if mergedVTigerAccount[i][2] not in numbers:
            allContacts[j][1] += f'{mergedVTigerAccount[i][2]}|'
          found = True
      
      # Check if record has secondary number   
      if mergedVTigerAccount[i][2] != '0':
        # Check if secondary number is in the numbers of this record
        if mergedVTigerAccount[i][2] in numbers: 
          # Check if unique id is already added
          if mergedVTigerAccount[i][0] not in allContacts[j][4]:
            allContacts[j][4] += f'{mergedVTigerAccount[i][0]}|'
          # Check if the primary of the secondary is in the numbers
          if mergedVTigerAccount[i][1] not in numbers:
            allContacts[j][1] += f'{mergedVTigerAccount[i][1]}|'
          found = True
          
      j += 1
      
    # Check if the number wasnt found == NO DUPELICATE
    if not found:
      if mergedVTigerAccount[i][1] != '0' and mergedVTigerAccount[i][2] != '0':
        allContacts.append([f'{myID}', '|' + mergedVTigerAccount[i][1] + '|' + mergedVTigerAccount[i][2] + '|', '', '|', '|' + mergedVTigerAccount[i][0] + '|', '|', '|'])
      elif mergedVTigerAccount[i][1] != '0':
        allContacts.append([f'{myID}', '|' + mergedVTigerAccount[i][1] + '|', '', '|', '|' + mergedVTigerAccount[i][0] + '|', '|', '|'])
      else:
        allContacts.append([f'{myID}', '|' + mergedVTigerAccount[i][2] + '|', '', '|', '|' + mergedVTigerAccount[i][0] + '|', '|', '|'])
      myID += 1
  
  # Start filling the dictionary with VTigerContactDetails numbers take duplicates in mind
  mergedVTigerContact = merge(vtigerContactDetailsMobile, vtigerContactDetailsPhone)
  maxCompany = myID
  for i in range(len(mergedVTigerContact)):
    # Check if the number isnt in allContacts
    j = 0
    end = len(allContacts)
    found = False
    hasCompany = 0
    duplicate = False
    while j < end:
      numbers = allContacts[j][1]
      # Check if record has primary number
      if mergedVTigerContact[i][1] != '0':
        # Check if primary number is in the numbers of this record
        if mergedVTigerContact[i][1] in numbers:
          found = True
          # Check if the record the number was found in is a Company or not
          if allContacts[j][2] == '' and int(allContacts[j][0]) > maxCompany: # NOT COMPANY
            duplicate = True
            # Check if unique id is already added
            if mergedVTigerContact[i][0] not in allContacts[j][5]:
              allContacts[j][5] += f'{mergedVTigerContact[i][0]}|'
            # Check if the secondary of the primary is in the numbers
            if mergedVTigerContact[i][2] not in numbers:
              allContacts[j][1] += f'{mergedVTigerContact[i][2]}|'
            break

          elif allContacts[j][2] == '' and int(allContacts[j][0]) <= maxCompany: # COMPANY
            hasCompany = j
            
          elif allContacts[j][2] != '': 
            duplicate = True
            # Check if unique id is already added
            if mergedVTigerContact[i][0] not in allContacts[j][5]:
              allContacts[j][5] += f'{mergedVTigerContact[i][0]}|'
            # Check if the secondary of the primary is in the numbers
            if mergedVTigerContact[i][2] not in numbers:
              allContacts[j][1] += f'{mergedVTigerContact[i][2]}|'
            break

      # Check if record has secondary number
      if mergedVTigerContact[i][2] != '0':
        # Check if secondary number is in the numbers of this record
        if mergedVTigerContact[i][2] in numbers:
          found = True
          # Check if the record the number was found in is a Company or not
          if allContacts[j][2] == '' and int(allContacts[j][0]) > maxCompany: # NOT COMPANY
            duplicate = True
            # Check if unique id is already added
            if mergedVTigerContact[i][0] not in allContacts[j][5]:
              allContacts[j][5] += f'{mergedVTigerContact[i][0]}|'
            # Check if the primary of the secondary is in the numbers
            if mergedVTigerContact[i][1] not in numbers:
              allContacts[j][1] += f'{mergedVTigerContact[i][1]}|'
            break

          elif allContacts[j][2] == '' and int(allContacts[j][0]) <= maxCompany: # COMPANY
            hasCompany = j
            
          elif allContacts[j][2] != '': 
            duplicate = True
            # Check if unique id is already added
            if mergedVTigerContact[i][0] not in allContacts[j][5]:
              allContacts[j][5] += f'{mergedVTigerContact[i][0]}|'
            # Check if the primary of the secondary is in the numbers
            if mergedVTigerContact[i][1] not in numbers:
              allContacts[j][1] += f'{mergedVTigerContact[i][1]}|'
            break
          
      j += 1
      
    if not found:
      if mergedVTigerContact[i][1] != '0' and mergedVTigerContact[i][2] != '0':
        allContacts.append([f'{myID}', f'|{mergedVTigerContact[i][1]}|{mergedVTigerContact[i][2]}|', '', '|', '|', f'|{mergedVTigerContact[i][0]}|', '|'])
      elif mergedVTigerContact[i][1] != '0':
        allContacts.append([f'{myID}', f'|{mergedVTigerContact[i][1]}|', '', '|', '|', f'|{mergedVTigerContact[i][0]}|', '|'])
      else:
        allContacts.append([f'{myID}', f'|{mergedVTigerContact[i][2]}|', '', '|', '|', f'|{mergedVTigerContact[i][0]}|', '|'])
      myID += 1
    else:
      if not duplicate:
        if hasCompany != 0:
          if mergedVTigerContact[i][1] != '0' and mergedVTigerContact[i][2] != '0':
            allContacts.append([f'{myID}', f'|{mergedVTigerContact[i][1]}|{mergedVTigerContact[i][2]}|', f'{allContacts[hasCompany][0]}', '|', '|', f'|{mergedVTigerContact[i][0]}|', '|'])
          elif mergedVTigerContact[i][1] != '0':
            allContacts.append([f'{myID}', f'|{mergedVTigerContact[i][1]}|', f'{allContacts[hasCompany][0]}', '|', '|', f'|{mergedVTigerContact[i][0]}|', '|'])
          else:
            allContacts.append([f'{myID}', f'|{mergedVTigerContact[i][2]}|', f'{allContacts[hasCompany][0]}', '|', '|', f'|{mergedVTigerContact[i][0]}|', '|'])
          myID += 1
  
  # Start filling the dictionary with WolfApp numbers take duplicates in mind
  # 0: num 1: id
  for i in range(len(wolfmobiles)):
    # Check if the number isnt in allContacts
    j = 0
    end = len(allContacts)
    found = False
    hasCompany = 0
    duplicate = False
    while j < end:
      numbers = allContacts[j][1]
      # Check if primary number is in the numbers of this record
      if wolfmobiles[i][0] in numbers:
        found = True
        # Check if the record the number was found in is a Company or not
        if allContacts[j][2] == '' and int(allContacts[j][0]) > maxCompany: # NOT COMPANY
          duplicate = True
          # Check if unique id is already added
          if str(wolfmobiles[i][1]) not in allContacts[j][6]:
            allContacts[j][6] += f'{wolfmobiles[i][1]}|'
          break
        elif allContacts[j][2] == '' and int(allContacts[j][0]) <= maxCompany: # COMPANY
          hasCompany = j
          
        elif allContacts[j][2] != '': 
          duplicate = True
          # Check if unique id is already added
          if str(wolfmobiles[i][1]) not in allContacts[j][6]:
            allContacts[j][6] += f'{wolfmobiles[i][1]}|'
          break
        
      j += 1
      
    if not found:
      allContacts.append([f'{myID}', f'|{wolfmobiles[i][0]}|', '', '|', '|', '|', f'|{wolfmobiles[i][1]}|'])
      myID += 1
    else:
      if not duplicate:
        if hasCompany != 0:
          allContacts.append([f'{myID}', f'|{wolfmobiles[i][0]}|', f'{allContacts[hasCompany][0]}', '|', '|', '|', f'|{wolfmobiles[i][1]}|'])
          myID += 1

  orderedAllContacts = orderContacts(allContacts)
  # Add Softex Names
  for contact in orderedAllContacts:
    # ADD Universal Name field
    contact.append('')
    # Add Softex other Names
    contact.append('|')
    # Get Serials and split to use each serial when adding data
    serials = contact[3]
    cleanSerials = serials.split('|')
    cleanSerials.remove('')
    cleanSerials.remove('')
    # Add Softex Old Mobiles
    contact.append('|')
    # Add Softex climit
    contact.append('|')
    # Add Softex City
    contact.append('')
    # Add Softex Area
    contact.append('|')
    # Add Softex ctype
    contact.append('|')
    # Add Softex Branch
    contact.append('|')
    # Add Softex Salesman
    contact.append('|')
    # Add Softex taxesno
    contact.append('|')
    # Add Softex commercialno
    contact.append('|')
    # Add Softex email
    contact.append('|')
    # Add Softex freedays
    contact.append('|')
    # Add Softex scode
    contact.append('|')
    # Add Softex status
    contact.append('|')
    # Add Softex paymenttype
    contact.append('|')
    # Add Softex allowcoin
    contact.append('|')
    # Add Softex person
    contact.append('|')
    # Add Softex address
    contact.append('|')
    
    for serial in cleanSerials:
      for data in softexData:
        if int(serial) == int(data[0]):
          # Name
          data[1] = re.sub(namePattern, '', data[1])
          if contact[7] == '':
            contact[7] += f'{data[1]}'
          else:
            if shouldAdd(data[1], contact[8]):
              contact[8] += f'{data[1]}|'
          # Mobiles
          if data[2] != '':
            contact[9] += f'{data[2]}|'
          if data[3] != '':
            contact[9] += f'{data[3]}|'
          # Climit
          contact[10] += f'{data[4]}|'
          # City
          SoftexCityName = SoftexCity[str(data[5])]
          if contact[11] == '':
            contact[11] += SoftexCityName
          else:
            if SoftexCityName not in contact[11]:
              contact[11] += f'|{SoftexCityName}'
          # Area
          SoftexAreaName = SoftexArea[str(data[6])] 
          contact[12] += f'{SoftexAreaName}|'
          # ctype
          SoftexCtypeName = SoftexCtype[str(data[7])]
          contact[13] += f'{SoftexCtypeName}|'
          # Branch
          SoftexBranchName = SoftexBranch[str(data[8])]
          contact[14] += f'{SoftexBranchName}|'
          # Salesman
          SoftexSalesmanName = SoftexSalesman[str(data[9])]
          contact[15] += f'{SoftexSalesmanName}|'
          # Taxesno
          contact[16] += f'{data[10]}|'
          # Commercialno
          contact[17] += f'{data[11]}|'
          # Email
          contact[18] += f'{data[12]}|'
          # Freedays
          contact[19] += f'{data[13]}|'
          # Scode
          contact[20] += f'{data[14]}|'
          # Status
          contact[21] += f'{data[15]}|'
          # Paymenttype
          contact[22] += f'{data[16]}|'
          # AllowCoin
          contact[23] += f'{data[17]}|'
          # Person
          data[18] = re.sub(namePattern, '', data[18])
          contact[24] += f'{data[18]}|'
          # Address
          contact[25] += f'{data[19]}|'

    # ADD VTAccount accountname
    contact.append('|')
    # Clean Accountids to loop through them
    accountids = contact[4]
    cleanAccountids = accountids.split('|')
    cleanAccountids.remove('')
    cleanAccountids.remove('')
    # Add VTAccount Old Numbers
    contact.append('|')
    # Add isconvertedfromlead
    contact.append('|')
    # Add accoount_no
    contact.append('|')
    # Add Street Details
    contact.append('|')
    # Add Building No
    contact.append('|')
    # Add Country
    contact.append('')
    # Add ClientType
    contact.append('|')
    # Add WayOfPayment
    contact.append('|')
    # Add Contact Person
    contact.append('|')
    # Add 2nd Contact Person
    contact.append('|')
    # Add Organization Type
    contact.append('|')
    # Add SalesMan
    contact.append('|')
    # Add Location Link
    contact.append('|')
    # Add Area
    contact.append('|')
    # Add Brands
    contact.append('|')
    # Add State
    contact.append('|')
    # Add Converted Lead ID
    contact.append('|')
    
    for accountid in cleanAccountids:
      for data in vtigerAccountsData:
        if int(accountid) == int(data[0]):
          # Name
          data[1] = re.sub(namePattern, '', data[1])
          if contact[7] == '':
            contact[7] += data[1]
          elif shouldAdd(data[1], contact[26]):
            contact[26] += f'{data[1]}|'
          # Mobiles
          if data[2] != '':
            contact[27] += f'{data[2]}|'
          if data[3] != '':
            contact[28] += f'{data[3]}|'
          # Isconvertedfromlead
          contact[28] += f'{data[4]}|'
          # Account No
          contact[29] += f'{data[5]}|'
      # Add Extra data 
      for data in vtigerAccountsExtraData:
        if int(accountid) == int(data[0]):
          # Streeet Detaiks
          contact[30] += f'{data[1]}|'
          # Building No
          contact[31] += f'{data[2]}|'
          # Country
          if contact[32] == '':
            contact[32] += f'{data[3]}'
          else:
            if data[3] not in contact[32]:
              contact[32] += f'|{data[3]}'
          # Client Type
          contact[33] += f'{data[4]}|'
          # Way Of Payment
          contact[34] += f'{data[5]}|'
          # Contact Peson 1 & 2
          data[6] = re.sub(namePattern, '', data[6])
          data[7] = re.sub(namePattern, '', data[7])
          # 1
          contact[35] += f'{data[6]}|'
          # 2
          contact[36] += f'{data[7]}|'
          # Organization Type
          contact[37] += f'{data[8]}|'
          # SalesMan
          data[9] = re.sub(namePattern, '', data[9])
          contact[38] += f'{data[9]}|'
          # Location Link
          contact[39] += f'{data[10]}|'
          # Area
          contact[40] += f'{data[11]}|'
          # Brands
          contact[41] += f'{data[12]}|'
          # State
          contact[42] += f'{data[13]}|'
          # Converted Lead ID
          contact[43] += f'{data[14]}|'
          
    # ADD VTContact firstname + lastname
    contact.append('|')
    # Add VTContact Old Mobiles
    contact.append('|')
    # Add Email
    contact.append('|')
    # Add ContactNo
    contact.append('|')
    # Add Salutation
    contact.append('|')
    # Add Vehicle Type
    contact.append('|')
    # Add Contact Brand
    contact.append('|')
    # Add Year of Made
    contact.append('|')
    # Add Client Point
    contact.append('|')
    # Add Add Point
    contact.append('|')
    # Clean VTContact ids to loop through them
    contactids = contact[5]
    cleanContactids = contactids.split('|')
    cleanContactids.remove('')
    cleanContactids.remove('')
    # Add Name in Arabic
    contact.append('|')
    # Add Landline
    contact.append('|')
    # Add Client Type
    contact.append('|')
    # Add District
    contact.append('|')
    # Add Street Details
    contact.append('|')
    # Add Country
    contact.append('')
    # Add City
    contact.append('|')
    # Add Mobile 2
    contact.append('')
    # Add Model
    contact.append('|')
    # Add Call Feedback
    contact.append('|')
    # Add Vehicle Service Tracker
    contact.append('|')
    # Add App User Experience
    contact.append('|')
    # Add Order
    contact.append('|')
    # Add Points Awareness
    contact.append('|')
    # Add Other Comments
    contact.append('|')
    # Add Client Case
    contact.append('|')
    # Add Next Action Date
    contact.append('|')
    # Converted Lead ID
    contact.append('|')
    
    for contactid in cleanContactids:
      for data in vtigerContactsData:
        if int(contactid) == int(data[0]):
          data[1] = re.sub(namePattern, '', data[1])
          data[2] = re.sub(namePattern, '', data[2])
          # Name
          if contact[7] == '':
            contact[7] += f'{data[1]} {data[2]}'
          else:
            if shouldAdd(f'{data[1]} {data[2]}', contact[44]):
              contact[44] += f'{data[1]} {data[2]}|'
          # Old Mobiles
          if data[3] != '':
            contact[45] += f'{data[3]}|'
          if data[4] != '':
            contact[45] += f'{data[4]}|'
          # Email
          contact[46] += f'{data[5]}|'
          # ContactNo
          contact[47] += f'{data[6]}|'
          # Salutation
          contact[48] += f'{data[7]}|'
          # Vehicle Type
          contact[49] += f'{data[8]}|'
          # Contact Brand
          contact[50] += f'{data[9]}|'
          # Year Of Made
          contact[51] += f'{data[10]}|'
          # Client Point
          contact[52] += f'{data[11]}|'
          # Add Point
          contact[53] += f'{data[12]}|'
      
      for data in vtigerContactsExtraData:
        if int(contactid) == int(data[0]):
          # Name in Arabic
          data[1] = re.sub(namePattern, '', data[1])
          contact[54] += f'{data[1]}|'
          # Landline
          contact[55] += f'{data[2]}|'
          # Client Type          
          contact[56] += f'{data[3]}|'
          # District
          contact[57] += f'{data[4]}|'
          # Street Details
          contact[58] += f'{data[5]}|'
          # Country
          if contact[59] == '':
            contact[59] += f'{data[6]}'
          else:
            if data[6] not in contact[59]:
              contact[59] += f'|{data[6]}'
          # City
          contact[60] += f'{data[7]}|'
          # Mobile 2
          m1 = data[8]
          m2 = data[9]
          if contact[61] == '':
            if m1 != '':
              contact[61] = m1
            elif m2 != '':
              contact[61] = m2
          # Model
          contact[62] += f'{data[10]}|'
          # Call Feedback
          contact[63] += f'{data[11]}|'
          # Vehicle Service Tracker
          contact[64] += f'{data[12]}|'
          # App User Experience
          contact[65] += f'{data[13]}|'
          # Order
          contact[66] += f'{data[14]}|'
          # Points Awareness
          contact[67] += f'{data[15]}|'
          # Other Comments
          contact[68] += f'{data[16]}|'
          # Client Case
          contact[69] += f'{data[17]}|'
          # Next Action Data
          contact[70] += f'{data[18]}|'
          # Converted Lead ID
          contact[71] += f'{data[19]}|'
                     
    # ADD WolfApp ClientName
    contact.append('|')
    # Add WolfApp Old Mobile
    contact.append('|')
    # Add WolfApp Email
    contact.append('|')
    # Add WolfApp City
    contact.append('|')
    # Add WolfApp ClientPasswordPlain
    contact.append('|')
    # Add WolfApp ClientStatus
    contact.append('|')
    # Add WolfApp ClientPoints
    contact.append('|')
    # Clean Wolf IDs
    wolfids = contact[6]
    cleanWolfids = wolfids.split('|')
    cleanWolfids.remove('')
    cleanWolfids.remove('')
    for wolfid in cleanWolfids:
      for data in wolfData:
        if int(wolfid) == int(data[0]):
          # Name
          data[1] = re.sub(namePattern, '', data[1])
          if contact[7] == '':
            contact[7] += f'{data[1]}'
          else:
            if shouldAdd(f'{data[1]}', contact[72]):
              contact[72] += f'{data[1]}|'
          # Old Mobile
          if data[2] != '':
            contact[73] += f'{data[2]}|'
          # Email
          contact[74] += f'{data[3]}|'
          # City
          try:
            WolfCityName = WolfCity[str(data[4])]
          except:
            WolfCityName = ''
          contact[75] += f'{WolfCityName}|'
          # Client Password Plain
          contact[76] += f'{data[5]}|'
          # ClientStatus
          contact[77] += f'{data[6]}|'
          # Client Points
          contact[78] += f'{data[7]}|'
          
    # ADD Is Company w Change Company ID to Related Company
    contact.append('')
    if contact[2] == '':
      if contact[3] != '|' or contact[4] != '|':
        if 'Delivery' not in contact[13]:
          contact[79] = '1'
          contact.append('')
        else:
          contact[79] = '0'
          contact.append('')
      else:
          contact[79] = '0'
          contact.append('')
    else:
      contact[79] = '0'
      relatedCompanyID = contact[2]
      for c in orderedAllContacts:
        if c[0] == relatedCompanyID:
          relatedCompanyName = c[7]
          break
      contact.append(relatedCompanyName)
      
  return orderedAllContacts

def orderContacts(allContacts):
  ordered = []
  # Loop through contacts
  for i in range(len(allContacts)):
    # Check if its a company
    if allContacts[i][2] == '':
      # Append to ordered
      ordered.append(allContacts[i])
      # Find all contacts related to this company
      for j in range(len(allContacts)):
        # Check if a number has a CompanyID == the Company's ID
        if allContacts[i][0] == allContacts[j][2]:
          ordered.append(allContacts[j])
  
  return ordered

def CamelCaseName(name):
  name.lower()
  name = name.split(' ')
  name = list(filter(lambda x: x != '', name))
  camelName = ''
  for i, n in enumerate(name):
    camelName += n.capitalize()
    if i != len(name) - 1:
      camelName += ' '
  return camelName

def FormatNames(names):
  formattedNames = []
  names = names.split('|')
  names = list(filter(lambda x: x != '', names))
  for name in names:
    formattedNames.append(CamelCaseName(name))
  return formattedNames

def CombineAddress(a1,a2):
  a3 = []
  for i in range(len(a1)):
    try:
      a3.append(f'{a1[i]}, {a2[i]}')
    except:
      a3.append(f'{a1[i]}')
  return a3
  
def refactorData(data):
  refactoredData = []
  for record in data:
    newRecord = []
    
    # Name 7
    name = record[7]
    name = CamelCaseName(name)
    newRecord.append(name)
    
    # Is A Company
    isCompany = record[79]
    newRecord.append(isCompany)
    
    # Related Company
    relatedCompanyName = record[80]
    relatedCompanyName = CamelCaseName(relatedCompanyName)
    newRecord.append(relatedCompanyName)

    # Other Names
    # 8: Softex, 26: VTA, 44: VTC, 72: WolfApp, Filled in order
    sNames, vaNames, vcNames, wNames = record[8], record[26], record[44], record[72]
    otherNames = ''
    # Softex
    sNames = FormatNames(sNames)
    for n in sNames:
      if n not in name:
        if n not in otherNames:
          otherNames += f'|{n}'
    # VTA
    vaNames = FormatNames(vaNames)
    for n in vaNames:
      if n not in name:
        if n not in otherNames:
          otherNames += f'|{n}'
    # VTC
    vcNames = FormatNames(vcNames)
    for n in vcNames:
      if n not in name:
        if n not in otherNames:
          otherNames += f'|{n}'
    # Wolf
    wNames = FormatNames(wNames)
    for n in wNames:
      if n not in name:
        if n not in otherNames:
          otherNames += f'|{n}'
    newRecord.append(otherNames[1:])
    
    # Email
    # 18: Softex, 46: VTAccount, 74: WolfApp, Filled in order
    sEmail, vEmail, wEmail = record[18], record[46], record[74]
    Email = ''
    otherEmails = ''
    # Softex
    sEmail = sEmail.split('|')
    sEmail = list(filter(lambda x: x != '', sEmail))
    if sEmail != []:
      Email = sEmail[0]
      for i in range(1, len(sEmail)):
        if sEmail[i] not in otherEmails:
          otherEmails += f'|{sEmail[i]}'
    # VT
    vEmail = vEmail.split('|')
    vEmail = list(filter(lambda x: x != '', vEmail))
    if vEmail != []:
      if Email == '':
        Email = vEmail[0]
        for i in range(1, len(vEmail)):
          if vEmail[i] not in otherEmails:
            otherEmails += f'|{vEmail[i]}'
      else:
        for email in vEmail:
          if email not in Email:
            if email not in otherEmails:
              otherEmails += f'|{email}'
    # Wolf
    wEmail = wEmail.split('|')
    wEmail = list(filter(lambda x: x != '', wEmail))
    if wEmail != []:
      if Email == '':
        Email = wEmail[0]
        for i in range(1, len(wEmail)):
          if wEmail[i] not in otherEmails:
            otherEmails += f'|{wEmail[i]}'   
      else:
        for email in wEmail:
          if email not in Email:
            if email not in otherEmails:
              otherEmails += f'|{email}'
    newRecord.append(Email)
    newRecord.append(otherEmails[1:])
    
    # Mobiles
    mobiles = record[1]
    newRecord.append(mobiles[1:len(mobiles)-1])
    
    # Street Address
    # 25: Softex, 30 + 31: VTA, 57 + 58: VTC
    address = ''
    sAddress, vaAddress1, vaAddress2, vcAddress1, vcAddress2, wAddress = record[25], record[30], record[31], record[57], record[58], record[71]
    vaAddress1 = vaAddress1[1:len(vaAddress1)-1]
    vaAddress2 = vaAddress2[1:len(vaAddress2)-1]
    vaAddress = CombineAddress(vaAddress1,vaAddress2)
    vcAddress1 = vcAddress1[1:len(vcAddress1)-1]
    vcAddress2 = vcAddress2[1:len(vcAddress2)-1]
    vcAddress = CombineAddress(vcAddress1,vcAddress2)
    # Softex
    sAddress = sAddress.split('|')
    sAddress = list(filter(lambda x: x != '', sAddress))
    for a in sAddress:
      if a not in address:
        address += f'|{a}'
    # VTA
    vaAddress = list(filter(lambda x: x != '', vaAddress))
    for a in vaAddress:
      if a not in address:
        address += f'|{a}'
    # VTC
    vcAddress = list(filter(lambda x: x != '', vcAddress))
    for a in vcAddress:
      if a not in address:
        address += f'|{a}'
    # WolfApp
    wAddress = wAddress.split('|')
    wAddress = list(filter(lambda x: x != '', wAddress))
    for a in wAddress:
      if a not in address:
        address += f'|{a}'
    newRecord.append(address[1:])

    # Area
    # 12: Softex, 40: VTA
    area = ''
    sArea, vaArea = record[12], record[40]
    # Softex
    sArea = sArea.split('|')
    sArea = list(filter(lambda x: x != '', sArea))
    for ar in sArea:
      if ar not in area:
        area += f'|{ar}'
    # VTA
    vaArea = vaArea.split('|')
    vaArea = list(filter(lambda x: x != '', vaArea))
    for ar in vaArea:
      if ar not in area:
        area += f'|{ar}'
    newRecord.append(area[1:])
    
    # State
    # 42: VTA
    State = ''
    vStates = record[42]
    vStates = vStates.split('|')
    vStates = list(filter(lambda x: x != '', vStates))
    for s in vStates:
      if s not in State:
        State += f'|{s}'
    newRecord.append(State[1:])
    
    # City
    # 11: Softex, 42: VTA, 60: VTC, 75: WolfApp
    City = ''
    sCity, vaCity, vcCity, wCity = record[11], record[42], record[60], record[75]
    # Softex
    if sCity not in City:
      City += sCity
    # VTA
    vaCity = vaCity.split('|')
    vaCity = list(filter(lambda x: x != '', vaCity))
    for c in vaCity:
      if c not in vaCity:
        City += f'|{c}'
    # VTC
    vcCity = vcCity.split('|')
    vcCity = list(filter(lambda x: x != '', vcCity))
    for c in vcCity:
      if c not in vcCity:
        City += f'|{c}'
    # WolfApp
    wCity = wCity.split('|')
    wCity = list(filter(lambda x: x != '', wCity))
    for c in wCity:
      if c not in wCity:
        City += f'|{c}'   
    newRecord.append(City[1:])
    

        
        
    refactoredData.append(newRecord)
  refactoredDataDf = pd.DataFrame(
    refactoredData,
    columns=[
      'Name',
      'Is A Company',
      'Related Company',
      'Other Names',
      'Email',
      'Other Emails',
      'Mobiles',
      'Street Address',
      'Area',
      'State',
      'City'
    ]
  )
  file_name = 'RefactoredV3.xlsx'
  refactoredDataDf.to_excel(file_name)
    
  
def exportExcel(allContacts):
  allContactsDf = pd.DataFrame(
    allContacts,
    columns=[
      'ID',  # 0
      'Mobiles',  # 1
      'CompanyID',  # 2
      'Softex serial',  # 3
      'VTAccount accountid',  # 4
      'VTContactDetails contactid',  # 5
      'WolfApp IDClient',  # 6
      'Name',  # 7
      
      'Softex otherNames',  # 8
      'Softex Old Mobiles',  # 9
      'Softex climit',  # 10
      'Softex City',  # 11
      'Softex Area',  # 12
      'Softex ctype',  # 13
      'Softex branch',  # 14
      'Softex salesman',  # 15
      'Softex taxesno',  # 16
      'Softex commercialno',  # 17
      'Softex email',  # 18
      'Softex freedays',  # 19
      'Softex scode',  # 20
      'Softex status',  # 21
      'Softex paymenttype',  # 22
      'Softex allowcoin',  # 23
      'Softex person',  # 24
      'Softex address',  # 25
      
      'VTAccount accountname',  # 26
      'VTAccount Old Mobiles',  # 27
      'VTAccount isconvertedfromlead',  # 28
      'VTAccount AccountNo',  # 29
      'VTAccount Street Details',  # 30
      'VTAccount BuildingNo',  # 31
      'VTAccount Country',  # 32
      'VTAccount Client Type',  # 33
      'VTAccount Way Of Payment',  # 34
      'VTAccount Contact Person 1',  # 35
      'VTAccount Contact Person 2',  # 36
      'VTAccount Organization Type',  # 37
      'VTAccount Salesman',  # 38
      'VTAccount Location Link',  # 39
      'VTAccount Area',  # 40
      'VTAccount Brands',  # 41
      'VTAccount States',  # 42
      'VTAccount Converted Lead ID',  # 43
      
      'VTContacts otherNames',  # 44
      'VTContacts Old Mobiles',  # 45
      'VTContacts Email',  # 46
      'VTContacts ContactNo',  # 47
      'VTContacts Salutation',  # 48
      'VTContacts Vehicle Type',  # 49
      'VTContacts Contact Brand',  # 50
      'VTContacts Year Of Made',  # 51
      'VTContacts Client Point',  # 52
      'VTContacts Add Point',  # 53
      'VTContacts Name in Arabic',  # 54
      'VTContacts Landline',  # 55
      'VTContacts Client Type',  # 56
      'VTContacts District',  # 57
      'VTContacts Street Details',  # 58
      'VTContacts Country',  # 59
      'VTContacts City',  # 60
      'VTContacts Mobile 2',  # 61
      'VTContacts Model',  # 62
      'VTContacts Call Feedback',  # 63
      'VTContacts Vehicle Service Tracker',  # 64
      'VTContacts App User Experience',  # 65
      'VTContacts Order',  # 66
      'VTContacts Points Awareness',  # 67
      'VTContacts Other Comments',  # 68
      'VTContacts Client Case',  # 69
      'VTContacts Next Action Date',  # 70
      'VTContacts Converted Lead ID',  # 71
      
      'WolfApp ClientName',  # 72
      'WolfApp Old Mobiles',  # 73
      'WolfApp ClientEmail',  # 74
      'WolfApp City',  # 75
      'WolfApp ClientPasswordPlain',  # 76
      'WolfApp ClientStatus',  # 77
      'WolfApp ClientPoints',  # 78
      
      'Is a company',  # 79
      'Related company'  # 80
    ]
  )
  column_names = [
    'ID',
    
    'Name',
    'Is a company',
    'Related company',
    
    'Mobiles',
    'Softex Old Mobiles',
    'VTAccount Old Mobiles',
    'VTContacts Old Mobiles',
    'WolfApp Old Mobiles',
    
    'CompanyID',
    'Softex serial',
    'VTAccount accountid',
    'VTContactDetails contactid',
    'WolfApp IDClient',
    
    'Softex otherNames',
    'VTAccount accountname',
    'VTContacts otherNames',
    'WolfApp ClientName',
    
    'Softex climit',
    'Softex City',
    'Softex Area',
    'Softex ctype',
    'Softex branch',
    'Softex salesman',
    'Softex taxesno',
    'Softex commercialno',
    'Softex email',
    'Softex freedays',
    'Softex scode',
    'Softex status',
    'Softex paymenttype',
    'Softex allowcoin',
    'Softex person',
    'Softex address',
    
    'VTAccount AccountNo',
    'VTAccount isconvertedfromlead',
    'VTAccount Street Details',
    'VTAccount BuildingNo',
    'VTAccount Country',
    'VTAccount Client Type',
    'VTAccount Way Of Payment',
    'VTAccount Contact Person 1',
    'VTAccount Contact Person 2',
    'VTAccount Organization Type',
    'VTAccount Salesman',
    'VTAccount Location Link',
    'VTAccount Area',
    'VTAccount Brands',
    'VTAccount States',
    'VTAccount Converted Lead ID',
    
    'VTContacts Email',
    'VTContacts ContactNo',
    'VTContacts Salutation',
    'VTContacts Vehicle Type',
    'VTContacts Contact Brand',
    'VTContacts Year Of Made',
    'VTContacts Client Point',
    'VTContacts Add Point',
    'VTContacts Name in Arabic',
    'VTContacts Landline',
    'VTContacts Client Type',
    'VTContacts District',
    'VTContacts Street Details',
    'VTContacts Country',
    'VTContacts City',
    'VTContacts Mobile 2',
    'VTContacts Model',
    'VTContacts Call Feedback',
    'VTContacts Vehicle Service Tracker',
    'VTContacts App User Experience',
    'VTContacts Order',
    'VTContacts Points Awareness',
    'VTContacts Other Comments',
    'VTContacts Client Case',
    'VTContacts Next Action Date',
    'VTContacts Converted Lead ID',
    
    'WolfApp ClientEmail',
    'WolfApp City',
    'WolfApp ClientPasswordPlain',
    'WolfApp ClientStatus',
    'WolfApp ClientPoints',
  ]
  allContactsDf = allContactsDf.reindex(columns=column_names)
  file_name = 'AllContactsV9.xlsx'
  allContactsDf.to_excel(file_name)
  
# Getting Softex Data
print('Gathering Softex Data...')
softexPhones, softexMobiles, softexData = softex()
print('Cleaning Softex Data...')
correctedSoftexPhones, brokenSoftexPhones = phoneCleaner(softexPhones)
correctedSoftexMobiles, brokenSoftexMobiles = phoneCleaner(softexMobiles)
print('------SUCCESS------')

# Getting VTiger Data
print('Gathering VTiger Data...')
vtigerContactDetailsMobiles, vtigerAccountPhone, vtigerContactDetailsPhone, vtigerAccountOtherPhone, vtigerAccountsData, vtigerContactsData, vtigerAccountsExtraData, vtigerContactsExtraData = vtiger()
print('Cleaning VTiger Data...')
correctedVtigerContactDetailsMobile, brokenVtigerContactDetailsMobile = phoneCleaner(vtigerContactDetailsMobiles)
correctedVtigerAccountPhone, brokenVtigerAccountPhone = phoneCleaner(vtigerAccountPhone)
correctedVtigerAccountOtherPhone, brokenVtigerAccountOtherPhone = phoneCleaner(vtigerAccountOtherPhone)
correctedVtigerContactDetailsPhone, brokenVtigerContactDetailsPhone = phoneCleaner(vtigerContactDetailsPhone)
print('------SUCCESS------')

# Getting WolfApp Data
print('Gathering WolfApp Data...')
wolfMobiles, wolfData = wolfapp()
print('Cleaning WolfApp Data...')
correctedWolf, brokenWolf = phoneCleaner(wolfMobiles)
print('------SUCCESS------')

# Merging all gathered and cleaned data
print('Merging Softex, VTiger and WolfApp...')
allContacts = getAllContacts(
  correctedSoftexPhones,
  correctedVtigerContactDetailsMobile,
  correctedVtigerAccountPhone,
  correctedWolf,
  correctedSoftexMobiles,
  correctedVtigerContactDetailsPhone,
  correctedVtigerAccountOtherPhone,
  softexData,
  vtigerAccountsData,
  vtigerContactsData,
  wolfData,
  vtigerAccountsExtraData,
  vtigerContactsExtraData
)
print('------Merge COMPLETE------')
print('Exporting to Excel...')
refactorData(allContacts)
#exportExcel(allContacts) 
print('------Export COMPLETE------')

# Timing Program
print(f'The Program took {time.time() - start_time} seconds to execute')
