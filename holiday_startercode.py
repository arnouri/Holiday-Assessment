# %% [markdown]
# TODO:
# -I'm converting to date so frequently I should honestly just have a function for it 
# -Likewise the submenus are so similar it could just be one function that takes in the user selection and selects from the appropriate txt file
# -Finish input 3 in main and json load
# -Strangely enough no holidays from week 51 of 2022 get returned in displayholiday

# %%
import datetime
import time
import json
import bs4
from bs4 import BeautifulSoup
import requests
from dataclasses import dataclass
from IPython.display import clear_output
bs4.__version__

# %%
#TESTING

# %%
# -------------------------------------------
# Modify the holiday class to 
# 1. Only accept Datetime objects for date.
# 2. You may need to add additional functions
# 3. You may drop the init if you are using @dataclasses
# --------------------------------------------
class Holiday:
      
    def __init__(self,name, date):
        #Your Code Here
        self.name = name
        if type(date) == datetime.datetime:
            self.date = date
        else:
            raise TypeError("Please enter a valid date in the correct format!")

    def __str__ (self):
        # String output
        # Holiday output when printed.
        #output is clunky without a suffix but man that'll be annoying to implement 
        print(f'{self.name} is on {(self.date).strftime("%A")} the {(self.date).strftime("%d")} this year ({(self.date).strftime("%Y")})\n')
         


# %%
        
