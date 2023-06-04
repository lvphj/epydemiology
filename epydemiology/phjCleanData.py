import pkg_resources

try:
    pkg_resources.get_distribution('numpy')
except pkg_resources.DistributionNotFound:
    numpyPresent = False
    print("Error: Numpy package not available.")
else:
    numpyPresent = True
    import numpy as np


try:
    pkg_resources.get_distribution('pandas')
except pkg_resources.DistributionNotFound:
    pandasPresent = False
    print("Error: Pandas package not available.")
else:
    pandasPresent = True
    import pandas as pd


import datetime
import re



def phjParseDateVar(phjDF,
                    phjDateVarName = None,   # This can be a string or a list of variable names
                    phjDateFormat = '%Y-%m-%d',
                    phjMissingValue = 'missing',
                    phjPrintResults = False):
    
    # Copy the entered dataframe to a working version so can
    # revert back to original if necessary.
    phjWorkingDF = phjDF.copy()
    
    # Convert the column headings to a list for future use
    phjColumnHeadingsList = phjWorkingDF.columns.values
    
    # If the phjDateVarName argument is not None then continue to run the function
    if phjDateVarName is not None:
        
        # Check if the phjDateVarName argument is a string (as opposed to a list or tuple).
        # If so, it is assumed to represent the heading of one of the columns in the dataframe.
        if isinstance(phjDateVarName,str):
            
            # Check that the variable exists as one of the columns 
            if phjDateVarName in phjColumnHeadingsList:
                
                # Convert missing values to np.nan which is not recognised as not
                # matching the datetime format and will be converted to NaT by
                # the to_datetime() method.
                phjWorkingDF[phjDateVarName] = phjWorkingDF[phjDateVarName].replace(phjMissingValue,np.nan)
                
                # Try to convert dates to datetime format based on given format string.
                # If any strings cannot be converted then raise a ValueError.
                try:
                    phjWorkingDF[phjDateVarName] = pd.to_datetime(phjWorkingDF[phjDateVarName],
                                                                  format = phjDateFormat,
                                                                  errors = 'raise')
                
                # If ValueError is raised, give user the option of leaving the dataframe
                # unchanged and checking manually, or try to re-parse and convert any
                # errors to NaT.
                except ValueError:
                    print("Some date strings in variable '{0}' do not match the entered format.\n"
                          "Do you want to leave the function so you can check the date formats in the original data or do you want the function to parse the data again but convert date errors to NaT?".format(phjDateVarName))
                    
                    # In the event that there is a ValueError, ask user to indicate
                    # whether to leave or re-parse the variable. Repeat asking question
                    # until a valid input is given (i.e. 'L' or 'P').
                    phjValidInput = False
                    
                    while phjValidInput == False:
                        phjChoice = input("Enter 'L' to leave or 'P' to parse dates again: ")
                        
                        if phjChoice == 'L' or phjChoice == 'l' or phjChoice == 'P' or phjChoice == 'p':
                            phjValidInput = True
                            
                            # If user requests to leave, reset the working DF back to the original
                            if phjChoice == 'L' or phjChoice == 'l':
                                # User elects to leave function; revert dataframe back to original
                                phjWorkingDF = phjDF
                                print('\nYou have elected to leave the function to evaluate your data. Your original dataframe has not been modified.')
                            
                            # If user requests to re-parse the variable then do so but
                            # any errors should be indicated as NaT.
                            elif phjChoice == 'P' or phjChoice == 'p':
                                print('\nYou chose to convert dates to datetime format and convert any missing values to NaT.')
                                phjWorkingDF[phjDateVarName] = pd.to_datetime(phjWorkingDF[phjDateVarName],
                                                                              format = phjDateFormat,
                                                                              errors = 'coerce')
                        
                        # User entered an invalid code (i.e. not 'L' or 'P') and so
                        # repeat until they get it right.
                        else:
                            print('\nInvalid input. Please try again.')
                            phjValidInput = False
            
            else:
                print("Variable '{0}' does not exist in dataframe.".format(phjDateVarName))
        
        # If the phjDateVarName argument is a list (or tuple) then treat each item
        # as a separate column heading.
        elif isinstance(phjDateVarName,(list,tuple)):
            
            # Check whether all items in the list are actually columns in the dataframe.
            # If not, then return unchanged dataframe.
            if set(phjDateVarName).issubset(phjColumnHeadingsList):
                
                # If all items in list are column headings then step through each one
                # and try to convert to to datetime format
                for varname in phjDateVarName:
                    
                    # Convert missing values to np.nan which is not recognised as not
                    # matching the datetime format and will be converted to NaT by
                    # the to_datetime() method.
                    phjWorkingDF[phjDateVarName] = phjWorkingDF[phjDateVarName].replace(phjMissingValue,np.nan)
                    
                    # Try to convert dates to datetime format based on given format string.
                    # If any strings cannot be converted then raise a ValueError.
                    try:
                        phjWorkingDF[varname] = pd.to_datetime(phjWorkingDF[varname],
                                                               format = phjDateFormat,
                                                               errors = 'raise')
                    
                    # If ValueError is raised, give user the option of leaving the dataframe
                    # unchanged and checking manually, or try to re-parse and convert any
                    # errors to NaT.
                    except ValueError:
                        print("Some date strings in variable '{0}' do not match the entered format.\n"
                              "Do you want to leave the function so you can check the date formats in the original data or do you want the function to parse the data again but convert date errors to NaT?".format(phjDateVarName))
                        
                        phjValidInput = False
                        
                        while phjValidInput == False:
                            phjChoice = input("Enter 'L' to leave or 'P' to parse dates again: ")
                            
                            if phjChoice == 'L' or phjChoice == 'l' or phjChoice == 'P' or phjChoice == 'p':
                                phjValidInput = True
                                
                                # If user elects to leave then convert the working directory back
                                # to original (i.e. any previously successfully changed variables
                                # are reverted back to original) and bread from the loop without
                                # trying to format any other columns.
                                if phjChoice == 'L' or phjChoice == 'l':
                                    # User elects to leave function; revert dataframe back to original
                                    phjWorkingDF = phjDF
                                    print('\nYou have elected to leave the function to evaluate your data. Your original dataframe has not been modified.')
                                    break
                                
                                # If user requests to re-parse the variable then do so but
                                # any errors should be indicated as NaT.
                                elif phjChoice == 'P' or phjChoice == 'p':
                                    print('\nYou chose to convert dates to datetime format and convert any missing values to NaT.')
                                    phjWorkingDF[varname] = pd.to_datetime(phjWorkingDF[varname],
                                                                           format = phjDateFormat,
                                                                           errors = 'coerce')
                            
                            # User entered an invalid code (i.e. not 'L' or 'P') and so
                            # repeat until they get it right.
                            else:
                                print('\nInvalid input. Please try again.')
                                phjValidInput = False
            
            # If one or more of the items in the list is not a column heading, print
            # which items are affected.
            else:
                # At least one item in the phjDateVarName list is not a column heading.
                # Report which one (or ones) are missing.
                for varname in phjDateVarName:
                    if varname not in phjColumnHeadingsList:
                        print("The variable '{}' is not in the dataframe.".format(varname))
        
        # The value entered as the variable name for a date column is not recognised
        # (i.e. it is not a string, a list or a tuple).
        else:
            print("Value entered for phjDateVarName ('{0}') is not recognised.".format(phjDateVarName))
    
    # If the date variable name is not defined (e.g. it is left as None)
    else:
        print('Date variable name is not defined.')
    
    return phjWorkingDF



