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

from collections import Counter
from collections import OrderedDict


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



def phjAddColHeadingPrefix(phjColHeadingList,
                           phjExceptColHeadingList,
                           phjPrefixStr,
                           phjSeparator = '_',
                           phjRemoveUnalteredEntries = True,
                           phjPrintResults = False):
    """
    Creates a dictionary with keys equal to the original column heading
    and values equal to the column heading with prefix added if required
    (i.e. items in the exception list are not affected).
    
    Creating a dictionary to rename columns avoids any potential issues with
    columns in dataframe being reordered. It also allows for the same renaming
    dictionary to be used repeatedly on dataframes with the same column names
    but in a different order.
    
    Adding a prefix to column headings enables pd.wide_to_long() function to
    rearrange Pandas dataframe into long format.
    
    Parameters
    ----------
    
    phjColHeadingList = List of columns headings in dataframe
    
    phjExceptColHeadingList
    
    phjPrefixStr
    
    phjSeparator
    
    phjRemoveUnalteredEntries (default = True) = Cases where the key and value are identical are not included in the dictionary
    
    phjPrintResults
    
    Examples
    --------
    
    The following dataframe (myDF) consists of two categorical variables defining
    each row, namely cat1 and cat2. The remaining columns (stuff, things and value)
    represent variables that might need to be renamed to allow pd.wide_to_long()
    function to be used.
    
       cat1 cat2  stuff  things  value
    0     1    a   2230     489    143
    1     2    b   1134     267     87
    2     3    c   1165     256     25
    3     4    d   1176     232     47
    4     5    e   2279     478     86
    5     6    f   1165     276     67
    6     7    g   1176     287     87
    7     8    h   3456     850    207
    8     9    i   1156     245     34
    9    10    j   1176     223     62
    
    The phjAddColHeadingPrefix() function returns a dictionary that can be used
    to rename the column headings with a prefix (and separator character) as
    follows:
    
    myDict = phjAddColHeadingPrefix(phjColHeadingList = list(myDF.columns),
                                    phjExceptColHeadingList = ['cat1','cat2'],
                                    phjPrefixStr = 'category',
                                    phjSeparator = '_',
                                    phjRemoveUnalteredEntries = True,
                                    phjPrintResults = True)
    
    The following dictionary would be returned:
    {'stuff': 'category_stuff','things': 'category_things','value': 'category_value'}
    
    """
    
    # Checks to perform
    # =================
    # Check phjSeparator is allowed character (e.g. '_', '-')
    # Ensure none of the column headings already start with prefix and separator
    
    
    #phjColHeadingList = [phjPrefixStr + phjSeparator + c if c not in phjExceptionList else c for c in phjColHeadingList]
    
    # Create dictionary to rename column headings
    phjRenameColHeadingDict = {k:c for (k,c) in zip(phjColHeadingList,
                                                       ([phjPrefixStr + phjSeparator + c if c not in phjExceptColHeadingList else c for c in phjColHeadingList]))}    
    
    # Retain only k:v pairs where k and v are different
    if phjRemoveUnalteredEntries == True:
        phjRenameColHeadingDict = {k:c for k,c in phjRenameColHeadingDict.items() if k != c}
    
    if phjPrintResults == True:
        print('Dictionary to rename column headings: {}'.format(phjRenameColHeadingDict))
        print('\n')
    
    return phjRenameColHeadingDict


