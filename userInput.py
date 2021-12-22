# This is the file to make forms. Forms organized collections of user data.
# a good example of a form is registration. A registration form will accept 
#   and check a username and password.

#The information collected on a form will be added to a database


class exampleForm:#very basic form. It does not error check.
    def __init__(self, passedName):
        self.nm = passedName


class kickStarterForm:
    
    def empty_error(self):
        if self.id == "":
            return "error: empty id"
        if self.name == "":
            return "error: empty name"
        if self.category == "":
            return "error: empty category"
        if self.main_category == "":
            return "error: empty main_category"
        if self.currency == "":
            return "error: empty currency"
        if self.deadline == "":
            return "error: empty deadline"
        if self.goal == "":
            return "error: empty goal"
        if self.date_launched == "":
            return "error: empty date_launched"
        if self.number_pledged == "":
            return "error: empty number_pledged"
        if self.state == "":
            return "error: empty state"
        if self.number_backers == "":
            return "error: empty number_backers"
        if self.country == "":
            return "error: empty country"
        if self.amount_usd_pledged == "":
            return "error: empty amount_usd_pledged"
        if self.amount_usd_pledged_real == "":
            return "error: empty amount of real usd pledged"
        return "passed"

    def errorRunner(self):
        errorList = list()#create an instant of the errorList to pass back
        currentError = ""#use it to track the current error
        currentError = self.empty_error()
        if currentError != "passed": #if an error does not return "passed" we append it to the list.
            errorList.append(currentError)
        return errorList
        #other errors are placed below here to be ran on form init





    def __init__(self,id,name,category,main_category,currency,deadline,goal,date_launched,time_launched,number_pledged,state,number_backers,country,amount_usd_pledged,amount_usd_pledged_real):
        self.id = str(id) #print
        self.name = str(name) #print
        self.category = str(category) #print
        self.main_category = str(main_category) #print
        self.currency = str(currency) #the type of currency
        self.deadline = str(deadline)
        self.goal = str(goal)
        self.date_launched = str(date_launched + " " + time_launched)
        self.number_pledged = str(number_pledged) #the number of times someone has pledged
        self.state = str(state)
        self.number_backers = str(number_backers)
        self.country = str(country)
        self.amount_usd_pledged = str(amount_usd_pledged)# the actual cash
        self.amount_usd_pledged_real = str(amount_usd_pledged_real)
        self.error_msgs = self.errorRunner()#if error_msg is not equal to "passed" then an error occured



    
