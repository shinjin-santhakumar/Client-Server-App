import os
import time
import json
import io
import time
#from typing import final
from flask import Flask, render_template, request, redirect, url_for, flash
from userInput import exampleForm, kickStarterForm # import forms here. We import these to keep ourselves organized.
from category_searches import highest_usd_pledged_search#functions from the category_searches file. Use them to search a specific category
from add_function import add_to_json
import plotly # pip install plotly==5.3.1
from plotly.subplots import make_subplots
import plotly.graph_objects as go
#from analytic_functions import average_length_ks, count_cat_fail_success, most_funded_category_per_year, bad_date, countProjects, count_cat_fail_success, findAmbitious, gatherYears
from analytic_functions import *
from collections import Counter
#from analytic_functions import average_length_ks, most_funded_category_per_year, bad_date, countProjects, count_words,count_categories_per_month
# notice here that index.html does not need to be passed in. That is because it is in the templates folder
# In the future we might use templates to reduce redundant html code.

# instructions to run app
# py -m venv env
# env/Scripts/Activate
# export FLASK_APP=app_interface.py
# export FLASK_DEBUG=1
# flask run

# dummy_file.json

# ----- GLOBAL VARIABLES -----
FILENAME =  'ks-projects-201801.json' # Name of .json data file
DATA = list() # .load()ed list of dictionaries containing all data
# Incremental analytic dictionaries
COUNTDICT = {}
YEARDICT = dict() # What is this? Why is it called this? Consider using gatherYears() and use list instead?
#POPMONTH_PROJDICT = dict()
# Incremental analytic booleans
UPDATE_COUNTWORDS = True
UPDATE_COUNTPROJECTS = True
# -----------------------------

# ----- SETUP / NECESSARY FUNCTIONS -----
# Helper function to make searching more user-friendly and less crash-inducing
def search_helper(key, method="GET", input_type=''):
    if method == 'POST': # will only run below code if client is posting
        value = request.form.get(key) # request.form looks at the html in current route
        if not value or value.isspace(): # refresh page if search is blank
            return redirect(request.url)
        return redirect(url_for('results', key=key, value=value)) # go to results function
    return render_template('search-input.html', type=input_type, name=key) # load page
# -------------------

def analytic_helper_edit(proj, new_state, new_name, new_launched):
    analytic_helper_delete(proj, new_launched)
    analytic_helper_add(proj, new_state, new_name, new_launched)

def analytic_helper_add(proj, state, name, date_launched):
    global COUNTDICT
    global YEARDICT
    
    if(state == "successful" or (state == '\n' and proj['state'] == "successful")):
            if name != '\n':
                res = name.split()
            else:
                res = proj['name'].split()
            for i in res:
                if(len(i) >= 4):
                    if i in COUNTDICT:
                        COUNTDICT[i] += 1
                    else:
                        COUNTDICT[i] = 1

    if date_launched != '\n':
        launchVals = date_launched.split('-')
        if launchVals[0] in YEARDICT.keys():
            YEARDICT[launchVals[0]][(int(launchVals[1]) - 1)] += 1

def analytic_helper_delete(i,date_launched):
    global COUNTDICT
    global YEARDICT
    #for incremental analytics count words
    if(i['state'] == "successful"):
        res = i['name'].split()
        for x in res:
            if x in COUNTDICT:
                if(len(x) >= 4):
                    COUNTDICT[x] -= 1
    #incremental analytics end ------
    #for incremental analytics count projects
    if date_launched != '\n':
        launchVals = i["launched"].split('-')
        if launchVals[0] in YEARDICT.keys():
            YEARDICT[launchVals[0]][(int(launchVals[1]) - 1)] -= 1

    #incremental analytics end ------

app = Flask(__name__) # neccessary for flask

# Data preparation
@app.before_first_request
def loadJsonFile():
    file = os.path.join(app.static_folder, FILENAME) # location of json file
    with open(file ,encoding='utf-8-sig') as json_file:
        global DATA
        DATA = json.load(json_file) # json --> list of dictionaries
# ---------------------------------------

# ----- DIRECTORIES AND METHODS -----
# Homepage Directory
@app.route("/")
def index():
    return render_template('index.html')
