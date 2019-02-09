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



if __name__ == '__main__':
    main()

