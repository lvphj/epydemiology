"""
There appears to be a problem with the pypyodbc library that causes column names
to be returned as the first letter only as a byte rather than a char.
This question was asked on StackExchange (Dec 2015) and is seems that the
problem had already been reported to pypyodbc in 2014. No update has since been
released to fix the problem.

Therefore, will connect using pymssql or pymysql instead...

N.B. There is an obscure bug on Unix machines (see: http://www.pymssql.org/en/latest/freetds_and_dates.html)
where returned dates can be shifted back by one month. I checked the results returned below with the
dates in the database and this problem does not seem to be an issue.
"""

# IMPORT REQUIRED PACKAGES
# ========================
# The following method to check that a package is available is not considered to be
# good practice:
#
#   try:
#       import package_name
#       HAVE_PACKAGE = True
#   except ImportError:
#       HAVE_PACKAGE = False
#
# Instead use the following method (as described at: https://docs.plone.org/develop/styleguide/python.html#about-imports)...

import pkg_resources

try:
    pkg_resources.get_distribution('pandas')
except pkg_resources.DistributionNotFound:
    phjPandasPresent = False
    print("Error: Pandas package not available.")
else:
    phjPandasPresent = True
    import pandas as pd


try:
    pkg_resources.get_distribution('pymysql')
except pkg_resources.DistributionNotFound:
    phjPymysqlPresent = False
    print("Error: PyMySQL package not available. Some features may not be available.")
else:
    phjPymysqlPresent = True
    import pymysql


try:
    pkg_resources.get_distribution('pymssql')
except pkg_resources.DistributionNotFound:
    phjPymssqlPresent = False
    print("Error: PyMSSQL package not available. Some features may not be available.")
else:
    phjPymssqlPresent = True
    import pymssql


from .phjMiscFuncs import phjGetStrFromArgOrFile


import re
import getpass



def phjGetDataFromDatabase(phjQueryStr = None,
                           phjQueryPathAndFileName = None,
                           phjPrintResults = False):
    
    phjAllowedAttempts = 3
    
    phjTempQuery = phjGetSELECTQueryStr(phjQueryStr = phjQueryStr,
                                        phjQueryPathAndFileName = phjQueryPathAndFileName,
                                        phjAllowedAttempts = phjAllowedAttempts,
                                        phjPrintResults = phjPrintResults)
    
    
    if phjTempQuery is not None:
        # Enter name of database (convert to lower case and remove white space)
        phjTempDBName  = input('Please enter type of database (MySQL or SQL Server): ')
        phjTempDBName = re.sub(r'\s+','', phjTempDBName.lower())
        
        if phjTempDBName == 'mysql':
            # Retrieve data from MySQL database
            phjTempDF = phjLoadQueryIntoDataframe(phjDBName = 'mysql',
                                                  phjQuery = phjTempQuery,
                                                  phjMaxAttempts = phjAllowedAttempts,
                                                  phjPrintResults = phjPrintResults)
        
        elif (phjTempDBName == 'mssql') or (phjTempDBName == 'sqlserver'):
            # Retrieve data from SQL SERVER database
            phjTempDF = phjLoadQueryIntoDataframe(phjDBName = 'mssql',
                                                  phjQuery = phjTempQuery,
                                                  phjMaxAttempts = phjAllowedAttempts,
                                                  phjPrintResults = phjPrintResults)
        
        else:
            print('Database type was not recognised.')
            phjTempDF = None
    
    else:
        phjTempDF = None
    
    if phjPrintResults:
        if phjTempDF is not None:
            print('\nQuery completed')
            print('Number of rows returned = ',len(phjTempDF.index))
            print('\n')
            print(phjTempDF.head(5))
            print(phjTempDF.tail(5))
        else:
            print('\nReturned dataframe is empty.')
            print('\n')
    
    return phjTempDF



def phjGetSELECTQueryStr(phjQueryStr = None,
                         phjQueryPathAndFileName = None,
                         phjAllowedAttempts = 3,
                         phjPrintResults = False):
    
    phjTempQuery = phjGetStrFromArgOrFile(phjStr = phjQueryStr,
                                          phjPathAndFileName = phjQueryPathAndFileName,
                                          phjAllowedAttempts = phjAllowedAttempts,
                                          phjPrintResults = phjPrintResults)
    
    if phjPrintResults == True:
        print("Query entered: ",phjTempQuery)
    
    # Check whether input string matches a SELECT...FROM... query
    phjSelectQueryRegex = re.compile('^SELECT[\s\S]+\sFROM\s',flags=re.I|re.X)
    
    if phjTempQuery is not None:
        if not(re.match(phjSelectQueryRegex, phjTempQuery)):
            print("Only 'SELECT' queries can be used to interrogate the database.")
            phjTempQuery = None
    
    return phjTempQuery



