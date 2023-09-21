import tkinter as tk
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import requests 
from tkcalendar import Calendar
import calendar
import bcrypt
from tkinter import messagebox
from tkinter import font
from tkinter import ttk
from datetime import datetime
import time
import random
import webbrowser
import csv
#from api_keys import currency_api_key, news_api_key  #Make sure to use your own api_keys. I am using the following APIS: https://www.exchangerate-api.com/ and https://newsapi.org/

#TODO: make a requirements file
 
data = pd.read_csv("Expenses.csv",dtype={'Day': str,'Month':str,'Year':str})

credentials = {"username":'your_desired_username', "password": b'your_hashed_password_from_the_password_hash_file' }

def view_expenses():
    '''This function is called by the view expenses button located in frame 1. 
       It opens a new window and displays the expenses in a table form using ttk.TreeView.
    '''
    toplvl = tk.Toplevel(root)
    toplvl.title("Expenses")
    toplvl.geometry("1000x500")
    toplvl.grid_rowconfigure(0, weight=1)  
    toplvl.grid_columnconfigure(0, weight=1)

    tree = ttk.Treeview(toplvl)
    tree.pack(fill="both", expand=True)

    with open("Expenses.csv", "r") as file:
        csv_reader = csv.reader(file)   #parse the csv file row by row
        header = next(csv_reader)       # get the first row of the csv file which contains the column names
        tree["columns"] = header        # create the columns
        tree.heading("#0", text="Row")  #set the name of the first column which has the row indeces
        for col in header:
            tree.heading(col, text=col)   #set the names of the columns
            tree.column(col, width=100)  # Adjust column width as needed

        #Populate the Treeview with CSV data
        #Fill the table row by row,startin by row number 1 (specified in the enumerate) 
        #An empty string "" is used to specify that the new item should be inserted at the root level of the Treeview. "end" means to append the new row after the last appended row
        for i, row in enumerate(csv_reader, 1):
            tree.insert("", "end", text=str(i), values=row)  
   

def open_link(event):
    '''This function is binded to the link label of frame 5. When the label is pressed the function is callled
       and it opens the link in the default browser.'''
    link = link_label["text"]
    webbrowser.open(link)


def display_next_article():
   ''' This function is used to display the articles returned by the api.'''
   random_article_index = random.randint(0,len(articles_list)-1)
   article = articles_list[random_article_index]
   if article['source'] == "[removed]" or article['source'] == "[Removed]" :
      display_next_article()
   else:
      scource_label.config(text="Source: "+article["source"])
      title_label.config(text=article["title"])
      link_label.config(text=article["link"])

      #Getting the date in the desired format
      date_time = article["date"].split("T")
      date = date_time[0]
      time = date_time[1].replace("Z","")
      date_label.config(text=date+"\n" +time +"(UTC)")
   
      scource_label.grid(row=2,column=0,pady=10)
      title_label.grid(row=3,column=0,columnspan=3,sticky="nswe")
      link_label.grid(row=4,column=0,columnspan=3,sticky="nswe",pady=10)
      date_label.grid(row=2,column=1,pady=10)
      root.after(10000,display_next_article)    #after 10sec the function is called again, to display another article

def show_news(event):
   '''This function is binded to the year and category combobox in frame 5.
      It makes the api request and revieces the desired articles and article informations.'''
   global articles_list
   news_country = country_combobox.get()
   news_category = news_category_combobox.get()
   news_country = countries_dict[news_country]  # we want the iso representation of the country

   news_url = "https://newsapi.org/v2/top-headlines?country="+news_country+"&category="+news_category+"&apiKey="+news_api_key

   response = requests.get(news_url)
   news = response.json()
   articles = news["articles"]   # a list of dicts
   articles_list = [] # a list of the articles, where every article is a dict with the following four key-value pairs
    
   for index, article in enumerate(articles):
       source = articles[index]["source"]["name"]
       title = articles[index]["title"]
       link = articles[index]["url"]
       date = articles[index]["publishedAt"]
       article_with_4_values = {"source":source, "title":title, "link":link, "date":date}
       articles_list.append(article_with_4_values)
    
   
   display_next_article()

   

