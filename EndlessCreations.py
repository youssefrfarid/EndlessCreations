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
  '1054': 'Lagence'
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
  
  cursor.execute('SELECT serial, name, phone, mobile, climit, city, area, ctype, branch, salesman, taxesno, commercialno, email, freedays, scode, status, paymenttype, allowcoin, person FROM dbo.clients')
  softexData = cursor.fetchall()
   
  return softexPhone, softexMobile, softexData

# Conntect to VTiger
def vtiger():
  open_ssh_tunnel()
  mysql_connect()
  
  dfContactDetailsMobile = run_query("SELECT mobile, contactid FROM vtiger_contactdetails")
  dfContactDetailsPhone = run_query("SELECT phone, contactid FROM vtiger_contactdetails")
  dfContactsData = run_query("SELECT contactid, firstname, lastname, mobile, phone FROM vtiger_contactdetails")
  
  
  dfAccountsPhone = run_query('SELECT phone, accountid FROM vtiger_account')
  dfAccountsOtherPhone = run_query('SELECT otherphone, accountid FROM vtiger_account')
  dfAccountsData = run_query('SELECT accountid, accountname, phone, otherphone, isconvertedfromlead, account_no FROM vtiger_account')
  dfAccountsExtraData = run_query('SELECT accountid, cf_893, cf_895, cf_899, cf_942, cf_956, cf_1599, cf_2027, cf_2057, cf_2137, cf_2177, cf_2209, cf_2455, cf_2457, cf_2528 FROM vtiger_accountscf')
  # id, Street Details, Building No, Country, ClientType, WayOfPayment, Contact Person, 2nd Contact Person, Organization Type, Sales Man, Location Link, Area, Brands, State محافظة, Converted Lead ID 
  
  mysql_disconnect()
  close_ssh_tunnel()
  
  return dfContactDetailsMobile.values, dfAccountsPhone.values, dfContactDetailsPhone.values, dfAccountsOtherPhone.values, dfAccountsData.values, dfContactsData.values, dfAccountsExtraData.values

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
  dfWolfData = pd.read_sql_query('SELECT IDClient, ClientName, ClientPhone FROM endlessc_endless.clients;', connection)
  
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
  vtigerAccountsExtraData
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
          if shouldAdd(data[1], contact[25]):
            contact[25] += f'{data[1]}|'
          # Mobiles
          if data[2] != '':
            contact[26] += f'{data[2]}|'
          if data[3] != '':
            contact[26] += f'{data[3]}|'
          # Isconvertedfromlead
          contact[27] += f'{data[4]}|'
          # Account No
          contact[28] += f'{data[5]}|'
      # Add Extra data 
      for data in vtigerAccountsExtraData:
        if int(accountid) == int(data[0]):
          # Streeet Detaiks
          contact[29] += f'{data[1]}|'
          # Building No
          contact[30] += f'{data[2]}|'
          # Country
          if contact[31] == '':
            contact[31] += f'{data[3]}'
          else:
            if data[3] not in contact[31]:
              contact[31] += f'|{data[3]}'
          # Client Type
          contact[32] += f'{data[4]}|'
          # Way Of Payment
          contact[33] += f'{data[5]}|'
          # Contact Peson 1 & 2
          data[6] = re.sub(namePattern, '', data[6])
          data[7] = re.sub(namePattern, '', data[7])
          # 1
          contact[34] += f'{data[6]}|'
          # 2
          contact[35] += f'{data[7]}|'
          # Organization Type
          contact[36] += f'{data[8]}|'
          # SalesMan
          data[9] = re.sub(namePattern, '', data[9])
          contact[37] += f'{data[9]}|'
          # Location Link
          contact[38] += f'{data[10]}|'
          # Area
          contact[39] += f'{data[11]}|'
          # Brands
          contact[40] += f'{data[12]}|'
          # State
          contact[41] += f'{data[13]}|'
          # Converted Lead ID
          contact[42] += f'{data[14]}|'
          
    # ADD VTContact firstname + lastname
    contact.append('|')
    # Add VTContact Old Mobiles
    contact.append('|')
    # Clean VTContact ids to loop through them
    contactids = contact[5]
    cleanContactids = contactids.split('|')
    cleanContactids.remove('')
    cleanContactids.remove('')
    for contactid in cleanContactids:
      for data in vtigerContactsData:
        if int(contactid) == int(data[0]):
          data[1] = re.sub(namePattern, '', data[1])
          data[2] = re.sub(namePattern, '', data[2])
          
          if contact[7] == '':
            contact[7] += f'{data[1]} {data[2]}'
          else:
            if shouldAdd(f'{data[1]} {data[2]}', contact[43]):
              contact[43] += f'{data[1]} {data[2]}|'
              
          if data[3] != '':
            contact[44] += f'{data[3]}|'
          if data[4] != '':
            contact[44] += f'{data[4]}|'
            
    # ADD WolfApp ClientName
    contact.append('|')
    contact.append('|')
    wolfids = contact[6]
    cleanWolfids = wolfids.split('|')
    cleanWolfids.remove('')
    cleanWolfids.remove('')
    for wolfid in cleanWolfids:
      for data in wolfData:
        if int(wolfid) == int(data[0]):
          data[1] = re.sub(namePattern, '', data[1])
          if contact[7] == '':
            contact[7] += f'{data[1]}'
          else:
            if shouldAdd(f'{data[1]}', contact[45]):
              contact[45] += f'{data[1]}|'
            
          if data[2] != '':
            contact[46] += f'{data[2]}|'

    # ADD Is Company w Change Company ID to Related Company
    contact.append('')
    if contact[2] == '':
      contact[47] = '1'
      contact.append('')
    else:
      contact[48] = '0'
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
  
def exportExcel(allContacts):
  allContactsDf = pd.DataFrame(
    allContacts,
    columns=[
      'ID',
      'Mobiles',
      'CompanyID',
      'Softex serial',
      'VTAccount accountid',
      'VTContactDetails contactid',
      'WolfApp IDClient',
      'Name',
      
      'Softex otherNames',
      'Softex Old Mobiles',
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
      
      'VTAccount accountname',
      'VTAccount Old Mobiles',
      'VTAccount isconvertedfromlead',
      'VTAccount AccountNo',
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
      
      'VTContacts otherNames',
      'VTContacts Old Mobiles',
      
      'WolfApp ClientName',
      'WolfApp Old Mobiles',
      
      'Is a company',
      'Related company'
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
    
    
  ]
  allContactsDf = allContactsDf.reindex(columns=column_names)
  file_name = 'AllContactsV6.4.xlsx'
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
vtigerContactDetailsMobiles, vtigerAccountPhone, vtigerContactDetailsPhone, vtigerAccountOtherPhone, vtigerAccountsData, vtigerContactsData, vtigerAccountsExtraData = vtiger()
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
  vtigerAccountsExtraData
)
print('------Merge COMPLETE------')
print('Exporting to Excel...')
exportExcel(allContacts) 
print('------Export COMPLETE------')

# Timing Program
print(f'The Program took {time.time() - start_time} seconds to execute')