def phjLoadQueryIntoDataframe(phjDBName,
                              phjQuery,
                              phjMaxAttempts = 3,
                              phjPrintResults = False):
    
    phjTempConnection = phjConnectToDatabase(phjDBName,
                                             phjMaxAttempts = phjMaxAttempts,
                                             phjPrintResults = False)
    
    if phjTempConnection is not None:
    
        if phjPandasPresent:
            try:
                phjTempDF = pd.io.sql.read_sql(phjQuery, con=phjTempConnection)
            
            except pd.io.sql.DatabaseError as e:
                print('\nA DatabaseError occurred.')
                print(e)
                print('Please edit the file containing the SQL query and re-run the function.\n')
                phjTempDF = None
            
            finally:
                phjTempConnection.close()
            
        else:
            print('\nRequired package Pandas is not available.\n')
    
    else:
        phjTempDF = None
    
    return phjTempDF



def phjConnectToDatabase(phjDBName,
                         phjMaxAttempts = 3,
                         phjPrintResults = False):
    
    for i in range(phjMaxAttempts):
    
        # Get login details
        phjTempServer = input("Enter host: ")
        phjTempUser = input("Enter user: ")
        phjTempPwd = getpass.getpass("Enter password: ")
        
        # Connect to MySQL database and load data into dataframe
        if phjDBName == 'mysql':
            
            # Check that PyMySQL has been installed before trying to use it.
            # If so, read data into datagram; if not,
            # set return value to None.
            if phjPymysqlPresent:
            
                try:
                    phjTempConnection = pymysql.connect(host = phjTempServer,
                                                        user = phjTempUser,
                                                        password = phjTempPwd,
                                                        cursorclass = pymysql.cursors.Cursor)
                    
                    break
                    
                except pymysql.err.OperationalError as e:
                    
                    print("\nAn OperationalError occurred and connection to database was unsuccessful.\nError number {0}: {1}.".format(e.args[0],e.args[1]))
                    
                    if i < (phjMaxAttempts-1):
                        print('\nPlease re-enter login details.\n')    # Only say 'Please try again' if not last attempt.
                        
                    else:
                        # If connection to database can't be made:
                        print('\nFailed to connect to database after {0} attempts.\n'.format(i+1))
                        phjTempConnection = None
                        
            else:
                print('\nRequired package PyMySQL is not available.\n')
                phjTempConnection = None
                break
                
        # Connect to SQL SERVER (or MS SQL) database and load data into dataframe
        elif phjDBName == 'mssql':
            
            # Check that PyMSSQL has been installed before trying to use it.
            # If so, read data into datagram; if not,
            # set return value to None.
            if phjPymssqlPresent:
            
                try:
                    phjTempConnection = pymssql.connect(server = phjTempServer,
                                                        user = phjTempUser,
                                                        password = phjTempPwd,
                                                        port = '1433')
                    
                    break
                    
                except pymssql.OperationalError as e:
                    # For full list of errors that may be raised by pymssql, see https://media.readthedocs.org/pdf/pymssql/latest/pymssql.pdf)
                    print("\nAn OperationalError occurred and connection to database was unsuccessful.\nError number {0}: {1}.".format(e.args[0],e.args[1]))
                    
                    if i < (phjMaxAttempts-1):
                        print('\nPlease re-enter login details.\n')    # Only say 'Please try again' if not last attempt.
                        
                    else:
                        # If connection to database can't be made:
                        print('\nFailed to connect to database after {0} attempts.\n'.format(i+1))
                        phjTempConnection = None
                        
            else:
                print('\nRequired package PyMsSQL is not available.\n')
                phjTempConnection = None
                break
                
        else:
            if phjPrintResults:
                print('\nDatabase type is not recognised. Connection to database cannot be made.\n')
                
            phjTempConnection = None
            
    return phjTempConnection



if __name__ == '__main__':
    main()