def convert():
   '''This function is binded to the convert button in frame 3
      and it handles the currency conversion.The api data is updated every 24 hours,
      so there is no reason to make a new request every time a conversion is executed.
      Inaccurate conversions are plausible due to the usage of 24hour old market data
      '''
   conversion_rates_dict = api_data["conversion_rates"]
   type_of_currency = currency_combobox.get()
   try:
    amount_of_currency = float(currency_entry.get())
   except ValueError as error:
    return messagebox.showerror(title="ValueError", message="Please enter a valid number (decimals delimeter must be a '.' Example: '5.4' not '5,4')")  
   type_of_currency_converted = currency_combobox_converted.get()
   if type_of_currency and amount_of_currency and type_of_currency_converted:
    #By default, the api returns the conversion rates of the currencies against the USD,if USD is not the desired currency to be converted 
    #The else clause is executed where the multiplication is a bit more complex due to the fact that we use a 
    #'currency middle man' to determine the converted amount
   
    if type_of_currency == 'USD':
     converted_amount = amount_of_currency * conversion_rates_dict[type_of_currency_converted]
     converted_amount = round(converted_amount,3)
     currency_label_converted.config(text = converted_amount)
    else:
     converted_amount = amount_of_currency * (1/conversion_rates_dict[type_of_currency]) * (conversion_rates_dict[type_of_currency_converted])
     converted_amount = round(converted_amount,3)
     currency_label_converted.config(text = converted_amount)   
    
   else:
      messagebox.showwarning("Warning", "Please fill all required entries")

def update_plot4(event):
    '''This function is used to update the pie chart in frame 4. It is binded to the selections of the month and year combobox's.'''
    data = pd.read_csv("Expenses.csv",dtype={'Day': str,'Month':str,'Year':str})
    selected_month = month_combobox4.get()
    selected_year = year_combobox4.get()
    #Clearing the previous plot
    ax4.cla()

    df_selected = data[(data["Month"]==selected_month) & (data["Year"]==selected_year)]
    y4=df_selected.groupby("Category").sum()["Amount"]
    x4= [x4 for x4, df in df_selected.groupby("Category")]
    fig4.set_facecolor("#2F2D37")
    ax4.set_facecolor("#2F2D37")
    wedges, texts, autotexts =ax4.pie(y4,labels=x4,autopct='%.2f%%', pctdistance=1, labeldistance=1.35,textprops={'fontsize': 8})
    for autotext in autotexts:
     autotext.set_color('white')
    for text in texts:
     text.set_color('white')
    ax4.set_title(f"{selected_month} {selected_year}",color="white",fontsize=10)
    
    
    fig4.tight_layout()
    #Displaying the updated plot into the tkinter window frame
    canvas4.draw()
    total_amount_label4.config(text=f"Total: {y4.sum():.2f}EUR")
    

def update_plot(event):
    ''' This function is used to update the plot in frame 1. It is binded to the the month, year, and plot type combobox's'''
    data = pd.read_csv("Expenses.csv",dtype={'Day': str,'Month':str,'Year':str})
    selected_month = month_combobox.get()
    selected_year = year_combobox.get()
    #Clear the previous plot
    ax.cla()

    df_selected = data[(data["Month"]==selected_month) & (data["Year"]==selected_year)]
    y=df_selected.groupby("Day").sum()["Amount"]
    x= [x for x, df in df_selected.groupby("Day")]
    fig.set_facecolor("#2F2D37")
    ax.set_facecolor("#2F2D37")
    if plot_combobox.get() == "Line Plot":
     ax.plot(x,y,label=f"{selected_month} {selected_year}")
    elif plot_combobox.get() == "Bar Chart":
     ax.bar(x,y,label=f"{selected_month} {selected_year}")   
    ax.set_title("Monthly Expenses",color="white") 
    ax.set_xlabel("Day",fontsize=10)
    ax.set_ylabel("Amount(EUR)",fontsize=10)
    ax.spines['bottom'].set_color('white')
    ax.spines['top'].set_color('white') 
    ax.spines['right'].set_color('white')
    
    ax.spines['left'].set_color('white')
    ax.spines['left'].set_lw(2)
    
    ax.spines['bottom'].set_linewidth(2)
    ax.xaxis.label.set_color('white')
    ax.yaxis.label.set_color('white')
    ax.tick_params(colors='white', which='both') 
     
    if not y.empty:
      ax.set_ylim(0, max(y) + 100)  # Adjust the limits as needed
    fig.tight_layout()
    legend = ax.legend(facecolor="#2F2D37",fontsize="10",loc='upper right')
    title = legend.get_title()
    title.set_color('white') 
    
    #Redraw the updated plot
    canvas.draw()  
    total_amount_label.config(text=f"Total: {y.sum():.2f} EUR")