def phjAggDupColsAndRows(phjDF,
                         phjReqVarList,
                         phjReqVarAllPresent = True,
                         phjAutoAgg = True,
                         phjColAgg = 'sum', # Currently the only option
                         phjRowAgg = 'sum', # Currently the only option
                         phjPrintResults = False):
    
    """
    Function identifies duplicate column headings and duplicate rows (based
    on subset of variables) and aggregates cells to produce a dataframe that
    contains no duplicates.
    
    Importing a dataframe from an Excel file, does not allow duplicate column
    headings, and only the last duplicate column is retained. However, a dataframe
    can be imported with unique column headings but, after some data wrangling,
    duplicate column headings might be created. For example, a dataframe might
    be imported from a spreadsheet with column headings 'other' and 'other*'.
    These column headings would be considered deistinct and would be imported as
    two separate columns into a Pandas dataframe. However, after cleaning, it
    might be the case that the asterisk is removed resulting in two columns named
    'other'. This function will aggregate these duplicated columns (default by
    summing).
    
    Similarly, rows of data may be duplicated on a selection of defining categorical
    variables and the data in remaining columns therefore needs to be aggregated
    across rows to produce a single output.
    
    Parameters
    ----------
    
    phjDF: Pandas dataframe
    
    phjReqVarList: List of column headings (variables) that will be used to
    identify duplicated rows.
    
    phjReqVarAllPresent: (default = True) Boolean variable to indicate that ALL
    the columns listed in phjReqVarList must be present in the dataframe. In
    most cases, the required list of variables should all be present in the
    dataframe. However, in some cases, it might be that the data should only be
    grouped by those listed variables that are present in the dataframe. This
    situation has arisen when processing multiple files and in a small number
    of files, one of the variables had not been included. Therefore, if
    phjReqVarAllPresent is set to False, adjust to only include those required
    variables that are present in the dataframe.
    
    phjAutoAgg: (default = False) Automatically aggregate duplicate columns and
    rows; if True, simply return the original dataframe. Setting to False and
    combining with phjPrintResults set to True allows the duplication to be viewed
    before modifying the dataframe.
    
    phjColAgg: (default = 'sum') Aggregation method to use to aggregate duplicate
    columns. N.B. Currently, 'sum' is the only option.
    
    phjRowAgg: (default = 'sum') Aggregation method to use to aggregate duplicate
    rows. N.B. Currently, 'sum' is the only option.
    
    phjPrintResults: (default = False) Boolean to indicate whether intermediate
    results should be printed.
    
    Returns
    -------
    If no errors have been encountered, the function returns a dataframe where
    duplicated columns and duplicated rows have been aggregated.
    
    Raises
    ------
    None
    
    See also
    --------
    None
    
    Examples
    --------
    
    import numpy as np
    import pandas as pd

    # Define a dataframe that has duplicated column headings and duplicated rows
    dupdf = pd.DataFrame({'cat1':[1,1,2,3,4,5,5,6,7,8,8,8,9,10],
                          'cat2':['a','a','b','c','d','e','e','f','g','h','h','h','i','j'],
                          'stuff':[10,20,34,65,76,45,34,65,76,87,23,46,56,76],
                          'things':[55,34,67,56,32,15,63,76,87,89,67,94,45,23],
                          'morestuff':[100,100,100,100,100,100,100,100,100,100,100,100,100,100],
                          'morethings':[200,200,200,200,200,200,200,200,200,200,200,200,200,200],
                          'yetmorestuff':[1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000,1000],
                          'value':[67,76,87,25,47,52,34,67,87,87,66,54,34,62]
                         })
                            
    print(dupdf)
    
            cat1 cat2  stuff  things  morestuff  morethings  yetmorestuff  value
        0      1    a     10      55        100         200          1000     67
        1      1    a     20      34        100         200          1000     76
        2      2    b     34      67        100         200          1000     87
        3      3    c     65      56        100         200          1000     25
        4      4    d     76      32        100         200          1000     47
        5      5    e     45      15        100         200          1000     52
        6      5    e     34      63        100         200          1000     34
        7      6    f     65      76        100         200          1000     67
        8      7    g     76      87        100         200          1000     87
        9      8    h     87      89        100         200          1000     87
        10     8    h     23      67        100         200          1000     66
        11     8    h     46      94        100         200          1000     54
        12     9    i     56      45        100         200          1000     34
        13    10    j     76      23        100         200          1000     62
    
    # Clean up process that will create columns with duplicated name
    dupdf = dupdf.rename(columns = {'morestuff':'stuff'})
    dupdf = dupdf.rename(columns = {'yetmorestuff':'stuff'})
    dupdf = dupdf.rename(columns = {'morethings':'things'})
    
    print(dupdf)
    
            cat1 cat2  stuff  things  stuff  things  stuff  value
        0      1    a     10      55    100     200   1000     67
        1      1    a     20      34    100     200   1000     76
        2      2    b     34      67    100     200   1000     87
        3      3    c     65      56    100     200   1000     25
        4      4    d     76      32    100     200   1000     47
        5      5    e     45      15    100     200   1000     52
        6      5    e     34      63    100     200   1000     34
        7      6    f     65      76    100     200   1000     67
        8      7    g     76      87    100     200   1000     87
        9      8    h     87      89    100     200   1000     87
        10     8    h     23      67    100     200   1000     66
        11     8    h     46      94    100     200   1000     54
        12     9    i     56      45    100     200   1000     34
        13    10    j     76      23    100     200   1000     62
    

    # To list the duplicated column headings and duplicated rows (as defined
    # by the listed columns in phjReqVarList), run the phjAggDupColsAndRows()
    # function with phjAutoAgg set to False and phjPrintResults set to True.
    aggdf = epy.phjAggDupColsAndRows(phjDF = dupdf,
                                     phjReqVarList = ['cat1','cat2'],
                                     phjReqVarAllPresent = True,
                                     phjAutoAgg = False,
                                     phjColAgg = 'sum', # Currently the only option
                                     phjRowAgg = 'sum', # Currently the only option
                                     phjPrintResults = True)

        Duplicated columns
        ------------------
        Column 'stuff': number of occurrences = 3
        Column 'things': number of occurrences = 2


        Duplicated rows
        ---------------
            cat1 cat2  count
        0      1    a      2
        1      1    a      2
        5      5    e      2
        6      5    e      2
        9      8    h      3
        10     8    h      3
        11     8    h      3


        The phjAutoAgg parameter was set to False and, therefore, the original dataframe has not been altered.


    # To aggregate the duplicated columns and rows, set phjAutoAgg to True
    aggdf = epy.phjAggDupColsAndRows(phjDF = dupdf,
                                     phjReqVarList = ['cat1','cat2'],
                                     phjReqVarAllPresent = True,
                                     phjAutoAgg = True,
                                     phjColAgg = 'sum', # Currently the only option
                                     phjRowAgg = 'sum', # Currently the only option
                                     phjPrintResults = False)
    
    print(aggdf)
    
           cat1 cat2  stuff  things  value
        0     1    a   2230     489    143
        1     2    b   1134     267     87
        2     3    c   1165     256     25
        3     4    d   1176     232     47
        4     5    e   2279     478     86
        5     6    f   1165     276     67
        6     7    g   1176     287     87
        7     8    h   3456     850    207
        8     9    i   1156     245     34
        9    10    j   1176     223     62
    
    """
    
    # Checks to perform
    # 1. Check that variables included in the phjReqVarList are not duplicated
    #    (see note below)
    
    
    # Create a temporary copy of the dataframe which can be modified but, should
    # an error occur, the original dataframe can be returned unaltered
    phjTempDF = phjDF.copy(deep = True)
    
    # In most cases, the required list of variables should all be present in the
    # dataframe. However, in some cases, it might be that the data should only be
    # grouped by those listed variables that are present in the dataframe. This
    # situation has arisen when processing multiple files and in a small number
    # of files, one of the variables had not been included. Therefore, if
    # phjReqVarAllPresent is set to False, adjust to only include those required
    # variables that are present in the dataframe.
    if phjReqVarAllPresent == False:
        phjReqVarList = [c for c in phjReqVarList if c in list(phjTempDF.columns)]
    
    # Identify and aggregate duplicate columns
    # ----------------------------------------
    
    # Create a dictionary listing duplicated column headings only and the number
    # of times each appears in the dataset. If there are no duplicated columns then
    # phjDupColDict will be empty
    # N.B. All columns in the dataframe are considered but, in reality, it is assumed
    # that variables in the phjReqVarList are not duplicated. Perhaps should check for
    # this explicitly as some point in the future.
    phjDupColDict = {k:v for k,v in Counter(list(phjTempDF.columns)).items() if v > 1}
    
    if phjPrintResults == True:
        print('Duplicated columns')
        print('------------------')
        
    # Test if phjDupColDict exists; if not then no column headings are duplicated
    if phjDupColDict:
        
        if phjPrintResults == True:
            for c in phjDupColDict.keys():
                print('Column \'{}\': number of occurrences = {}'.format(c,phjDupColDict[c]))
            print('\n')
        
        # Retain a list of the original column heading order
        # See: https://stackoverflow.com/questions/480214/how-do-i-remove-duplicates-from-a-list-while-preserving-order
        # Since Python 3.6, dict is ordered and could be used; however, OrderedDict will work
        # with earlier versions
        phjOrigColOrderList = list(OrderedDict.fromkeys(list(phjTempDF.columns)))
    
        # Define a suffix with which to temporarily label duplicate columns
        phjAggSuff = '_AGG'
        
        # Aggregate duplicate columns (if phjAutoAgg == True)
        # ---------------------------
        if phjAutoAgg == True:
            for i in phjDupColDict.keys():

                # Aggregate duplicated columns into column of same name but tagged with suffix '_AGG' (actually phjAggSuff)
                if phjRowAgg == 'sum':
                    phjTempDF[i + phjAggSuff] = phjTempDF[i].sum(axis = 1,
                                                                 skipna = True,
                                                                 numeric_only = True)

                    # Drop original duplicated columns
                    phjTempDF = phjTempDF.drop(i,
                                               axis = 1)

                    # Rename suffixed column with original column name
                    phjTempDF = phjTempDF.rename(columns = {i + phjAggSuff:i})

                    if phjPrintResults == True:
                        print('Dataframe with aggregated \'{}\' column ({} occurrences)'.format(i,phjDupColDict[i]))
                        print(phjTempDF)
                        print('\n')   

            # Reset columns to original order
            phjTempDF = phjTempDF[phjOrigColOrderList].copy(deep = True)
        
    else:
        if phjPrintResults == True:
            print('No duplicated column headings')
            print('\n')
    
        
    # Identify and aggregate duplicate rows (across named variables)
    # -------------------------------------
    
    if phjPrintResults == True:
        print('Duplicated rows')
        print('---------------')
    
    # Test if there are any duplicated rows based on required variable list
    # by comparing the number of groupby groups with the length of the dataframe
    # (if there are no duplicates, each groupby group will contain a single row)
    # Firstly, create groupby object...
    phjTempGrpby = phjTempDF.groupby(phjReqVarList)
    
    # ...and then test is number of groups is less than length of dataframe
    if phjTempGrpby.ngroups < len(phjTempDF.index):
        
        if phjPrintResults == True:
            # Create a dataframe consisting on only those rows that are duplicated
            # on required variable list
            phjDupRowDF = phjTempDF.loc[phjTempDF.duplicated(subset = phjReqVarList,
                                                              keep = False),
                                        phjReqVarList]

            # Add a 'count' column indicating how many times the row is duplicated
            # Since the count column will be based on duplication of all columns
            # present in the database, it seems that an addition column is required
            # in order to count. Try adding a dummy column.
            phjDupRowDF['dummy'] = 1

            # Add a count column
            phjDupRowDF['count'] = phjDupRowDF.groupby(phjReqVarList)['dummy'].transform('count')

            # Delete dummy column
            phjDupRowDF = phjDupRowDF.drop('dummy', axis = 1).copy(deep = True)

            # Print all duplicated rows
            print(phjDupRowDF)
            
            print('\n')
        
        # Aggregate duplicate rows
        # ------------------------
        if phjAutoAgg == True:
            # Record number of rows in original dataframe (or, at least, the dataframe after
            # any column aggregations have taken place)
            phjOrigNRows = len(phjTempDF.index)

            # Aggregate rows that are duplicated on required variable list using
            # the aggregation defined in functions parameters (default = sum)
            phjTempDF = phjTempDF.groupby(phjReqVarList).agg(phjRowAgg).reset_index()

            if phjPrintResults == True:
                print('Number of rows BEFORE aggregating duplicate rows = {}'.format(phjOrigNRows))
                print('Number of rows AFTER aggregating duplicate rows = {}'.format(len(phjTempDF.index)))
                print('\n')
    
    else:
        if phjPrintResults == True:
            print('No duplicated rows')
            print('\n')
    
    if phjAutoAgg == False:
        print('The phjAutoAgg parameter was set to False and, therefore, the original dataframe has not been altered.')
    
    else:
        # If the original dataframe has been altered in some way (i.e. aggregated
        # either rows or columns) then print the new, aggregrated dataframe
        if phjPrintResults == True:
            if phjTempDF.equals(phjDF) == False:
                print('Aggregated dataframe')
                print('--------------------')
                print(phjTempDF)
                print('\n')
        
    return phjTempDF



