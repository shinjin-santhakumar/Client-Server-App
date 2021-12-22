# cs180project-022-the-jarss
cs180project-022-the-jarrs created by GitHub Classroom

# Libraries:
1. Github
    - Open empty folder
    - Install github with `sudo apt install git`
    - Install git LFS with `sudo apt-get install git-lfs` and `git-lfs install`
    - Run `git clone --recursive https://github.com/ucr-cs180-fall21/cs180project-022-the-jarss.git` in the terminal
    - cd into repository

2. Flask
    - Reference: https://flask.palletsprojects.com/en/2.0.x/quickstart/
    - How to install Flask on terminal:
        - `sudo apt install python3-pip`
        - `python3 -m pip install --upgrade pip`
        - `pip install -U Flask`

3. Plotly
    - `pip install plotly==5.4.0`


# Running the Website
  - Ensure Flask version 2.x.x and plotly are installed
    - Use `flask --version` 
    - Expected output:
        ```
        Python 3.8.5
        Flask 2.0.2
        Werkzeug 2.0.2
        ```
    - Run `import plotly` in interactive shell
  - Expected output: (no output)
  - Run one of the following in the terminal
    - Powershell terminals: `$env:FLASK_APP = "app_interface.py”`
    - Bash terminals: `export FLASK_APP=app_interface.py`
    - CMD terminals: `set FLASK_APP=app_interface.py`
  - Then run `flask run`
  - Open the resulting localhost website by copying printed IP address into your browser

# Using the Website
1. Features
  - Ability to import a kickstarter dataset
  - Ability to backup the current modified dataset. 
  - Search by ID, Month, Name, State, or Category 
  - Ability to add an item 
  - Ability to delete an item
  - Ability to edit an item 

2. Analytics provided
  - Average length of a kickstarter
  - Category most likely to fail
  - Most funded Category
  - Most popular Month to Start a Kickstarter
  - Most Popular Category Each Month
  - Most Ambitious Project Each Month
  - Most Popular Category Each Country
  - Recurring words in successful Kickstarter campaigns

# High-Level-Guide
1. App_interface.py
  - Uses Flask to route User to different webpages
  - Imports analytic_functions.py for function calls


2. Analytic_functions.py
  - Contains the function calls used in app_interface.py for incremental analytics
3. Static
  - Contains the CSS and images assets for the pages of our website, as well as the working copy of the database
4. Add_function.py 
  - Contains the function that converts and appends a python dictionary into a json file
5. Backup Folder
  - Contains a backup of the original csv database converted to json.
6. Parser
  - Contains the csv to json parser that is written in C++.
7. Templates
  - Contains the HTML files that display the website
8. Test_interface.py
  - Contains the units for our analytical functions 
9. Sprint Folders 1-7
  - Each folder contains demos and artifacts for each sprint meeting.
10. UserInput.py
  - Contains a function that checks null inputs for the the add component of the update feature

# Testing
 1. Our project features continuous integration and unit testing
 2. In order use our unit tests run: `python test_interface.py`
 3. Tests are passed if no errors are returned.