def submit_expense():
    '''This function is used to submit a new expense. It is binded to the submit expense button in frame 1'''
    global data
    try:
     amount = float(amount_entry.get())
    except ValueError as error:
     return messagebox.showerror(title="ValueError",message="Please insert a valid amount (the decimal delimeter must be a '.' Example: '5.4' not '5,4')")
       
    date = date_entry.get()          # it has been converted into a str
    category = category_combobox.get()  #str
    description = description_entry.get() #str
    if amount and date and category:
      date_splitted= date.split("/")
      day=date_splitted[0]
      month=date_splitted[1]
      year=date_splitted[2]
      month_dict = {"01":"January","02":"February","03":"March","04":"April","05":"May","06":"June","07":"July","08":"August", "09":"September",
                  "10":"October","11":"November","12":"December"
        }
      #Getting the str name month representation from the number representation
      for number_month in month_dict:
          if month == number_month:
              month = month_dict[number_month]

    
      new_entry = {"Amount":amount, "Date":date,"Category":category,"Description":description,"Day":day,"Month":month,"Year":year}
      data = pd.concat([data, pd.DataFrame([new_entry])], ignore_index=True)
      amount_entry.delete('0','end')
      date_entry.config(state='normal')
      date_entry.delete('0','end')
      date_entry.config(state="readonly")
      category_combobox.set('')
      description_entry.delete('0','end')
      data['Day'] = data['Day'].astype(str)
      data['Month'] = data['Month'].astype(str)
      data['Year'] = data['Year'].astype(str)
      data.to_csv('Expenses.csv', index=False)
      messagebox.showinfo("Submition Completed", "Successful submission!")
    
      #Reading the new file in order to be able to obtain information about the new expenses without having to re-open the application
      data = pd.read_csv("Expenses.csv")
    else:
       messagebox.showerror("Submission Error", "Please fill the required amount, date and category data")


    
def submit_date():
    '''This function is used to submit the date chosen from the calendar into the corresponding entry. 
       It is binded to the submit date button.'''
    selected_day = cal.get_date()

    #Stop displaying the calendar
    cal.place_forget()

    close_calendar_button.destroy()
    date_entry.config(state = 'normal',bg="#2F2D37")
    date_entry.delete(0,"end")
    date_entry.insert(0,str(selected_day))
    date_entry.config(state = 'readonly',bg="#2F2D37")
    
   

def open_calendar(event=None):
    '''This function opens the calendar when the date entry widget is selected'''
    global cal
    global close_calendar_button
    cal = Calendar(frame1, selectmode = "day", date_pattern = "dd/mm/y" )
    cal.place(relx=0.5, rely=0.5, anchor='center')
    close_calendar_button = tk.Button(frame1,text="Submit Date", command=submit_date,bg="#2F2D37",fg="white")
    close_calendar_button.grid(row=5,column=0,padx=(0,100), pady=80)
    