def phjStripWhiteSpc(phjDF,
                     phjPrintResults = False):

    '''
    Strip whitespace from all columns of dtype 'object' (and only from str data within column)

    Using .str.strip() on columns that are not text strings can cause the cell content
    to be converted to NaN. Some columns with object dtype actually contain mixed data
    types (e.g. text strings and datetime). Applying .str.strip() to these columns
    inadvertently deletes data.
    
    This function steps through each column in a Pandas dataframe and for each column
    of type 'object' creates a mask that identifies all cells containing str data. The
    function then strips white space from start and end using .strip() method.

    Parameters
    ----------
    phjDF : Pandas dataframe
            The dataframe from which white space should be stripped

    phjPrintResults : Boolean, default: False
                      Parameter to indicate whether intermediate results (if
                      there are any) should be printed. Useful for debugging.

    Returns
    -------
    phjDF : Pandas dataframe
            Returns the pandas dataframe which has had whitespace stripped.

    Raises
    ------
    None

    See Also
    --------
    None

    Examples
    --------
    # Define a dataframe with a column that contains data consisting of strings and numeric values
    phjTempDF = pd.DataFrame({'column1':[' abc  ',1,' def  ',2,3.14,' ghi  ']})
    print(phjTempDF)

    # View the mixed data types in 'column1' of the dataframe
    # Taken from: https://stackoverflow.com/questions/38964819/warning-multiple-data-types-in-column-of-very-large-dataframe
    print('dtypes of data columns in dataframe')
    print('-----------------------------------')
    print(phjTempDF.dtypes)
    print('\n')

    print('Number of each different data type in single column')
    print('---------------------------------------------------')
    phjTempDF['column1'].apply(type).value_counts()

    # Create a second dataframe and create a column that contains the values
    # from the original dataframe but with trailing white space stripped using
    # standard .str.strip() method. Notice that the values which were not strings
    # have been converted to NaN values.
    phjTemp2DF = pd.DataFrame()
    phjTemp2DF['column1'] = phjTempDF['column1'].str.strip()
    
    print('Effect of using standard .str.strip() method on object column')
    print('-------------------------------------------------------------')
    print(phjTemp2DF)

    # Strip white space from string values only
    phjTempDF = epy.phjStripWhiteSpc(phjTempDF,
                                     phjPrintResults = False)

    print('Effect of stripping white space from object column using phjStripWhiteSpc()')
    print('---------------------------------------------------------------------------')
    print(phjTempDF)
    print('\n')

    print('...but the data types within the column remain the same')
    phjTempDF['column1'].apply(type).value_counts()
    '''

    
    # Add checks to ensure passed parameters are correct
    
    # Step through list of column names
    for c in phjDF.columns.to_list():
        
        # Only select columns of type object
        if phjDF[c].dtype == 'object':
            # Create a mask to identify cells that contain strings
            phjStrMask = phjDF[c].apply(type) == str
            # Strip whitespace from string cells only
            phjDF.loc[phjStrMask,c] = phjDF.loc[phjStrMask,c].str.strip()
        
    return phjDF



