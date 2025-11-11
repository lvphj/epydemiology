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
import inspect
import sys

from .phjTestFunctionParameters import phjAssert



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



def phjAddColumnOfMinRepeatingString(phjDF,
                                     phjColName,
                                     phjNewColName,
                                     phjPrefixStr = None,
                                     phjSuffixStr = None,
                                     phjReattachAffixes = False,
                                     phjReduceMultiSpc = True,
                                     phjStripWhiteSpc = True,
                                     phjPrintResults = False):
    """
    Extracts minimum repeating string from string variable
    
    This function identifies the minimum string that is repeated in a given string. In the
    event that the string does not consist of a repeating unit, the whole string is returned.
    
    
    This function is based on an answer given by David Zhang at:
    https://stackoverflow.com/questions/29481088/how-can-i-tell-if-a-string-repeats-itself-in-python/29482936
    The function does not use regular expressions and appears to be much quicker than other methods.
    
    Parameters
    ----------
    phjDF : pd.DataFrame
            A Pandas dataframe

    phjColName : str
                 The name of the column containing strings that may consist of replicating
                 strings

    phjNewColName : str
                    The name of the column that will be added to the dataframe to contain
                    the minimal replicating strings

    phjPrefixStr : str (default = None)
                   Prefix string to remove from the start of the string before trying to
                   find the replicating string.
    
    phjSuffixStr : str (default = None)
                   Suffix string to remove from the end of the string before trying to
                   find the replicating string.

    phjReattachAffixes: Boolean (default = False)
                        Indicates whether prefixes and suffixes should be reattached to string.
    
    phjReduceMultiSpc = Boolean (default = True)
                        Indicates whether duplicated spaces in string should be converted to a
                        single space.
    
    phjStripWhiteSpc : Boolean (default = True)
                       The repeating string may contain a trailing space; strip the white
                       space from the repeating string.
    
    phjPrintResults : Boolean (default = False)
                      Print intermediate results.
    
    Returns
    -------
    phjDF : Dataframe with additional column (phjNewColName) containing minimal repeating
            string.

    Raises
    ------
    AssertionError if any passed parameter is not correct.

    See Also
    --------
    None

    Examples
    --------
    df = pd.DataFrame({'OriginalStr':['Value:abcdabcd','defdefxyz','hij hij ']})
    
    df = epy.phjAddColumnOfMinRepeatingString(phjDF = df,
                                              phjColName = 'OriginalStr',
                                              phjNewColName = 'RepeatingStr',
                                              phjPrefixStr = 'Value:',
                                              phjSuffixStr = 'xyz',
                                              phjReattachAffixes = False,
                                              phjReduceMultiSpc = True,
                                              phjStripWhiteSpc = True,
                                              phjPrintResults = True)
    
    Returned dataframe
    ==================
          OriginalStr RepeatingStr
    0  Value:abcdabcd         abcd
    1       defdefxyz          def
    2        hij hij           hij
    
    """
    
    
    try:
        phjAssert('phjDF',phjDF,pd.DataFrame)
        phjAssert('phjColName',phjColName,str,phjMustBePresentColumnList = list(phjDF.columns))
        phjAssert('phjNewColName',phjNewColName,str,phjMustBeAbsentColumnList = list(phjDF.columns))
        phjAssert('phjReattachAffixes',phjReattachAffixes,bool)
        phjAssert('phjReduceMultiSpc',phjReduceMultiSpc,bool)
        phjAssert('phjStripWhiteSpc',phjStripWhiteSpc,bool)
        phjAssert('phjPrintResults',phjPrintResults,bool)
    
    except AssertionError as e:
        
        # If function has been called directly, present message.
        if inspect.stack()[1][3] == '<module>':
            print("An AssertionError occurred in {fname}() function. ({msg})\n".format(msg = e,
                                                                                       fname = inspect.stack()[0][3]))
        
        # If function has been called by another function then modify message and re-raise exception
        else:
            print("An AssertionError occurred in {fname}() function when called by {callfname}() function. ({msg})\n".format(msg = e,
                                                                                                                             fname = inspect.stack()[0][3],
                                                                                                                             callfname = inspect.stack()[1][3]))
            raise
    
    else:
        # If a prefix or suffix is entered as '' then this should be considered as None
        if phjPrefixStr == '':
            phjPrefixStr = None
            
        if phjSuffixStr == '':
            phjSuffixStr = None

        # Add new column containing repeating string
        phjDF[phjNewColName] = phjDF[phjColName].apply(lambda s: phjExtractRepeatingString(phjStr = s,
                                                                                           phjPrefixStr = phjPrefixStr,
                                                                                           phjSuffixStr = phjSuffixStr,
                                                                                           phjReattachAffixes = phjReattachAffixes,
                                                                                           phjReduceMultiSpc = phjReduceMultiSpc,
                                                                                           phjStripWhiteSpc = phjStripWhiteSpc,
                                                                                           phjPrintResults = phjPrintResults))
        
        # Ensure leading and trailing spaces have been removed from strings which do not contain duplication
        if phjStripWhiteSpc == True:
            phjDF[phjNewColName] = phjDF[phjNewColName].str.strip()
    
    finally:
        if phjPrintResults == True:
            print('Returned dataframe')
            print('==================')
            with pd.option_context('display.max_rows',10, 'display.max_columns',10):
                print(phjDF)
            print('\n')
        
        return phjDF