def main_window():
    '''This function creates the main window of the application when the login window is closed, after the user inputs the correct 
       login credentials.'''
    global root
    global frame1,frame2,frame5
    global date_entry,amount_entry,description_entry,category_combobox,submit_expense_button,amount_var,date_var,category_var,selected_month_var,ax,fig,canvas,month_combobox,year_combobox,plot_combobox,total_amount_label,ax4,fig4,canvas4,month_combobox4,year_combobox4,total_amount_label4,currency_entry,currency_combobox,currency_combobox_converted,currency_label_converted,currencies,api_data,country_combobox,news_category_combobox,articles_list,countries_dict,scource_label,link_label,title_label,date_label
    #Creating and configuring the main window
    root = tk.Tk()
    root.title("Expenses Tracker")
    root.geometry("700x770")
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)

    #Creating and placing the main window frames:
  
    frame1 = tk.Frame(root, width=250, height=270,highlightthickness=1,highlightbackground='black',bg="#1F193E")
    frame2 = tk.Frame(root, width=450, height=270,highlightthickness=1,highlightbackground='black',bg="#1F193E")
    frame3 = tk.Frame(root, width=250, height=250,highlightthickness=1,highlightbackground='black',bg="#1F193E")
    frame4 = tk.Frame(root, width=450, height=250,highlightthickness=1,highlightbackground='black',bg="#1F193E")
    frame5 = tk.Frame(root, width=700, height=250,highlightthickness=1,highlightbackground='black',bg="#1F193E")

    frame1.grid(row=0,column=0,sticky="nswe")
    frame2.grid(row=0,column=1,sticky="nswe")
    frame3.grid(row=1,column=0,sticky="nswe")
    frame4.grid(row=1,column=1,sticky="nswe")
    frame5.grid(row=2,column=0,columnspan=2,sticky="nswe")

   
    #Configuring the frames so they do note adjust their dimensions to fit the widgets inside of them
    frames = [frame1,frame2,frame3,frame4,frame5]
    for frame in frames:
        frame.grid_propagate(0)
        

    #FRAME1 widgets:
    new_entry_label = tk.Label(frame1, text="Enter a new expense", font=font.Font(weight="bold"),bg="#069EF0",fg="white")
    amount_label = tk.Label(frame1, text="Amount(EUR):",width=11,bg="#2F2D37",fg="white")
    date_label = tk.Label(frame1, text="Date:",width=11,bg="#2F2D37",fg="white")
    category_label = tk.Label(frame1, text="Category:",width=11,bg="#2F2D37",fg="white")
    description_label = tk.Label(frame1, text="Description:",width=11,bg="#2F2D37",fg="white")

    new_entry_label.grid(row=0,column=0,sticky="nsw",pady=(10,5),columnspan=2,padx=10)
    amount_label.grid(row=1,column=0,sticky="nsw",pady=(0,3),padx=10)
    date_label.grid(row=2,column=0,sticky="nsw",pady=(0,3),padx=10)
    category_label.grid(row=3,column=0,sticky="nsw",pady=(0,3),padx=10)
    description_label.grid(row=4,column=0,sticky="nsw",pady=(0,3),padx=10)

    amount_var = tk.StringVar()
    amount_entry = tk.Entry(frame1,width=20, textvariable=amount_var,bg="#2F2D37",fg="white")
    amount_entry.grid(row=1, column=1)

    description_entry = tk.Entry(frame1,width=20,bg="#2F2D37",fg="white")
    description_entry.grid(row=4,column=1)

    date_var = tk.StringVar()
    date_entry = tk.Entry(frame1,width=20,textvariable=date_var,bg="#2F2D37")
    date_entry.grid(row=2,column=1)
    date_entry.bind("<Button-1>", open_calendar)

    categories=["Entertainment", "Housing", "Transportation", "Health care","Utilities","Travel Expenses","Groceries","Education","Personal Care", "Insurance"]
    categories.sort()
    category_var = tk.StringVar(value=categories[0])  # Set the default selected option

    category_combobox = ttk.Combobox(frame1, textvariable=category_var, values=categories,width=17,state="readonly")
    category_combobox.grid(row=3, column=1)

    submit_expense_button = tk.Button(frame1, text="Submit Expense",command=submit_expense,bg="#2F2D37",fg="red")
    submit_expense_button.grid(row=5,column=0,columnspan=2,padx=(0,0),pady=(30,0))  

    view_expenses_button = tk.Button(frame1, text="View Expenses",command=view_expenses,bg="#2F2D37",fg="white")
    view_expenses_button.grid(row=6,column=0,columnspan=2,padx=(0,0),pady=(20,0))  
    
    #Frame 2 - MONTHLY EXPENSES PLOT
      
    current_month = datetime.now().strftime("%B")     #returns the current month
    current_year =datetime.now().year                 #returns the current year
    years_list = [year for year in range(2020,current_year+1,1)]
    month_names = list(calendar.month_name[1:])
    
    
    #Month Combobox:
    selected_month_var = tk.StringVar()
    month_combobox = ttk.Combobox(frame2, textvariable=selected_month_var, values=month_names,state='readonly',width=13)
    month_combobox.set(current_month)
    month_combobox.grid(row=0,column=0,padx=(20,0),pady=8)
    month_combobox.bind("<<ComboboxSelected>>", update_plot)

    #Year Combobox:
    selected_year_var = tk.IntVar()
    year_combobox = ttk.Combobox(frame2, textvariable=selected_year_var, values=years_list,state='readonly',width=13)
    year_combobox.set(current_year)
    year_combobox.grid(row=0,column=1,padx=20,pady=8)
    year_combobox.bind("<<ComboboxSelected>>", update_plot)   

    #Plot Combobox:
    selected_plot_var = tk.StringVar()
    plot_combobox = ttk.Combobox(frame2, textvariable=selected_plot_var, values=["Line Plot","Bar Chart"],state='readonly',width=13)
    plot_combobox.set("Line Plot")
    plot_combobox.grid(row=0,column=2,padx=(0,0),pady=8)
    plot_combobox.bind("<<ComboboxSelected>>", update_plot)  

    #Creating the default plot in frame 2. The plot updates everytime a frame 2 combobox choice is selected
    fig, ax = plt.subplots()
    fig.set_size_inches(4,2)

    # Seting ther color of the axes and the figure
    fig.set_facecolor("#2F2D37")
    ax.set_facecolor("#2F2D37")

    #Seting the colors and the line widths of the axis's
    ax.spines['bottom'].set_color('white')
    ax.spines['top'].set_color('white') 
    ax.spines['right'].set_color('white')
    
    ax.spines['left'].set_color('white')
    ax.spines['left'].set_lw(2)
    
    ax.spines['bottom'].set_linewidth(2)

    #Seting the color of the axis labels and the color of the ticks
    ax.xaxis.label.set_color('white')
    ax.yaxis.label.set_color('white')
    ax.tick_params(colors='white', which='both') 

    #Ploting the data(The monthly expenses)
    df_default_month_and_year = data[(data["Month"]==current_month) & (data["Year"]==current_year)]
    y=df_default_month_and_year.groupby("Day").sum()["Amount"]
    total_amount = y.sum()
    x= [x for x, df in df_default_month_and_year.groupby("Day")]
    ax.plot(x,y,label=f"{current_month} {current_year}")
  
    ax.set_title("Monthly Expenses",color="white")
    ax.set_xlabel("Day",fontsize=10)
    ax.set_ylabel("Amount(EUR)",fontsize=10)
    try:
     ax.set_yticks([ tick for tick in range(0,int(max(y)),100)])
    except ValueError as error:
        pass
    
    #adjusting the figure size to fit the frame space
    fig.tight_layout()
    legend = ax.legend(facecolor="#2F2D37",fontsize="10",loc='upper right')
   
    # Create a FigureCanvasTkAgg widget in order to be able to put the matplotlib plot in the tkinter window
    canvas = FigureCanvasTkAgg(fig, master=frame2)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.grid(row=1,column=0,padx=(25,0),pady=(8,10),columnspan=3)

    #Creating and placing the total amount label
    total_amount_label = tk.Label(frame2,text=f"Total: {total_amount:.2f}EUR",bg="#2F2D37",fg='white')
    total_amount_label.place(relx=0.18, rely=0.22, anchor="center")

    #Frame 4 - PIE PLOT OF THE CATEGORIES

    #Month Combobox:
    selected_month_var4 = tk.StringVar()
    month_combobox4 = ttk.Combobox(frame4, textvariable=selected_month_var4, values=month_names,state='readonly',width=13)
    month_combobox4.set(current_month)
    month_combobox4.grid(row=0,column=0,padx=(20,0),pady=8)
    month_combobox4.bind("<<ComboboxSelected>>", update_plot4)

    #Year Combobox:
    selected_year_var4 = tk.IntVar()
    year_combobox4 = ttk.Combobox(frame4, textvariable=selected_year_var4, values=years_list,state='readonly',width=13)
    year_combobox4.set(current_year)
    year_combobox4.grid(row=0,column=1,padx=20,pady=8)
    year_combobox4.bind("<<ComboboxSelected>>", update_plot4) 

    #Creating the plot
    fig4, ax4 = plt.subplots()
    fig4.set_size_inches(4,2)
  
    #Seting fig and ax colors
    fig4.set_facecolor("#2F2D37")
    ax4.set_facecolor("#2F2D37")

    #Ploting the data
    y4=df_default_month_and_year.groupby("Category").sum()["Amount"]
    total_amount4=y4.sum()
    x4= [x4 for x4, df in df_default_month_and_year.groupby("Category")]
    wedges, texts, autotexts =ax4.pie(y4,labels=x4,autopct='%.2f%%', pctdistance=2.5, labeldistance=1.25)  #texts are the strs for the categories, and autotext are the strs for the percentages
    for autotext in autotexts:
     autotext.set_color('white')
    for text in texts:
     text.set_color('white')
    ax4.set_title(f"{current_month} {current_year}",color="white",fontsize=10)
    
    # Create a FigureCanvasTkAgg widget to display the plot in the tkinter window
    canvas4 = FigureCanvasTkAgg(fig4, master=frame4)
    canvas_widget4 = canvas4.get_tk_widget()
    canvas_widget4.grid(row=1,column=0,padx=(25,0),pady=(6,15),columnspan=3)

    #Creating and placing the total amount label
    total_amount_label4 = tk.Label(frame4,text=f"Total: {total_amount4:.2f}EUR",bg="#2F2D37",fg='white')
    total_amount_label4.place(relx=0.18, rely=0.22, anchor="center")

    #FRAME 3 - CURRENCY CONVERTER

    #Making the request
    url = "https://v6.exchangerate-api.com/v6/"+currency_api_key+"/latest/USD"  
    response = requests.get(url)
    api_data = response.json()
    currencies=[]
    for currency in api_data["conversion_rates"]:
     currencies.append(currency)

    # Creating and placing the widgets
    converter_label = tk.Label(frame3, text="Currency Converter",bg="#069EF0",fg="white",font=font.Font(weight="bold"))
    converter_label.grid(row=0,column=0,columnspan=2,sticky="nswe",pady=(10,5),padx=(10,65))

    currency_combobox = ttk.Combobox(frame3,values=currencies,width=6,state="readonly")
    currency_combobox.grid(row=1,column=0,padx=(8,10),pady=40)

    currency_combobox_converted = ttk.Combobox(frame3,values=currencies,width=6,state="readonly")
    currency_combobox_converted.grid(row=3,column=0,padx=(8,10),pady=20)

    currency_entry = tk.Entry(frame3,bg="#2F2D37",fg="white",width=10)
    currency_entry.grid(row=1,column=1,padx=(10,100),pady=40)

    currency_label_converted = tk.Label(frame3,bg="#2F2D37",fg="white",width=8)
    currency_label_converted.grid(row=3,column=1,padx=(10,100),pady=20)

    convert_button = tk.Button(frame3,text="Convert",bg="#2F2D37",fg="red",width=14,command=convert)
    convert_button.grid(row=2,column=0,padx=(30,130),pady=(0,10),columnspan=2)

