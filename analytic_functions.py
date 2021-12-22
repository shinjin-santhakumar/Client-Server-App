#this file will contain all the functions that we use to create the data that we will pass to the graphs

from datetime import date
from decimal import Decimal, DecimalException

# ----- check_float() -----
# Helper function for analytics, used for input validation.
# Passes in the value to be tested.
# Makes no external function calls.
# Checks the value can be expressed as a floating point number.
# Returns TRUE if valid, FALSE if invalid.
# -------------
def check_float(potential_float): 
    try:
        float(potential_float)
        return True

    except ValueError:
        return False
# --------------------------



# ----- most_funded_category_per_year() -----
# Helper function for analytics, namely... well, analytics_most_funded_category()
# Passes in the year to test for, and the datafile to be read.
# Makes no external function calls.
# Reads each entry, finds the pledged value, and increments it to the corresponding category if the year is correct.
# Returns a list containing the category with the highest amount pledged for the requested year, and that amount.
# ---------------------
def most_funded_category_per_year(year , file_data):
    category_dict = { # key=main category, value= total amount pledged for the year
        'Games':0, 'Design': 0, 'Technology': 0, 'Film & Video': 0, 'Music': 0, 
        'Publishing': 0, 'Fashion': 0, 'Food': 0, 'Art': 0, 
        'Comics': 0, 'Photography': 0, 'Theater': 0, 'Crafts': 0, 
        'Journalism': 0, 'Dance': 0}

    result = []

    if len(file_data) == 0 or file_data == [{}]:
        return result
    
    for key in file_data:
        if key['main_category'] in category_dict.keys():
            if check_float(key['pledged']):
                str = key['launched']
                if str[0:4] == year:
                    category_dict[key['main_category']] += float(key['pledged'])
    
    list_of_values = category_dict.values()
    max_value = max(list_of_values)
    result.append(max_value)

    max_key = max(category_dict, key=category_dict.get)
    result.append(max_key)

    return result
# -------------------------------------------



# ----- bad_date() -----
# Helper function for analytics, used for input validation.
# Passes in the date to be read, expected to be in the format "yyyy-mm-dd hh:mm:ss", or at least "yyyy-mm-dd"
# Makes no external function calls.
# Reads the date and checks it against various criteria:
# - A project could not be launched before 2008, when Kickstarter was created.
# - A project should not be made after the year 3000, when humans have learned ascension, computers have become obsolete, and the Earth has been reclaimed by nature.
# - A project's month should not be less than 1, for January, or greater than 12, for December.
# - A project's day should not be less than 1 or greater than 31, because those days do not exist.
# Returns a boolean of TRUE indicating invalid date, or FALSE if correct.
# -----------
def bad_date(date):

    if(len(date) < 10):
        return True
    try:
        yearNum = int(date[0:4])
        monthNum = int(date[5:7])
        dayNum = int(date[8:10])
    except:
        return True

    if yearNum < 2008 or yearNum > 3000:
        return True
    if  monthNum < 1 or monthNum > 12:
        return True
    if dayNum < 1 or dayNum > 31:
        return True
    return False
# -----------------------



# ----- average_length_ks() -----
# Helper function for analytics, namely make_length_analytic()
# Passes in the datafile to be read.
# Calls on bad_date() for input validation.
# Reads each entry, collects the start and end date, adds the difference to the entry's year.
# Returns the completed list of years, list of average kickstarter lengths for those years, and the total average across all years.
# ---------------
def average_length_ks(pyfile):
    labels = [] #labels for each datapoint
    returnData = [] #datapoints(average length per year)
    totalAverage = 0
    totalDates = 0
    dataByMonth = [] #
    #listValues = ["year",0.0,0]#"year or total", sum of lengths, number of values

    if len(pyfile) == 0 or pyfile == [{}]:
        return labels,returnData,totalAverage


    for i in pyfile: # For every entry,
        if bad_date(i["launched"]) or bad_date(i["deadline"]): # Check if dates are valid,
            continue
        startDate = date(int(i["launched"][0:4]),int(i["launched"][5:7]),int(i["launched"][8:10])) # Gather the starting time
        endDate = date(int(i["deadline"][0:4]),int(i["deadline"][5:7]),int(i["deadline"][8:10])) # and the ending time,
        
        timeBetween = endDate - startDate # Find the difference,

        if timeBetween.days < 0:
            continue
        
        yearNotInList = True
        for val in range(len(dataByMonth)): # Then for all currently collected data,
            if dataByMonth[val][0] == i["launched"][0:4]: # Find the year,
                yearNotInList = False
                dataByMonth[val][1] = dataByMonth[val][1] + timeBetween.days # add this entry's time to the year's total,
                dataByMonth[val][2] = dataByMonth[val][2] + 1 # and increment the project count.
        if yearNotInList:
            dataByMonth.append([i["launched"][0:4],timeBetween.days,1]) # If year is missing, these are the first values for it.
    
    #sort by year

    for iteration in dataByMonth: # For every year in the collected data,
        labels.append(iteration[0]) # Add the year to labels list,
        returnData.append(iteration[1]/iteration[2]) # Add that year's (total length / total projects) average to returnData,
        totalDates = iteration[2] + totalDates # and calculate the totals.
        totalAverage = iteration[1] + totalAverage


    if totalDates == 0:#error check for if there were only bad kickstarters passed in to prevent divide by zero
        totalAverage = 0
    else:
        totalAverage = totalAverage/totalDates

    # Finally, return everything.
    return labels, returnData,totalAverage