def phjWide2Long(phjDF,
                 phjReqVarList,
                 phjReqVarAllPresent = True,
                 phjAutoAgg = False,
                 phjColAgg = 'sum', # Currently the only option
                 phjRowAgg = 'sum', # Currently the only option
                 phjNewCatColNameStr = 'category',
                 phjNewAggColNameStr = 'count',
                 phjDropZeros = False,
                 phjPrintResults = False):
    """
    Converts a 'wide' dataframe to 'long' format.
    
    This function meets a specific data situation where an individual
    subject is described in a series of categorical variables and the
    additional numerical values are given in a series of variables
    which are entered as separate columns. Clearly, this situation is
    exactly what Pandas' wide_to_long() function is designed to do. This
    wrapper, however, automatically adds an appropriate prefix to the
    column headings to act as stubname and renames the column to more
    intuitive values.

    This function also provides the opportunity for duplicate columns and rows (as
    defined by a series of named columns) to be automatically aggregated before
    the wide_to_long() function is applied.
    
    The function retains all the named descriptive columns but then
    converts the series of numeric columns to just two columns, one
    called 'var' (phjPrefixStr) and the other called 'value' (phjValueStr).
    
    As a visual example, the following dataframe (df) consists of two
    categorical variables defining each row, namely cat1 and cat2. The
    remaining columns (stuff, things and value) represent variables that
    need to be used to convert to long function.
    
           cat1 cat2  stuff  things  value
        0     1    a   2230     489    143
        1     2    b   1134     267     87
        2     3    c   1165     256     25
        3     4    d   1176     232     47
        4     5    e   2279     478     86
        5     6    f   1165     276     67
        6     7    g   1176     287     87
        7     8    h   3456     850    207
        8     9    i   1156     245     34
        9    10    j   1176     223     62
    
    longdf = epy.phjWide2Long(phjDF = df,
                              phjReqVarList = ['cat1','cat2'],
                              phjReqVarAllPresent = True,
                              phjAutoAgg = True,
                              phjColAgg = 'sum', # Currently the only option
                              phjRowAgg = 'sum', # Currently the only option
                              phjNewCatColNameStr = 'category',
                              phjNewAggColNameStr = 'count',
                              phjDropZeros = False,
                              phjPrintResults = False)
    
    print(longdf)
    
        cat1 cat2 category  count
    0      1    a    stuff   2230
    1      1    a   things    489
    2      1    a    value    143
    3      2    b    stuff   1134
    4      2    b   things    267
    5      2    b    value     87
    6      3    c    stuff   1165
    7      3    c   things    256
    8      3    c    value     25
    9      4    d    stuff   1176
    10     4    d   things    232
    11     4    d    value     47
    12     5    e    stuff   2279
    13     5    e   things    478
    14     5    e    value     86
    15     6    f    stuff   1165
    16     6    f   things    276
    17     6    f    value     67
    18     7    g    stuff   1176
    19     7    g   things    287
    20     7    g    value     87
    21     8    h    stuff   3456
    22     8    h   things    850
    23     8    h    value    207
    24     9    i    stuff   1156
    25     9    i   things    245
    26     9    i    value     34
    27    10    j    stuff   1176
    28    10    j   things    223
    29    10    j    value     62

    """
    
    # The function will (hopefully) eventually return a 'long' version of the
    # dataframe. If a problem occurs, the original dataframe will be returned.
    # Determining whether a problem has occurred before returning can be done
    # by testing if phjTempLongDF variable contains long dataframe is None
    phjTempLongDF = None
    
    try:
        phjAssert('phjDF',phjDF,pd.DataFrame)
        
        phjAssert('phjReqVarAllPresent',phjReqVarAllPresent,bool)

        if phjReqVarAllPresent == True:
            phjAssert('phjReqVarList',phjReqVarList,(str,list),phjMustBePresentColumnList = list(phjDF.columns))
        else:
            phjAssert('phjReqVarList',phjReqVarList,(str,list))

        phjAssert('phjAutoAgg',phjAutoAgg,bool)
        phjAssert('phjColAgg',phjColAgg,str,phjAllowedOptions = ['sum']) # Currently only one option
        phjAssert('phjRowAgg',phjRowAgg,str,phjAllowedOptions = ['sum']) # Currently only one option
        phjAssert('phjNewCatColNameStr',phjNewCatColNameStr,str,phjMustBeAbsentColumnList = list(phjDF.columns))
        phjAssert('phjNewAggColNameStr',phjNewAggColNameStr,str,phjMustBeAbsentColumnList = list(phjDF.columns))
        phjAssert('phjDropZeros',phjDropZeros,bool)
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
        # Create a temporary copy of the dataframe which can be modified but, should
        # an error occur, the original dataframe can be returned unaltered
        phjTempDF = phjDF.copy(deep = True)

        # In most cases, the required list of variables should all be present in the
        # dataframe. However, in some cases, it might be that the data should only be
        # grouped by those listed variables that are present in the dataframe. This
        # situation has arisen when processing multiple files and in a small number
        # of files, one of the variables had not been included. Therefore, if
        # phjReqVarAllPresent is set to False, adjust to only include those required
        # variables that are present in the dataframe.
        if phjReqVarAllPresent == False:
            phjReqVarList = [c for c in phjReqVarList if c in list(phjTempDF.columns)]
        
        # Set default prefix and separator that will be used to rename column headings
        # to enable pd.wide_to_long() function to operate
        #phjDefaultPrefixStr = 'column'
        phjDefaultSeparator = '_'
        
        
        # Aggregate duplicate columns and rows
        # ------------------------------------
        if phjAutoAgg == True:
            phjTempDF = phjAggDupColsAndRows(phjDF = phjTempDF,
                                             phjReqVarList = phjReqVarList,
                                             phjReqVarAllPresent = phjReqVarAllPresent,
                                             phjAutoAgg = phjAutoAgg,
                                             phjColAgg = phjColAgg,
                                             phjRowAgg = phjRowAgg,
                                             phjPrintResults = phjPrintResults)
        
        # Add prefix to column headings not included in phjExceptionList
        # --------------------------------------------------------------
        phjTempDF = phjTempDF.rename(columns = phjAddColHeadingPrefix(phjColHeadingList = list(phjTempDF.columns),
                                                                      phjExceptColHeadingList = phjReqVarList,
                                                                      phjPrefixStr = phjNewAggColNameStr,   # 'count'
                                                                      phjSeparator = phjDefaultSeparator,   # '_'
                                                                      phjRemoveUnalteredEntries = True,
                                                                      phjPrintResults = phjPrintResults
                                                                     ))

        # Convert wide-to-long
        # --------------------
        try:
            phjTempLongDF = pd.wide_to_long(df = phjTempDF,
                                            stubnames = phjNewAggColNameStr,
                                            i = phjReqVarList,
                                            j = phjNewCatColNameStr,
                                            sep = phjDefaultSeparator,
                                            suffix = '.+').reset_index(drop = False)
            
            # Rename columns so they make more sense
            # (N.B. No longer required as column heading prefix used phjNewAggColNameStr parameter that
            #       was passed into the function.)
            #phjTempLongDF = phjTempLongDF.rename(columns = {phjDefaultPrefixStr:phjNewAggColNameStr})

        except ValueError as e:
            print('A ValueError occurred when converting a wide dataframe to long format ({}).'.format(e))
            phjTempLongDF = None

        except Exception as e:
            print('An unexpected {} error occurred when converting a wide dataframe to long format ({}).'.format(type(e).__name__,e))
            phjTempLongDF = None

        else:
            # Drop rows where aggregated column (e.g. 'count' column) is zero or NaN (or similar)
            if phjDropZeros == True:
                phjTempLongDF = phjTempLongDF.drop(phjTempLongDF[phjTempLongDF[phjNewAggColNameStr].fillna(0).eq(0)].index).reset_index(drop = True).copy(deep = True)

            # Having dropped rows where aggregated column is NaN (i.e. a float value), determine
            # whether all remaining values are integers (albeit expressed as .0 floats due to previous
            # existance of NaN values) and, if so, recast column as integer
            # (see answer by cs95 at:
            # https://stackoverflow.com/questions/49249860/how-to-check-if-float-pandas-column-contains-only-integer-numbers)
            # It is important to check that the column is float dtype otherwise a TypeError will be raised
            # because is_integer requires a float value.
            try:
                if phjTempLongDF[phjNewAggColNameStr].dtype == np.float64:
                    if (phjTempLongDF[phjNewAggColNameStr].apply(float.is_integer).all()) == True:
                        phjTempLongDF[phjNewAggColNameStr] = phjTempLongDF[phjNewAggColNameStr].astype('int64')

            except TypeError as e:
                print('A TypeError occurred when trying to convert column to integer dtype ({}).'.format(e))
                phjTempLongDF = None

            except Exception as e:
                print('An unexpected {} exception occurred when trying to convert column to integer dtype ({}).'.format(type(e).__name__,e))
                phjTempLongDF = None

            else:
                if phjPrintResults == True:
                    print('Long dataframe')
                    print('--------------')
                    print(phjTempLongDF)
                    print('\n')

    finally:
        # If phjTempLongDF is not None then return phjTempLongDF dataframe, otherwise return
        # original phjDF dataframe unaltered
        if phjTempLongDF is not None:
            return phjTempLongDF
        else:
            print('An error has occurred. The original dataframe has been returned unaltered.')
            return phjDF


if __name__ == '__main__':
    main()