# -----------------

# Search by ID Method
@app.route("/id", methods=['POST','GET'])
def search_ID():
    return search_helper('ID', request.method, "number")
# -----------------

# Search by Name Method
@app.route("/name", methods=['POST','GET'])
def search_name():
    return search_helper('name', request.method, "text")
# -----------------

# Search by Category Method
@app.route("/category", methods=['POST','GET'])
def search_category():
    return search_helper('category', request.method, "text")
# -----------------

# Search by State Method
@app.route("/state", methods=['POST','GET'])
def search_state():
    return search_helper('state', request.method, "text")
# -----------------

# Search by Date Launched Method
@app.route("/launched", methods=['POST','GET'])
def search_month():
    return search_helper('launched', request.method, "month")
# -----------------

# Analytics Directory
@app.route("/analytics",methods=['POST','GET'])
def redirect_to_analytics():
    return render_template('analytic_options.html')
# -----------------

# Update Kickstarter Method
@app.route("/update_database")
def update_database():
    file = os.path.join(app.static_folder, FILENAME) # location of json file
    with open(file,"r+" ,encoding='utf-8-sig') as json_file:
        json_file.seek(0) # go to start of file
        json.dump(DATA, json_file, indent=4) # write data to json file
        # necessary since we open the file with r+
        # if we dump a lesser amount of lines than the file originally had,
        # we end up with trailing garbage values; truncate() gets rid of that
        json_file.truncate()
    return render_template('results.html', projects=[], message="Successfully updated database file")
# -----------------

# Import New Datafile Method
@app.route("/import_file", methods=['POST','GET'])
def import_file():
    global UPDATE_COUNTWORDS
    global UPDATE_COUNTPROJECTS
    if request.method == 'POST':
        if 'passed_file' not in request.files:
            print('No file part')
            return redirect(request.url)
        file = request.files["passed_file"]
        if file: #and allowed_file(request.url)
            file_path = os.path.join(app.static_folder, file.filename)
            file.save(file_path)
            with open(file_path, encoding='utf-8-sig') as json_file:
                global DATA
                DATA = json.load(json_file) # json --> list of dictionaries
            global FILENAME
            FILENAME = file.filename
            UPDATE_COUNTPROJECTS = True
            UPDATE_COUNTWORDS = True
            return redirect(request.url)
    return render_template("import_file.html")
# -----------------

# Display Search Results Method
@app.route("/search/key=<key>&value=<value>")
def results(key, value):
    #file = os.path.join(app.static_folder, FILENAME) # location of json file
    projects = [] # the project(s) being looked for
    #with open(file, encoding='utf-8-sig') as json_file:
        #DATA = json.load(json_file) # json --> list of dictionaries
    for proj in DATA:
        if key == 'ID' and value == proj.get(key):
            projects.append(proj)
        elif (key == 'name' or key == 'state' or key == 'category' or key == 'launched') and value.lower() in proj.get(key).lower():
            projects.append(proj)
    return render_template('results.html', projects=projects, message="Project not found")
# -----------------

# Search Directory
@app.route("/search",methods=['POST','GET'])
def search():
    if request.method == 'POST': # will only run below code if client is posting
        choiceSearch = request.form.get('choice')
        if not choiceSearch or choiceSearch.isspace():
            return redirect(request.url)
        #return redirect(url_for('get_id', id=id))
    return render_template('search-options.html')
# -----------------

# Update Kickstarter Directory
@app.route("/update_ks_route",methods=['POST','GET'])
def update_ks():
    if request.method == 'POST': # will only run below code if client is posting
        choiceSearch = request.form.get('choice')
        if not choiceSearch or choiceSearch.isspace():
            return redirect(request.url)
        #return redirect(url_for('get_id', id=id))

    return render_template('updateDB-options.html')
# -----------------

# Delete Kickstarter Directory
@app.route("/delete",methods=['POST','GET'])
def delete_kickstarter():
    if request.method == 'POST': # will only run below code if client is posting
        deleteChoice = request.form.get('id_to_delete')
        if not deleteChoice or deleteChoice.isspace():
            return redirect(request.url)
        return redirect(url_for('do_delete', id_to_delete=deleteChoice))
    return render_template('deleteKickstarter.html')