def phjUKDateStrToDatetime(x,
                           phjCentury = 2000,
                           phjPrintResults = False):

    '''
    Converts a UK (day first) date string to a consistent date format

    This function converts a UK (day first) date string (e.g. 24-03-2022) to a consistent format
    so that pd.to_datetime() method can be used to convert the string to datetime. The need for
    the function arose when importing data from an Excel spreadsheet where the formats for date
    strings were inconsistent (e.g. 24-03-2022, 24/03/2022, 24/03/22, etc.). In such cases, strings
    of a different format were returned as NaT values, resulting in lost data.

    Parameters
    ----------
    x : str
        A date string

    phjCentury : int
                 The default century to use when only 2-digit century is included, default: 2000

    phjPrintResults : Boolean
                      Parameter to indicate whether intermediate results (if
                      there are any) should be printed. Useful for debugging.
                        
    Returns
    -------
    phjOut : Either a datetime or np.nan

    Raises
    ------
    None

    See Also
    --------
    None

    Examples
    --------    
    # Define a dataframe with UK date strings with multiple separators and 2- or 4-digit years
    phjTempDF = pd.DataFrame({'datecol':[np.nan,
                                         '20/03/04',
                                         '21/04/2004',
                                         '19-03-2010 00:00:00',
                                         '01-02_2002',
                                         '30-02-2003',
                                         '02/03\\2006',
                                         '03.04,2005',
                                         '5 6:2005',
                                         'abc',
                                         np.nan]})

    print("Example dateframe")
    print('-----------------')
    print(phjTempDF)
    print('\n')
    print("Date column dtype")
    print("-----------------")
    print(phjTempDF.dtypes)
    print('\n')

    # Convert date string to datetime using phjUKDateStrToDatetime() function
    phjTempDF['datecol'] = phjTempDF['datecol'].apply(lambda x: epy.phjUKDateStrToDatetime(x,phjCentury = 2000,phjPrintResults = True))
    print('\n')

    # Print new column and dtype
    print("Example dateframe")
    print("-----------------")
    print(phjTempDF)
    print('\n')
    print("Date column dtype")
    print("-----------------")
    print(phjTempDF.dtypes)
    '''
    
    # If the cell string is not NaN then attempt to process as a date string:
    if not pd.isna(x):
        # Process if x is a string
        # N.B. isinstance() is recommended for testing the type of an object because it takes subclasses
        # into account (see answer by Gabriel Staples at https://stackoverflow.com/questions/4843173/how-to-check-if-type-of-a-variable-is-string)
        if isinstance(x,str):
            # If date string includes a time component then delete
            x = re.sub("\s\d\d:\d\d:\d\d$",'',x)

            # Defining the regex to match punctuation marks is challenging due to the need
            # to escape special characters. The following works but "[/\-:., _]" does not.
            #phjDatePartsList = re.split("[/\-:., _]",x)   # does not work
            phjDatePartsList = re.split("/|\\\\|\-|:|\.|,| |_",x)   # The escape character needs to be escaped twice or use r"/|\\|\-|:|\.|,| |_"

            if phjPrintResults == True:
                print("Original string: {}; list of date parts: {}".format(x,phjDatePartsList))

            # Splitting the date string should result in a list with 3 items; if so, attempt to process as a date:
            if len(phjDatePartsList) == 3:
                # The final item in the list should be the year; if the year has 2 digits then convert to 4 digits:
                if len(phjDatePartsList[-1]) == 2:
                    phjDatePartsList[-1] = str(phjCentury + int(phjDatePartsList[-1]))

                phjDateStr = '-'.join([phjDatePartsList[2],phjDatePartsList[1].zfill(2),phjDatePartsList[0].zfill(2)])

                if phjPrintResults == True:
                    print("    Harmonised date string:{}".format(phjDateStr))

                phjOut = pd.to_datetime(phjDateStr,
                                        dayfirst = True,
                                        errors = 'coerce')

            else:
                phjOut = np.nan
                
        # Process if x is a datetime
        elif isinstance(x,datetime.datetime):
            phjOut = x
            
        else:
            phjOut = np.nan
        
    else:
        phjOut = np.nan
        
    return phjOut


if __name__ == '__main__':
    main()