def phjExtractRepeatingString(phjStr,
                              phjPrefixStr = None,
                              phjSuffixStr = None,
                              phjReattachAffixes = True,
                              phjReduceMultiSpc = True,
                              phjStripWhiteSpc = True,
                              phjPrintResults = False):
    """
    Extract minimum repeating string from string
    
    This function identifies the minimum string that is repeated in a given string. In the
    event that the string does not consist of a repeating unit, the whole string is returned.
    The prefix and suffix, if present, can be reattached to the extracted string before it
    is returned.
    """
    if (phjPrefixStr is not None) | (phjSuffixStr is not None):
        phjStr,phjPrefixPresent,phjSuffixPresent = phjRemoveAffixes(phjStr,
                                                                    phjPrefixStr = phjPrefixStr,
                                                                    phjSuffixStr = phjSuffixStr,
                                                                    phjPrintResults = False)
    
    # Identify minimum repeating string
    # The following finds the repeating string and, if it exists, assigns the string to
    # the phjStr variable.
    # In Python 3.8, the use of the Walrus operator (:=) would make things clearer. This
    # operator evaluates the result before set value of a variable. However, the := operator
    # is raised as a SyntaxError in earlier versions.
    
    if phjReduceMultiSpc == True:
        phjTemp = principal_period(re.sub(r"\s+"," ",phjStr))
    else:
        phjTemp = principal_period(phjStr)
                                   
    if phjTemp != None:
        phjStr = phjTemp
        
    # If a duplicated string has been identified then return string with affixes reattached;
    # if a prefix and/or affix exists but no duplicated string is identified then attach
    # affixes to original string
    if phjReattachAffixes == True:
        if (phjPrefixStr != None) & (phjPrefixPresent == True):
            phjStr = phjPrefixStr + phjStr
        if (phjSuffixStr != None) & (phjSuffixPresent == True):
            phjStr = phjStr + phjSuffixStr
        
    # Strip white space from start and end of extracted repeating string
    if phjStripWhiteSpc == True:
        phjStr = phjStr.strip()
        
    return phjStr
    
    
def phjRemoveAffixes(phjStr,
                     phjPrefixStr = None,
                     phjSuffixStr = None,
                     phjPrintResults = False):
    """
    Removes prefix and/or suffix from a string. The function returns the cleaned
    string and also two binary variables, phjPrefixPresent and phjSuffixPresent,
    indicating whether the prefix and/or suffix were present, respectively.
    The binary variables allow the affix to be reattached to the extracted string
    if required.
    """
    
    # Set phjPrefixPresent and phjSuffixPresent to False by default
    phjPrefixPresent = False
    phjSuffixPresent = False
    
    # First try to remove prefixes
    if phjPrefixStr is not None:
        try:
            # Check whether the string starts with the prefix
            if phjStr.startswith(phjPrefixStr):
                
                # If so, set phjPrefixPresent variable to True
                phjPrefixPresent = True
                
                # Remove prefix (depending on installed version)
                if sys.version_info >= (3,9):
                    phjStr = phjStr.removeprefix(phjPrefixStr)
                else:
                    phjStr = phjStr[len(phjPrefixStr):]
                    
            # If string does not start with prefix then set phjPrefixPresent variable to False
            else:
                phjPrefixPresent = False
                
        except (AttributeError, TypeError):
            print('Input variable, phjPrefixStr (\'{}\'), must be a string; prefix has not been removed.'.format(phjPrefixStr))

    # Next, try to remove suffixes
    if phjSuffixStr is not None:
        try:
            # Check whether the string ends with the suffix
            if phjStr.endswith(phjSuffixStr):
                
                # If so, set the phjSuffixPresent variable to True
                phjSuffixPresent = True
                
                # Remove suffix (depending on installed version)
                if sys.version_info >= (3,9):
                    phjStr = phjStr.removesuffix(phjSuffixStr)
                else:
                    phjStr = phjStr[:-len(phjSuffixStr)]
                    
            # If string does not end with suffix then set the phjSuffixPresent variable to False
            else:
                phjSuffixPresent = False
            
        except (AttributeError, TypeError):
            print('Input variable, phjSuffixStr, must be a string; suffix has not been removed.')
            
    return (phjStr,phjPrefixPresent,phjSuffixPresent)
    
    
# Answer given by David Zhang at:
# https://stackoverflow.com/questions/29481088/how-can-i-tell-if-a-string-repeats-itself-in-python/29482936
# Short link to answer: https://stackoverflow.com/a/29489919/1718097
def principal_period(s):
    i = (s+s).find(s, 1, -1)
    return None if i == -1 else s[:i]


if __name__ == '__main__':
    main()