# -----------------

# Delete Kickstarter Method
@app.route("/delete/<id_to_delete>")
def do_delete(id_to_delete):
    # Import global variables
    global COUNTDICT
    global YEARDICT

    # Variable initialization
    located = False
    pos = 0

    # Search data for requested ID to delete
    for i in DATA:
        if i['ID'] == id_to_delete: 
            located = True
            break
        else: 
            pos += 1
    
    # Delete Kickstarter, or return error message if ID was never found
    if located:
        poppedProj = DATA.pop(pos)
        analytic_helper_delete(poppedProj,"something")

        successMessage = "Project %s was deleted successfully."%id_to_delete
        return render_template('results.html', projects=[], message=successMessage)
    else:
        errorMessage = "Error: Project %s could not be found!"%id_to_delete
        return render_template('results.html', projects=[], message=errorMessage)
# -----------------

# Add Kickstarter Method
@app.route("/add",methods=['POST','GET']) # This was marked as not working, is this still nonfunctional?
def add_kickstarter():
    if request.method == 'POST': # will only run below code if client is posting
        ksToAdd = kickStarterForm(request.form.get('id'),request.form.get('name'),request.form.get('category'),request.form.get('main_category'),request.form.get('currency'),
        request.form.get('deadline'),request.form.get('goal'),request.form.get('date_launched'),request.form.get('time_launched'),request.form.get('number_pledged'),request.form.get('state'),
        request.form.get('number_backers'), request.form.get('country'), request.form.get('amount_usd_pledged'), request.form.get('amount_usd_pledged_real'))
        if not len(ksToAdd.error_msgs) == 0:
            return render_template('results.html', projects=[], message="Error on one or more fields")

        add_to_json(DATA,ksToAdd.id,ksToAdd.name,ksToAdd.category,ksToAdd.main_category,ksToAdd.currency,ksToAdd.deadline,ksToAdd.goal,ksToAdd.date_launched,
            ksToAdd.number_pledged,ksToAdd.state,ksToAdd.number_backers,ksToAdd.country,ksToAdd.amount_usd_pledged,ksToAdd.amount_usd_pledged_real)

        analytic_helper_add(DATA[0], ksToAdd.state, ksToAdd.name, ksToAdd.date_launched)#Data[0] is a hack, add will always have a new name so the first argument isn't used.(used in edit)


        return render_template('results.html', message="Successfully added kickstarter "+ksToAdd.name)
    return render_template('addKickstarter.html')
# -----------------

# Edit Kickstarter Directory
@app.route("/edit", methods=['POST','GET'])
def edit_project():
    if request.method == 'POST':
        id = request.form.get('id_to_edit')
        # these if statements prevent flask errors when any new value is left blank
        if not id or id.isspace():
            return redirect(request.url)
        new_id = request.form.get('new_id')
        if not new_id:
            new_id = '\n'
        new_name = request.form.get('new_name')
        if not new_name:
            new_name = '\n'
        new_category = request.form.get('new_category')
        if not new_category:
            new_category = '\n'
        new_main_category = request.form.get('new_main_category')
        if not new_main_category:
            new_main_category = '\n'
        new_currency = request.form.get('new_currency')
        if not new_currency:
            new_currency = '\n'
        new_deadline = request.form.get('new_deadline')
        if not new_deadline:
            new_deadline = '\n'
        new_goal = request.form.get('new_goal')
        if not new_goal:
            new_goal = '\n'
        new_launched = request.form.get('new_launched')
        if not new_launched:
            new_launched = '\n'
        else:
            # slicing is done to match the format of the rest of the launched values
            new_launched = new_launched[:10] + " " + new_launched[11:]
        new_pledged = request.form.get('new_pledged')
        if not new_pledged:
            new_pledged = '\n'
        new_state = request.form.get('new_state')
        if not new_state:
            new_state = '\n'
        new_backers = request.form.get('new_backers')
        if not new_backers:
            new_backers = '\n'
        new_country = request.form.get('new_country')
        if not new_country:
            new_country = '\n'
        return redirect(url_for('do_edit', id=id, new_id=new_id, new_name=new_name, new_category=new_category,
            new_main_category=new_main_category, new_currency=new_currency, new_deadline=new_deadline,
            new_goal=new_goal, new_launched=new_launched, new_pledged=new_pledged, new_state=new_state,
            new_backers=new_backers, new_country=new_country))
    return render_template('edit.html')