# -------------------------------------------
# The HolidayList class acts as a wrapper and container
# For the list of holidays
# Each method has pseudo-code instructions
# --------------------------------------------
class HolidayList:
    def __init__(self):
       self.innerHolidays = []
       self.read_json('holidays.json')
       #startup text
       s = open('Startup.txt', 'r')
       for i in s.readlines():
        print(i)
   
    def addHoliday(self, holidayObj):
        # Make sure holidayObj is an Holiday Object by checking the type
        # ok and do what if its not?
        if isinstance(holidayObj, Holiday):
            # Use innerHolidays.append(holidayObj) to add holiday
            if holidayObj not in self.innerHolidays:
                self.innerHolidays.append(holidayObj)
            # print to the user that you added a holiday
            print('Holiday added!')
            time.sleep(2)
        else:
            raise TypeError("Please enter a valid Holiday in the correct format!")
        
    def findHoliday(self, HolidayName, Date):
        # Find Holiday in innerHolidays
        for Holiday in self.innerHolidays:
            if Holiday.name == HolidayName and Holiday.date == Date:
                # Return Holiday
                return Holiday

    def removeHoliday(self, HolidayName, Date):
        # Find Holiday in innerHolidays by searching the name and date combination.
        Holiday = self.findHoliday(HolidayName, Date)
        # remove the Holiday from innerHolidays
        self.innerHolidays.remove(Holiday)
        # inform user you deleted the holiday
        print("Holiday deleted!")
        time.sleep(2)
        

    def read_json(self, filelocation):
        # Read in things from json file location
        f = open(filelocation)
        data = json.load(f)
        for i in data['holidays']:
            date_ = datetime.datetime.strptime(i['date'],'%Y-%m-%d')
            name = i['name']
            day = Holiday(name, date_)
            # Use addHoliday function to add holidays to inner list.
            self.addHoliday(day)
        
    def save_to_json(self, filelocation):
        # Write out json file to selected file.
        f = filelocation
        dict_translate = {"holidays":[{"name": h.name, "date": h.date} for h in self.innerHolidays]}
        with open(f, 'w') as foo:
            json.dump(dict_translate, foo, indent=4, default=str)
        


    def scrapeHolidays(self):
        # pass
        # Scrape Holidays from https://www.timeanddate.com/holidays/us/ 
        link = 'https://www.timeanddate.com/holidays/us/{}'
        # Remember, 2 previous years, current year, and 2  years into the future. You can scrape multiple years by adding year to the timeanddate URL. For example https://www.timeanddate.com/holidays/us/2022
        years = [2020, 2021, 2022, 2023, 2024]
        errors = []
        ids = []
        for i in years:
            response = requests.get(link.format(i))
            soup = BeautifulSoup(response.text, 'html.parser')
            table = soup.find('table', attrs={'id':"holidays-table"})
            body = table.find('tbody')
            rows = body.find_all('tr')
            

            for row in rows:
                tag = row.attrs
                id = tag['id']
                #to store empty rows for no errors
                ids.append(id)
                ids[:] = [id for id in ids if not id.lstrip('tr').isdigit()]
                if id not in ids:
                    try: 
                        date = row.find('th', attrs={'class':'nw'}).get_text()
                        str_ = date
                        str_ = str_ + str(i)
                        x = datetime.datetime.strptime(str_.replace(' ', ''), '%b%d%Y')
                        sub = row.find_all('td')
                        name = sub[1].get_text()
                        day = Holiday(name, x)
                        # Check to see if name and date of holiday is in innerHolidays array
                        # Add non-duplicates to innerHolidays
                        #^ handled in addHoliday 
                        #self.addHoliday(day)
                        if day not in self.innerHolidays:
                            self.innerHolidays.append(day)
                    # Handle any exceptions.
                    except Exception as e:
                        errors.append(str(e))
        errors = set(errors)     
        if len(errors) > 0:
            print(errors)
            
    def numHolidays(self):
        # Return the total number of holidays in innerHolidays
        return len(self.innerHolidays)

    def filter_holidays_by_week(self, year, week_number):
        # Use a Lambda function to filter by week number and save this as holidays, use the filter on innerHolidays
        Holidays = filter(lambda x: x if int(x.date.strftime('%V')) == week_number and int(x.date.strftime('%Y')) == year else None, self.innerHolidays)
        # Week number is part of the the Datetime object
        # Cast filter results as list
        Holidays = list(Holidays)

        # print(self.innerHolidays[0].name)
        # print(Holidays)
        # # return your holidays
        return Holidays

    #removed parameter from this funtion 
    def displayHolidaysInWeek(self):
        # Use your filter_holidays_by_week to get list of holidays within a week as a parameter
        year = input("Which year would you like to search? (leave blank for current year): ")
        week = input("Which week would you like to view? #[1-52, Leave blank for the current week]: ")
        if week == "" and year != "": 
            _, week = self.viewCurrentWeek()
        elif year == "" and week != "":
            year, _ = self.viewCurrentWeek()
        elif week == "" and year == "":
            year, week = self.viewCurrentWeek()
        filtered = self.filter_holidays_by_week(int(year), int(week))
        # Output formated holidays in the week.
        # print(type(week))
        # print(type(year))
        # print(type(filtered))
        print(f"These are the {len(filtered)} Holidays in week {week} of {year}\n")
        for Holiday in filtered:
            Holiday.__str__()
        # * Remember to use the holiday __str__ method.
        
    
    #stretch goal
    # def getWeather(weekNum):
    #     # Convert weekNum to range between two days
    #     # Use Try / Except to catch problems
    #     # Query API for weather in that week range
    #     # Format weather information and return weather string.
    #     pass

    def viewCurrentWeek(self):
        # Use the Datetime Module to look up current week and year
        week = datetime.datetime.now().strftime('%V')
        year = datetime.datetime.now().strftime('%Y')

        return year, week
        # Use your filter_holidays_by_week function to get the list of holidays
        # for the current week/year
        # Use your displayHolidaysInWeek function to display the holidays in the week

        # Ask user if they want to get the weather
        # If yes, use your getWeather function and display results
        



# %%
def menu():
    clear_output(wait=True)
    f = open('Holiday_Menu.txt', 'r')
    for i in f.readlines():
        print(i, flush = True)


# %%
def submenu_add():
    clear_output(wait=True)
    f = open('submenu_add.txt', 'r')
    for i in f.readlines():
        print(i)

# %%
def submenu_remove():
    clear_output(wait=True)
    f = open('submenu_remove.txt', 'r')
    for i in f.readlines():
        print(i)

# %%
def submenu_save():
    clear_output(wait=True)
    f = open('submenu_save.txt', 'r')
    for i in f.readlines():
        print(i)

# %%
def submenu_view():
    clear_output(wait=True)
    f = open('submenu_view.txt', 'r')
    for i in f.readlines():
        print(i)

# %%
def submenu_exit():
    clear_output(wait=True)
    f = open('submenu_exit.txt', 'r')
    for i in f.readlines():
        print(i)

# %%
#REARRANGE IN AN ORDER THAT MAKES SENSE

