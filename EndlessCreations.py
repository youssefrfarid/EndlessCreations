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
  
  cursor.execute('SELECT serial, name FROM dbo.clients')
  softexData = cursor.fetchall()
   
  return softexPhone, softexMobile, softexData

# Conntect to VTiger
def vtiger():
  open_ssh_tunnel()
  mysql_connect()
  
  dfContactDetailsMobile = run_query("SELECT mobile, contactid FROM vtiger_contactdetails")
  dfContactDetailsPhone = run_query("SELECT phone, contactid FROM vtiger_contactdetails")
  dfContactsData = run_query("SELECT contactid, firstname, lastname FROM vtiger_contactdetails")
  dfAccountsPhone = run_query('SELECT phone, accountid FROM vtiger_account')
  dfAccountsOtherPhone = run_query('SELECT otherphone, accountid FROM vtiger_account')
  dfAccountsData = run_query('SELECT accountid, accountname FROM vtiger_account')
  
  mysql_disconnect()
  close_ssh_tunnel()
  
  return dfContactDetailsMobile.values, dfAccountsPhone.values, dfContactDetailsPhone.values, dfAccountsOtherPhone.values, dfAccountsData.values, dfContactsData.values

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
  dfWolfData = pd.read_sql_query('SELECT IDClient, ClientName FROM endlessc_endless.clients;', connection)
  
  return dfWolfClients.values, dfWolfData.values

# Exporting Patterns
namePattern = '[^a-zA-Zء-ي]'
# Clean Numbers
onlyNumbersPattern = '[^+\d]'
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
  wolfData
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
    # ADD Softex name
    contact.append('|')
    serials = contact[3]
    cleanSerials = serials.split('|')
    cleanSerials.remove('')
    cleanSerials.remove('')
    for serial in cleanSerials:
      for data in softexData:
        if int(serial) == int(data[0]):
          if shouldAdd(data[1], contact[7]):
            contact[7] += f'{data[1]}|'
    
    # ADD VTAccount accountname
    contact.append('|')
    accountids = contact[4]
    cleanAccountids = accountids.split('|')
    cleanAccountids.remove('')
    cleanAccountids.remove('')
    for accountid in cleanAccountids:
      for data in vtigerAccountsData:
        if int(accountid) == int(data[0]):
          if shouldAdd(data[1], contact[8]):
            contact[8] += f'{data[1]}|'

    # ADD VTContact firstname + lastname
    contact.append('|')
    contactids = contact[5]
    cleanContactids = contactids.split('|')
    cleanContactids.remove('')
    cleanContactids.remove('')
    for contactid in cleanContactids:
      for data in vtigerContactsData:
        if int(contactid) == int(data[0]):
          if shouldAdd(f'{data[1]} {data[2]}', contact[9]):
            contact[9] += f'{data[1]} {data[2]}|'

    # ADD WolfApp ClientName
    contact.append('|')
    wolfids = contact[6]
    cleanWolfids = wolfids.split('|')
    cleanWolfids.remove('')
    cleanWolfids.remove('')
    for wolfid in cleanWolfids:
      for data in wolfData:
        if int(wolfid) == int(data[0]):
          if shouldAdd(f'{data[1]}', contact[10]):
            contact[10] += f'{data[1]}|'
    
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
      'Softex name',
      'VTAccount accountname',
      'VTContacts firstname + lastname',
      'WolfApp ClientName'
    ]
  )
  file_name = 'AllContactsV4.1.xlsx'
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
vtigerContactDetailsMobiles, vtigerAccountPhone, vtigerContactDetailsPhone, vtigerAccountOtherPhone, vtigerAccountsData, vtigerContactsData = vtiger()
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
  wolfData
)
print('------Merge COMPLETE------')
print('Exporting to Excel...')
exportExcel(allContacts) 
print('------Export COMPLETE------')

# Timing Program
print(f'The Program took {time.time() - start_time} seconds to execute')