# -----------------

# Edit Kickstarter Method
@app.route('''/edit/id=<id>&new_id=<new_id>&new_name=<new_name>&new_category=<new_category>
    &new_main_category=<new_main_category>&new_currency=<new_currency>&new_deadline=<new_deadline>
    &new_goal=<new_goal>&new_launched=<new_launched>&new_pledged=<new_pledged>&new_state=<new_state>
    &new_backers=<new_backers>&new_country=<new_country>''', methods=['POST','GET'])
def do_edit(id, new_id, new_name, new_category, new_main_category, new_currency, new_deadline, new_goal,
    new_launched, new_pledged, new_state, new_backers, new_country):
    projectFound = False # the project being looked for

    global COUNTDICT
    global YEARDICT

    for proj in DATA:
        if id == proj.get('ID'):
            projectFound = True


            analytic_helper_edit(proj, new_state, new_name, new_launched)

            if new_id != '\n':
                proj['ID'] = new_id
            if new_name != '\n':
                proj['name'] = new_name
            if new_category != '\n':
                proj['category'] = new_category
            if new_main_category != '\n':
                proj['main_category'] = new_main_category
            if new_currency != '\n':
                proj['currency'] = new_currency
            if new_deadline != '\n':
                proj['deadline'] = new_deadline
            if new_goal != '\n':
                proj['goal'] = new_goal
            if new_launched != '\n':
                proj['launched'] = new_launched
            if new_pledged != '\n':
                proj['pledged'] = new_pledged
            if new_state != '\n':
                proj['state'] = new_state
            if new_backers != '\n':
                proj['backers'] = new_backers
            if new_country != '\n':
                proj['country'] = new_country
            break
    if not projectFound:
        return render_template('results.html', projects=[], message="Project not found")
    hasChanged = True
    return render_template('results.html', projects=[proj])
# ---------------------





# ----- ANALYTIC METHODS -----
# Utilize analytics.html and render_template() to display graph
# Follow a general form: Collect data, Create, Format, and Export Graph
# ----------
@app.route("/analytic_likely_fail")
# Analytic expressing all categories and their failure state ratio
# Uses count_cat_fail_success() for data collection
# Not incremental
def category_fail():
    # Collect data
    category_names, category_failed_ratio = count_cat_fail_success(DATA)

    # Create the graph
    fig = go.Figure(data=[
        go.Bar(x=category_names, y=category_failed_ratio)
    ])

    # Format the graph
    fig.update_layout(
        barmode='stack', title="Ratio of failed projects in each main category", xaxis_title="Main categories",
        yaxis_title="Ratio of failed projects"
    )
    fig.update_xaxes(categoryorder='total ascending')

    # Export the graph
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template('analytics.html', graphJSON=graphJSON)
# ----------

@app.route("/analytic_avg_length_ks")
# Analytic expressing the average length of a Kickstarter for all available years
# Uses average_length_ks() for data collection
# Not incremental
def make_length_analytic():
    # Collect data
    labels, analyticByMonth, totalAverage = average_length_ks(DATA)

    # Create the graph
    fig = go.Figure(data=[
        go.Bar(x=labels, y=analyticByMonth)
    ])

    # Format the graph
    fig.update_layout(
        barmode='stack', title="Average Expected Length of Kickstarter by Year", xaxis_title="Year",
        yaxis_title="Average expected length(days)"
    )
    fig.update_xaxes(categoryorder='total ascending')

    # Export the graph
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template('analytics.html', graphJSON=graphJSON)
# ----------

