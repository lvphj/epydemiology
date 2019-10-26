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
    import _mssql


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
        phjTempDBType  = input('Please enter type of database (MySQL or SQL Server): ')
        phjTempDBType = re.sub(r'\s+','', phjTempDBType.lower())
        
        if phjTempDBType == 'mysql':
            # Retrieve data from MySQL database
            phjDF = phjLoadQueryIntoDataframe(phjDBType = 'mysql',
                                                  phjQuery = phjTempQuery,
                                                  phjMaxAttempts = phjAllowedAttempts,
                                                  phjPrintResults = phjPrintResults)
        
        elif (phjTempDBType == 'mssql') or (phjTempDBType == 'sqlserver'):
            # Retrieve data from SQL SERVER database
            phjDF = phjLoadQueryIntoDataframe(phjDBType = 'mssql',
                                                  phjQuery = phjTempQuery,
                                                  phjMaxAttempts = phjAllowedAttempts,
                                                  phjPrintResults = phjPrintResults)
        
        else:
            print('Database type was not recognised.')
            phjDF = None
    
    else:
        phjDF = None
    
    if phjPrintResults:
        if phjDF is not None:
            print('\nQuery completed')
            print('Number of rows returned = ',len(phjDF.index))
            print('\n')
            print(phjDF.head(5))
            print(phjDF.tail(5))
        else:
            print('\nReturned dataframe is empty.')
            print('\n')
    
    return phjDF



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
    
    # Check whether input string matches a SELECT...FROM... query.
    # The following regex also allows SELECT...FROM... query to occur inside a bracket
    # at the start of the string.
    phjSelectQueryRegex = re.compile('^\(?\s*SELECT[\s\S]+\sFROM\s',flags=re.I|re.X)
    
    if phjTempQuery is not None:
        if not(re.match(phjSelectQueryRegex, phjTempQuery)):
            print("Only 'SELECT' queries can be used to interrogate the database.")
            phjTempQuery = None
    
    return phjTempQuery



def phjLoadQueryIntoDataframe(phjDBType,
                              phjQuery,
                              phjMaxAttempts = 3,
                              phjPrintResults = False):
    
    phjTempConnection = phjConnectToDatabase(phjDBType,
                                             phjMaxAttempts = phjMaxAttempts,
                                             phjPrintResults = False)
    
    if phjTempConnection is not None:
    
        if phjPandasPresent:
            try:
                # phjDF = pd.io.sql.read_sql(phjQuery, con=phjTempConnection)
                phjDF = pd.read_sql_query(phjQuery, con=phjTempConnection)
            
            except pd.io.sql.DatabaseError as e:
                print('\nA DatabaseError occurred.')
                print(e)
                print('\nPlease edit the file containing the SQL query and re-run the function.\n')
                phjDF = None
            
            finally:
                phjTempConnection.close()
            
        else:
            print('\nRequired package Pandas is not available.\n')
    
    else:
        phjDF = None
    
    return phjDF



def phjConnectToDatabase(phjDBType,
                         phjMaxAttempts = 3,
                         phjPrintResults = False):
    
    for i in range(phjMaxAttempts):
    
        # Get login details
        phjTempServer = input("Enter host: ")
        phjTempUser = input("Enter user: ")
        phjTempPwd = getpass.getpass("Enter password: ")
        phjTempDBName = input("Enter database name (optional but may need to modify SQL query): ")
        
        if not phjTempDBName or phjTempDBName.isspace():
            phjTempDBName = None
        
        # Connect to MySQL database and load data into dataframe
        if phjDBType == 'mysql':
            
            # Check that PyMySQL has been installed before trying to use it.
            # If so, read data into datagram; if not,
            # set return value to None.
            if phjPymysqlPresent:
            
                try:
                    if phjTempDBName is None:
                        phjTempConnection = pymysql.connect(host = phjTempServer,
                                                            user = phjTempUser,
                                                            password = phjTempPwd,
                                                            cursorclass = pymysql.cursors.Cursor)
                    
                    else:
                        phjTempConnection = pymysql.connect(host = phjTempServer,
                                                            user = phjTempUser,
                                                            password = phjTempPwd,
                                                            db = phjTempDBName,
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
        elif phjDBType == 'mssql':
            
            # Check that PyMSSQL has been installed before trying to use it.
            # If so, read data into datagram; if not,
            # set return value to None.
            if phjPymssqlPresent:
            
                try:
                    # N.B. Need to use pymssql.connect() because the connection object
                    #      has a 'cursor' attribute which Pandas uses to read into
                    #      dataframe; in contrast, using _mssql.connect(), the resulting
                    #      _mssql.MSSQLConnection object does not have cursor attribute.
                    if phjTempDBName is None:
                        # If name of database is not entered then may need to modify
                        # SQL query, for example, to run query to get info from table1
                        # on database called ABC, could use:
                        #    SELECT * FROM ABC.dbo.table1
                        phjTempConnection = pymssql.connect(server = phjTempServer,
                                                            user = phjTempUser,
                                                            password = phjTempPwd,
                                                            port = '1433')
                    
                    else:
                        phjTempConnection = pymssql.connect(server = phjTempServer,
                                                            user = phjTempUser,
                                                            password = phjTempPwd,
                                                            database = phjTempDBName,
                                                            port = '1433')
                    
                    break
                
                except pymssql.InterfaceError:
                    print("\nA MSSQLDriverException has been caught.")
                    
                    if i < (phjMaxAttempts-1):
                        print('\nPlease re-enter login details.\n')    # Only say 'Please try again' if not last attempt.
                    
                    else:
                        # If connection to database can't be made:
                        print('\nFailed to connect to database after {0} attempts.\n'.format(i+1))
                        phjTempConnection = None
                
                except pymssql.DatabaseError as e:
                    # The e variable can be used to express number, severity, state and
                    # message
                    print("\nA MSSQLDatabaseException has been caught. ({0})".format(e))
                    
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
            print('\nDatabase type {} is not recognised.\n'.format(phjDBType))
            phjTempConnection = None
            
    return phjTempConnection



if __name__ == '__main__':
    main()