#FRAME 5 - NEWS HEADLINES
    # the values in the dict are the iso representations which are used in the api
    countries_dict = {"United Arab Emirates":"ae","Argentina":"ar","Austria":"at","Australia":"au","Belgium":"be","Bulgaria":"bg","Brazil":"br","Canada":"ca","Switzerland":"ch","China":"cn",
                 "Colombia":"co","Cuba":"cu","Czechia":"cz","Germany":"de","Egypt":"eg","France":"fr","United Kingdom":"gb","Greece":"gr","Hong Kong":"hk","Hungary":"hu","Indonesia":"id",
                 "Irland":"ie","Israel":"il","India":"in","Italy":"it","Japan":"jp","Korea":"kr","Lithuania":"lt","Latvia":"lv","Morocco":"ma","Malaysia":"my","Mexico":"mx","Nigeria":"ng","Netherlands":"nl",
                 "Norway":"no","New Zealand":"nz","Philippines":"ph","Poland":"pl","Portugal":"pt","Romania":"ro","Serbia":"rs","Russia":"ru","Saudi Arabia":"sa","Sweden":"se","Singapore":"sg","Slovenia":"si",
                 "Slovakia":"sk","Thailand":"th","Turkey":"tr","Taiwan":"tw","Ukraine":"ua","United States of America":"us","Venezuela":"ve","South Africa":"za"}
    
    countries_names = [country for country in countries_dict]
    
    news_categories = ['business','entertainment','general','health','science','sports','technology']
    
    #the default country is greece and the default category of news is business news

    news_url = "https://newsapi.org/v2/top-headlines?country="+"gr"+"&category="+"business"+"&apiKey="+news_api_key
 
    # Creating and placing the widgets
    country_combobox = ttk.Combobox(frame5,values=countries_names,state='readonly')
    news_category_combobox = ttk.Combobox(frame5,values=news_categories,state='readonly')

    news_label = tk.Label(frame5, text="Top News by Country and Category",bg="#069EF0",fg="white",font=font.Font(weight="bold"))

    country_combobox.grid(row=1, column=0,padx=(20,5),pady=(10,0))
    news_category_combobox.grid(row=1, column=1,padx=5,pady=(10,0))
    news_label.grid(row=0,column=0,columnspan=3,padx=10,sticky="nw",pady=10)

    country_combobox.set("Greece")
    news_category_combobox.set("business")

    #Making the request
    response = requests.get(news_url)
    news = response.json()
    articles = news["articles"]   # a list of dicts
    articles_list = [] # a list of the articles, where every article is a dict with the following four key-value pairs

    scource_label = tk.Label(frame5,bg="#2F2D37",fg="white")
    title_label = tk.Label(frame5,wraplength=600,bg="#2F2D37",fg="white")
    link_label = tk.Label(frame5,wraplength=600,bg="#2F2D37",fg="#84BCFF")
    date_label = tk.Label(frame5,bg="#2F2D37",fg="white")

    #From every article returned we only keep the source,title,link and date
    for index, article in enumerate(articles):
       source = articles[index]["source"]["name"]
       title = articles[index]["title"]
       link = articles[index]["url"]
       date = articles[index]["publishedAt"]
       article_with_4_values = {"source":source, "title":title, "link":link, "date":date}
       articles_list.append(article_with_4_values)
    
    #Displaying the articles
    display_next_article()

    country_combobox.bind("<<ComboboxSelected>>", show_news)
    news_category_combobox.bind("<<ComboboxSelected>>", show_news)
    link_label.bind("<Button-1>", open_link)

       
    