@app.route("/analytics_most_funded_category")
# Analytic expressing the most funded category each year, and the amount
# Uses most_funded_category_per_year() for data collection
# Not incremental
def analytics_most_funded_category():

    # Initialize variables
    list_of_categories = []
    list_of_years = ['2009','2010','2011','2012','2013','2014','2015','2016','2017','2018'] # Consider using gatherYears(), or incremental global variable.
    list_of_values = []
    temp = []

    # Collect data
    for str in list_of_years:
        temp = most_funded_category_per_year(str,DATA)
        #print(*temp, sep = "\n")
        list_of_values.append(temp[0])
        list_of_categories.append(temp[1])

    for i in range(len(list_of_years)):
        list_of_years[i] = list_of_years[i] + " " + list_of_categories[i]

    # Create the graph
    fig = go.Figure(data=[
        go.Bar(x=list_of_years, y=list_of_values) # create the bar chart
    ])

    # Format the graph
    fig.update_layout(
        title="Most Funded Category for each year", xaxis_title="Year",
        yaxis_title="Total Amount Pledged in Most Funded Category"
    )

    # Export the graph
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template('analytics.html', graphJSON=graphJSON)
# ----------

@app.route("/analytics_popmonth")
# Analytic expressing the number of projects launched each month across all years
# Uses countProjects() for data collection and createDropdown() to help with formatting
# Incremental
def popularMonth():
    # Import global variables
    global YEARDICT
    #global POPMONTH_PROJDICT
    global UPDATE_COUNTPROJECTS

    # Incremental: Begin start time and check if data needs updating
    start = time.time()

    if(UPDATE_COUNTPROJECTS): # if data has been changed, renew dictionary
        projDict = countProjects(DATA)
        #POPMONTH_PROJDICT = projDict
        YEARDICT = projDict # Why?
        UPDATE_COUNTPROJECTS = False 
    else: # if data has stayed constant, use existing dictionary
        projDict = YEARDICT

    # Initialize variables
    monthList = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
    yearList = projDict.keys()
    titleList = []
    barCount = 0

    # Create the graph
    fig = go.Figure()
    fig.update_layout(
        title="Kickstarters launched across all years",
        xaxis_title="Month",
        yaxis_title="Number of projects launched"
    )

    # Data collection
    for year in yearList:
        fig.add_trace(go.Bar(
            x=monthList,
            y=projDict[year],
            name="Number of Projects"
        ))
        barCount += 1
        titleList.append("Kickstarters launched in " + year)

    # Add dropdown menu
    finishedFigure = createDropdown(fig,barCount,yearList,titleList,1)

    # Prepare to export graph
    graphJSON = json.dumps(finishedFigure, cls=plotly.utils.PlotlyJSONEncoder)

    # Incremental: Stop timer and print result
    end = time.time()
    print(end - start)

    return render_template('analytics.html', graphJSON=graphJSON)
# ----------

@app.route("/analytics_popcat")
# Analytic expressing the most popular category each month, without respect to year
# Uses count_categories_per_month() for data collection.
# Not incremental
def category_per_month():
    # Variable initialization
    categories = ['Games', 'Design', 'Technology', 'Film & Video', 'Music', 'Publishing',
        'Fashion', 'Food', 'Art', 'Comics', 'Photography', 'Theater', 'Crafts', 'Journalism',
        'Dance']
    finalListCat = []
    finalListCount = []
    final_Dict = {}
    # listMonth = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

    # Data collection
    final_Dict = count_categories_per_month(DATA)
   
    for key in final_Dict.keys():
        monthList = final_Dict[key]
        max_Ind = monthList.index(max(monthList))
        cat = categories[max_Ind]
        finalListCat.append(cat)
        finalListCount.append(monthList[max_Ind])

    # Create graph
    fig = go.Figure(
        data =[go.Bar(name='January', x=categories, y=final_Dict['01']),
            go.Bar(name='February', x=categories, y=final_Dict['02']),
            go.Bar(name='March', x=categories, y=final_Dict['03']),
            go.Bar(name='April', x=categories, y=final_Dict['04']),
            go.Bar(name='May', x=categories, y=final_Dict['05']),
            go.Bar(name='June', x=categories, y=final_Dict['06']),
            go.Bar(name='July', x=categories, y=final_Dict['07']),
            go.Bar(name='August', x=categories, y=final_Dict['08']),
            go.Bar(name='September', x=categories, y=final_Dict['09']),
            go.Bar(name='October', x=categories, y=final_Dict['10']),
            go.Bar(name='November', x=categories, y=final_Dict['11']),
            go.Bar(name='December', x=categories, y=final_Dict['12'])])

    # Format graph
    fig.update_layout(
        barmode='group', title="Most popular Category per Month", xaxis_title="Main categories",
        yaxis_title="Project Count"
    )
    fig.update_xaxes(categoryorder='total ascending')

    # Export graph
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template('analytics.html', graphJSON=graphJSON)
# ----------

