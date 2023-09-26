# ExpensesTracker
This repository contains the Expenses Tracker app.

## The expenses tracker app is built upon a tkinter GUI and enables the users to add and manage their expenses. In more detail, the users can make use of the following functionalities.

1) The user can input a new expense by providing the amount, the date, and the category of the expense (required fields) and the optional description of it.
2) The data is stored in a .csv file which is indirectly accessible to the user through the app.
3) Through the various data visualization tools available in the app, the users can visualize and keep track of their spending habits.
   a) The monthly expenses can be line plotted or presented in a bar chart by selecting the desired month and year.
   b) There is also a pie plot representation of the categorical spending.
4) A currency converter tool powered by an exchange rates API providing forex rates for 161 currencies is also available.
5) Users have access through the app to news headlines provided by a news API. They can choose the type of articles from the desired country of origin that they want
   to be displayed in the corresponding window frame.
6) Given the sensitive and private nature of the economic data password protection is provided.

## NOTES:
1) In the password hash.py file you can choose your desired password and then proceed to encrypting it, the encrypted password should   be passed in the 'your_hashed_password_from_the_password_hash_file' placeholder inside the 'credentials' dictionary variable located in line 23 of main.py. Also, make sure to insert your desired username inside the placeholder value of the "username" key of the same dictionary.  
2) The APIS used are https://www.exchangerate-api.com/ and https://newsapi.org/. Create a free account and get the api keys.Then place the api keys in the corresponding variables: currency_api_key, news_api_key. In line 17 in main.py I import them from another file but that wont be needed for your case. It is a good practice in order to keep the api keys private when sharing your code.

![expense_tracker_img1](https://github.com/AthanasiosKwn/ExpensesTracker/assets/143710534/a1c5fab7-71f2-4665-810f-2f915b7ef4ff)


![expenses_tracker_img2](https://github.com/AthanasiosKwn/ExpensesTracker/assets/143710534/8982fd71-7a61-4d2c-9bcc-ff2fa7eed7a4)