def login(event=None):
    username = username_entry.get()
    password = password_entry.get()
    #Validating the credentials
    if username in credentials:
        hashed_password = credentials["password"]
        if bcrypt.checkpw(password.encode('utf-8'), hashed_password):
            main_window()
            login_window.destroy()
        else:
             messagebox.showerror("Authentication Failed", "Invalid username or password")

    else:
         messagebox.showerror("Authentication Failed", "Invalid username or password")

#Login Window
login_window = tk.Tk()
login_window.geometry("200x300")
login_window.title("Login")

#Creation and placement of login window widgets
username_entry = tk.Entry(login_window)
username_entry.grid(row=0,column=1, pady=(60,0))
password_entry = tk.Entry(login_window,show='*')
password_entry.grid(row=1, column=1, pady=(20,5))

username_label = tk.Label(login_window, text="Username:")
username_label.grid(row=0,column=0,  pady=(60,0))
password_label = tk.Label(login_window, text="Password:")
password_label.grid(row=1, column=0, pady=(20,5))

login_button = tk.Button(login_window, text="Login",command=login)
login_button.grid(row=2 ,column=0,columnspan=2, sticky="nswe", pady=10,padx=(10,0))


#Binding the "ENTER" KEY to the password_entry and to the username_entry so we can click enter and use the submit button when clicked both on the password entry and the username entry
password_entry.bind("<Return>", login)
username_entry.bind("<Return>", login)


login_window.mainloop()
try:
 root.mainloop()
except NameError as error:
    pass