def main():
    # Large Pseudo Code steps
    # -------------------------------------
    
    # 1. Initialize HolidayList Object
    myList = HolidayList()
    # 2. Load JSON file via HolidayList read_json function
    # ^ taken care of in the init 

    # 3. Scrape additional holidays using your HolidayList scrapeHolidays function.
    myList.scrapeHolidays()
    # 3. Create while loop for user to keep adding or working with the Calender
    time.sleep(2)
    input_ = ''
    while input_ != 'q':
        # 4. Display User Menu (Print the menu)
        menu()
        # 5. Take user input for their action based on Menu and check the user input for errors
        input_ = input("Select a menu option by entering a number: ")
        #add holiday
        if input_ == '1':
            submenu_add()
            Holiday_ = input("What Holiday would you like to add?: ")
            print(f'Holiday: {Holiday_}')
            date_ = input("Please enter the date in the YYYY-MM-DD format: ")
            print(f'Date: {date_}')
            try:
                date_ = datetime.datetime.strptime(date_, '%Y-%m-%d')
            except:
                clear_output(wait=True)
                print("Error! Invalid date! Returning to main menu...")
                time.sleep(5)
                continue
            try:
                day = Holiday(Holiday_, date_)
                myList.addHoliday(day)
            #not sure if this exception will ever be needed but hey, why not huh?
            except Exception as e:
                print(e)
                time.sleep(5)
                continue
        
        #remove holiday
        elif input_ == '2':
            submenu_remove()
            Holiday_ = input("What Holiday would you like to remove?: ")
            print(f'Holiday: {Holiday_}')
            date_ = input("Please enter the date in the YYYY-MM-DD format: ")
            print(f'Date: {date_}')
            try:
                date_ = datetime.datetime.strptime(date_, '%Y-%m-%d')
            except:
                clear_output(wait=True)
                print("Error! Invalid date! Returning to main menu...")
                time.sleep(5)
                continue
            myList.removeHoliday(Holiday_, date_)
    
        #Save Holiday List
        elif input_ == '3':
            submenu_save()
            input_ = input('Are you sure you want to save your changes? [y/n]: ')
            if input_.lower() == 'y':
                try:
                    loc = 'SavedHolidays.json'
                    myList.save_to_json(loc)
                    print("Success! Changes saved.")
                    time.sleep(2)
                except Exception as e:
                    print(f"Failure\n The Following error occurred: {e}")
                    time.sleep(5)

            elif input_.lower() == 'n':
                clear_output(wait=True)
                print("Returning to main menu...")
                time.sleep(5)
                continue
            else:
                clear_output(wait=True)
                print("Not a valid input! Returning to main menu...")
                time.sleep(5)
                continue
        
        #View Holiday List
        elif input_ == '4':
            submenu_view()
            myList.displayHolidaysInWeek()
            #how to linger here until button press?
            while input_.lower() != 'b':
                input_ = input("Press [B] to return to the main menu: ")
            continue

        #Exit
        elif input_ == '5':
            submenu_exit()
            input_ = input("Are you sure you wish to exit? [Y/N]: ")
            if input_.lower() == 'y':
                print("Goodbye!")
                input_ = 'q'
                continue 
            elif input_.lower() == 'n':
                clear_output(wait=True)
                print("Returning to main menu...")
                time.sleep(5)
                continue
            else:
                clear_output(wait=True)
                print("Not a valid input! Returning to main menu...")
                time.sleep(5)
                continue

        else:
            clear_output(wait=True)
            print("Invalid input!")
            time.sleep(2)
    # 6. Run appropriate method from the HolidayList object depending on what the user input is
    # 7. Ask the User if they would like to Continue, if not, end the while loop, ending the program.  If they do wish to continue, keep the program going. 
    


# %%

if __name__ == "__main__":
    main();

# Additional Hints:
# ---------------------------------------------
# You may need additional helper functions both in and out of the classes, add functions as you need to.
#
# No one function should be more then 50 lines of code, if you need more then 50 lines of code
# excluding comments, break the function into multiple functions.
#
# You can store your raw menu text, and other blocks of texts as raw text files 
# and use placeholder values with the format option.
# Example:
# In the file test.txt is "My name is {fname}, I'm {age}"
# Then you later can read the file into a string "filetxt"
# and substitute the placeholders 
# for example: filetxt.format(fname = "John", age = 36)
# This will make your code far more readable, by seperating text from code.