# --------------------------------



# ----- countProjects() -----
# Helper function for analytics, namely popularMonth().
# Passes in the datafile to be read.
# Calls on bad_date for input validation.
# Reads each entry, collects the date launched, and increments the corresponding list.
# Returns the completed dictionary.
# ----------------
def countProjects(dataFile):
    # list format: {Year}:[Jan,Feb,Mar,Apr,May,Jun,Jul,Aug,Sep,Oct,Nov,Dec]
    # each value represents the number of projects launched in that month for that year.
    retDict = {}

    if len(dataFile) == 0 or dataFile == [{}]:
        return retDict


    yearList = gatherYears(dataFile)
    for year in yearList:
        retDict[str(year)] = [0,0,0,0,0,0,0,0,0,0,0,0]

    for item in dataFile:
        launchTime = item['launched'] # 2012-03-17 03:24:11
        if (bad_date(launchTime) == False): #checks to see if launch time is actually a date
            launchVals = launchTime.split('-') # ['2012', '03', '17 03:24:11']
            retDict[launchVals[0]][(int(launchVals[1]) - 1)] += 1

    return retDict
# ----------------------------



# ----- count_cat_fail_success() -----
# Helper function for analytics, namely category_fail()
# Passes in the data file to be read.
# Makes no external function calls.
# Reads each entry and increments the fail or success value for its category, depending on its state.
# Returns the list of category titles, and the completed list of ratios for those categories
# -----------------
def count_cat_fail_success(data):

    if len(data) == 0 or data == [{}]:
        return [{}]

    category_dict = { # key=main category, value=#successful[0],#failed[1]
        'Games':[0,0], 'Design':[0,0], 'Technology':[0,0], 'Film & Video':[0,0], 'Music':[0,0], 
        'Publishing':[0,0], 'Fashion':[0,0], 'Food':[0,0], 'Art':[0,0], 
        'Comics':[0,0], 'Photography':[0,0], 'Theater':[0,0], 'Crafts':[0,0], 
        'Journalism':[0,0], 'Dance':[0,0]}
    for proj in data:
        if proj['state'] == 'successful':
            category_dict[proj['main_category']][0] += 1
        elif proj['state'] == 'failed' or proj['state'] == 'canceled':
            category_dict[proj['main_category']][1] += 1
   
    category_names = list(category_dict.keys())
    # FOR DEBUGGING: category_successful = [x[0] for x in list(category_dict.values())]
    # FOR DEBUGGING: category_failed = [x[1] for x in list(category_dict.values())]
    category_failed_ratio = [x[1] / (x[0] + x[1]) if x[0] or x[1] else 0 for x \
        in list(category_dict.values())] # list comprehension
    return category_names, category_failed_ratio
# -------------------------------------



# ----- findAmbitious() -----
# Helper function for analytics, namely ambitiousProjects()
# Passes in the data file to be read.
# Calls on bad_date() for input validation.
# Reads each entry, locates which year and month it belongs to, compares goals, keeps the higher one.
# If goals are equal, keeps the project with the highest pledged.
# Returns the completed and sorted-by-date dictionary
# -------------
def findAmbitious(dataFile):
    # dictionary format: {year-month}:[ID,goal,pledged]
    retDict = {}
    
    if len(dataFile) == 0 or dataFile == [{}]:
        return retDict


    for item in dataFile:
        if (bad_date(item['launched']) == False): # 2012-03-17 03:24:11
            date = item['launched'][0:7] # 2012-03
            
            try:
                int(item['ID'])
                Decimal(item['goal'])
                Decimal(item['pledged'])
            except (ValueError, DecimalException):
                continue
            
            itemVals = [int(item['ID']),int(Decimal(item['goal'])),int(Decimal(item['pledged']))]

            try:
                compVals = retDict.get(date)
                # if goal is higher, or goal is equal and pledged is higher
                if ((itemVals[1] > compVals[1]) or ((itemVals[1] == compVals[1]) and (itemVals[2] > compVals[2]))):
                    retDict[date] = itemVals
            except:
                retDict.setdefault(date, itemVals)
    sortDict = {}
    for i in sorted(retDict):
        sortDict[i] = retDict[i]
    return sortDict
# ---------------------------



# ----- gatherYears() -----
# Helper function for analytics, namely ambitiousProjects() and countProjects().
# Passes in the data file to be read.
# Calls on bad_date for input validation.
# Reads each entry, adds a new year if it is not yet added.
# Returns the completed list of years.
# -------------
def gatherYears(dataFile):    
    retList = []
    
    if len(dataFile) == 0 or dataFile == [{}]:
        return retList 

    for item in dataFile:
       date =  item['launched'] # 2012-03-17 03:24:11
       if (bad_date(date) == False):
           try: retList.index(date[0:4]) # find 2012 in list, if not...
           except: retList.append(date[0:4]) # add 2012 to list
    retList.sort() # sort years in ascending order
    return retList