@app.route("/analytics_ambitious")
# Analytic expressing the most ambitious project each month, its goal, and the amount pledged
# Uses gatherYears() and findAmbitious() for data collection, createDropdown() to help with formatting
# Not incremental
def ambitiousProjects():
    # Initialize variables
    monthList = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
    yearList = gatherYears(DATA)
    projectDict = findAmbitious(DATA) # Primary data-collecting function
    titleList = []
    barCount = 0

    # Create the graph
    fig = go.Figure() # Make the figure and add basic details
    fig.update_layout(
        title="Most Ambitious Projects",
        xaxis_title="Month",
        yaxis_title="US $"
    )

    # Data processing
    for year in yearList: # For every year,
        IDList = [] # Collect the ID's,
        goalList = [] # goals,
        pledgeList = [] # and amount pledged
        for m in range(1,13): # Across each year-month combination
            date = '-'.join((year,str(m).zfill(2)))
            try:
                proj = projectDict.get(date)
                IDList.append(('ID: ' + str(proj[0])))
                goalList.append(proj[1])
                pledgeList.append(proj[2])
            except:
                pass
        fig.add_trace(go.Bar( # Then, add a bar for this year-month's goals
            x=monthList,
            y=goalList,
            name='Goal',
            hovertext=IDList
        ))
        fig.add_trace(go.Bar( # and add a bar for this year-month's pledges
            x=monthList,
            y=pledgeList,
            name='Pledges',
            hovertext=IDList
        ))
        barCount += 2
        titleList.append("Most Ambitious Projects for " + year)

    # Format graph
    finishedFigure = createDropdown(fig,barCount,yearList,titleList,2)

    # Finally, export the graph
    graphJSON = json.dumps(finishedFigure, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template('analytics.html', graphJSON=graphJSON)
# ----------

@app.route("/analytics_popnation")
# Analytic expressing the most popular category for each available nation
# Uses get_countrys_category() for data collection.
# Not incremental
def popular_category_perNation():
    # Data collection
    countryDict = get_countrys_category(DATA)

    # Variable initialization
    categories = ['Games', 'Design', 'Technology', 'Film & Video', 'Music', 'Publishing',
        'Fashion', 'Food', 'Art', 'Comics', 'Photography', 'Theater', 'Crafts', 'Journalism',
        'Dance']
    catList = []
    finalListCountry = []
    finalListCat = []
    finalListCount = []

    # Data processing
    for i in countryDict:
        catList = countryDict[i]
        max_Ind = catList.index(max(catList))
        finalListCountry.append(i)
        finalListCount.append(catList[max_Ind])
        finalListCat.append(categories[max_Ind])
    keysList = list(countryDict.keys())

    # Debug
    print(countryDict[keysList[0]])

    # Create graph
    fig = go.Figure(
        data =[go.Bar(name=keysList[0], x=categories, y=countryDict[keysList[0]]),
            go.Bar(name=keysList[1], x=categories, y=countryDict[keysList[1]]),
            go.Bar(name=keysList[2], x=categories, y=countryDict[keysList[2]]),
            go.Bar(name= keysList[3], x=categories, y=countryDict[keysList[3]]),
            go.Bar(name= keysList[4], x=categories, y=countryDict[keysList[4]]),
            go.Bar(name= keysList[5], x=categories, y=countryDict[keysList[5]]),
            go.Bar(name= keysList[6], x=categories, y=countryDict[keysList[6]]),
            go.Bar(name= keysList[7], x=categories, y=countryDict[keysList[7]]),
            go.Bar(name= keysList[8], x=categories, y=countryDict[keysList[8]]),
            go.Bar(name= keysList[9], x=categories, y=countryDict[keysList[9]]),
            go.Bar(name= keysList[10], x=categories, y=countryDict[keysList[10]]),
            go.Bar(name= keysList[11], x=categories, y=countryDict[keysList[11]]),
            go.Bar(name= keysList[12], x=categories, y=countryDict[keysList[12]]),
            go.Bar(name= keysList[13], x=categories, y=countryDict[keysList[13]]),
            go.Bar(name= keysList[14], x=categories, y=countryDict[keysList[14]]),
            go.Bar(name=keysList[15], x=categories, y=countryDict[keysList[15]]),
            go.Bar(name=keysList[16], x=categories, y=countryDict[keysList[16]]),
            go.Bar(name= keysList[17], x=categories, y=countryDict[keysList[17]]),
            go.Bar(name= keysList[18], x=categories, y=countryDict[keysList[18]]),
            go.Bar(name= keysList[19], x=categories, y=countryDict[keysList[19]]),
            go.Bar(name= keysList[20], x=categories, y=countryDict[keysList[20]]),
            go.Bar(name= keysList[21], x=categories, y=countryDict[keysList[21]]),
            go.Bar(name= keysList[22], x=categories, y=countryDict[keysList[22]])
            ])

    # Update graph
    fig.update_layout(
        barmode='group', title="Most Popular Category in Each Country", xaxis_title="Countries",
        yaxis_title="Project Count"
    )
    fig.update_xaxes(categoryorder='total ascending')

    # Export graph
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template('analytics.html', graphJSON=graphJSON)
# ----------

@app.route("/success_words")
# Analytic expressing the most common words in successful Kickstarters
# Uses count_words() for data collection, and Counter() for... something
# Incremental
def most_successful_words():
    # I feel this function could certainly benefit from refactoring. Nevertheless, I documented it as-is, with very minor rearrangement.
    # Consider:
    # - Breaking into chunks, as other analytics are?
    # - The *only* line different in if-else branches is COUNTDICT = count_words(data). Replace redundant code with cleaner structure?
    # - If redundant if-else is restructured, graphJSON = "" likely will become irrelevant and can be removed.

    # Import global variables
    global UPDATE_COUNTWORDS
    global COUNTDICT

    # Variable initialization
    list_of_words = []
    list_of_count = []
    graphJSON = ""

    # Incremental: Begin start time
    start_time = time.time()
    
    if(UPDATE_COUNTWORDS == True):
        # Data collection
        COUNTDICT = count_words(DATA) # FIXME: NOT DEFINED

        new_dict = dict(Counter(COUNTDICT).most_common(10)) # FIXME: NOT DEFINED
        UPDATE_COUNTWORDS = False

        # Data processing
        for key, value in new_dict.items():
            list_of_words.append(key)
            list_of_count.append(value)

        # Create graph
        fig = go.Figure(data=[
            go.Bar(x=list_of_words, y=list_of_count)
        ])

        # Format graph
        fig.update_layout( # change the bar mode
            title="Most frequent words in successful projects", xaxis_title="Words",
            yaxis_title="Count"
        )

        # Prepare graph for export
        
        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder) # send json of graph to analytics.html
    else:
        # Data collection
        new_dict = dict(Counter(COUNTDICT).most_common(10)) # FIXME: NOT DEFINED
        UPDATE_COUNTWORDS = False

        # Data processing
        for key, value in new_dict.items():
            list_of_words.append(key)
            list_of_count.append(value)

        # Create graph
        fig = go.Figure(data=[
            go.Bar(x=list_of_words, y=list_of_count)
        ])

        # Format graph
        fig.update_layout(
            title="Most frequent words in successful projects", xaxis_title="Words",
            yaxis_title="Count"
        )

        # Prepare graph for export
        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder) # send json of graph to analytics.html

    # Incremental: Output elapsed time
    print("--- %s seconds ---" % (time.time() - start_time))

    # Export graph
    return render_template('analytics.html', graphJSON=graphJSON)