# -------------------------



# ----- createDropdown() -----
# Helper function for analytics, namely ambitiousProjects() and countProjects().
# Passes in the figure to edit, the number of bars, the keys for the bar data, the list of tab titles, and the number of bars to be seen on each tab.
# Makes no external function calls.
# Creates a dropdown menu with the desired characteristics, and applies it to the figure.
# Returns the edited figure.
# ----------------------------
def createDropdown(figure,barCount,titleKeys,titleList,barsPerTab):
    tabList = []
    visList = []
    labelList = []
    for i in range(barCount): # Add a visual boolean for every bar
        visList.append(False)
    for key in titleKeys: # Add each desired tab title to a list
        labelList.append(key)
    for i in range(int(barCount / barsPerTab)): # Add a new tab to tabList (number of tabs = barCount divided by barsPerTab)
        tabList.append(
            dict(
                label=labelList[i],
                method="update",
                args=[{"visible": []}, # This blank list will be filled later
                {"title": titleList[i]}]
            )
        )
    
    visIndex = 0
    for item in tabList: # For every tab to be made,
        copyVis = visList.copy() # Create a copy of our visList
        try:
            for i in range(barsPerTab):
                copyVis[(visIndex + i)] = True # and allow only the necessary bars to be seen
        except:
            print('An error occurred! Graph may not display correctly!') # If something bad happens, don't crash
        finally:
            item['args'][0]['visible'] = copyVis # Update this bar's visible arguments to the proper values instead of a blank list
            visIndex += barsPerTab # Increment visIndex for the next loop

    # Update the figure with its new, fancy dropdown menu!
    figure.update_layout(
        updatemenus=[
            dict(
                active=0,
                buttons=tabList
            )
        ]
    )
    return figure
# ----------------------------

# ----- count_categories_per_month() -----
# Helper function for analytics, namely category_per_month().
# Passes in the data file to be read.
# Makes no external function calls.
# Counts the number of projects belonging to each month and its corresponding category.
# Returns the completed dictionary of categories for all months.
# ------------------
def count_categories_per_month(data):
    # Check if it is necessary to create dictionary
    if len(data) == 0 or not data[0]:#quick check to see if pyfile is either empty or has an empty dictionary inside
        print("empty file passed into analytic") 
        return [{}]

    # Initialize variables
    month_dict = {'01':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], '02':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        '03':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], '04':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], '05':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        '06':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], '07':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], '08':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        '09':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], '10':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], '11':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        '12':[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]}
    categories = ['Games', 'Design', 'Technology', 'Film & Video', 'Music', 'Publishing',
        'Fashion', 'Food', 'Art', 'Comics', 'Photography', 'Theater', 'Crafts', 'Journalism',
        'Dance']

    # Increment each category respectively
    for proj in data:
        projDate = proj['launched']
        if bad_date(projDate):
            continue
        projMonth = projDate[5:7] # substring of the month 
        projCat = proj['main_category']
        if projCat in categories:
            catIndex = categories.index(projCat)
            month_dict[projMonth][catIndex] += 1 #increment up that category 
    return month_dict
# --------------------------------------


# ----- get_countrys_category() -----
# Helper function for analytics, namely popular_category_perNation().
# Passes in the data file to be read.
# Makes no external function calls.
# Counts the number of projects belonging to each country, and its corresponding category.
# Returns the completed dictionary of categories for all countries.
# ----------------
def get_countrys_category(data):
    # Check if it is necessary to create dictionary
    if len(data) == 0 or not data[0]:#quick check to see if pyfile is either empty or has an empty dictionary inside
        print("empty file passed into analytic") 
        return {}

    # Initialize variables
    categories = ['Games', 'Design', 'Technology', 'Film & Video', 'Music', 'Publishing',
        'Fashion', 'Food', 'Art', 'Comics', 'Photography', 'Theater', 'Crafts', 'Journalism',
        'Dance'] 
    analyticDict = {}

    # Loop through dataset to add entries
    for proj in data:
        projCountry = proj['country']
        projCat = proj['main_category']
        if projCat not in categories:
            continue
        catIndex = categories.index(projCat)
        if projCountry in analyticDict.keys(): # no need to create new entry in the dictionary
            analyticDict[projCountry][catIndex] += 1
        else:
            #makes entry for the newly detected country
            analyticDict[projCountry] = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
            analyticDict[projCountry][catIndex] += 1 

    return analyticDict
# ---------------------------------



##Successful words analytics
def count_words(data):

    count_dict = {}
    
    for item in data:
        if 'state' in item.keys():
            if(item['state'] == "successful"):
                res = item['name'].split()
                for i in res:
                    if(len(i) >= 4):
                        if i in count_dict:
                            count_dict[i] += 1
                        else:
                            count_dict[i] = 1
    

    return count_dict