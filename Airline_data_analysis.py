#!/usr/bin/env python
# coding: utf-8

# In[46]:


import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')


# # Database Connection

# In[2]:


connection = sqlite3.connect('travel.sqlite')
cursor = connection.cursor()#to execute query


# In[3]:


cursor.execute("""select name from sqlite_master where type = 'table';""")
print('List of tables present in the data base')
table_list = [table[0] for table in cursor.fetchall()]
table_list


# # Data Exploration

# In[4]:


aircrafts_data =  pd.read_sql_query("select * from aircrafts_data", connection)
aircrafts_data.head()


# In[5]:


aircrafts_data.shape


# In[6]:


aircrafts_data


# In[7]:


airports_data =  pd.read_sql_query("select * from airports_data", connection)
airports_data


# In[8]:


boarding_passes =  pd.read_sql_query("select * from boarding_passes", connection)
boarding_passes


# In[9]:


bookings =  pd.read_sql_query("select * from bookings", connection)
bookings


# In[10]:


flights =  pd.read_sql_query("select * from flights", connection)
flights


# In[11]:


seats =  pd.read_sql_query("select * from seats", connection)
seats


# In[12]:


ticket_flights =  pd.read_sql_query("select * from ticket_flights", connection)
ticket_flights


# In[13]:


tickets =  pd.read_sql_query("select * from tickets", connection)
tickets


# In[20]:


for table in table_list:
    print("\ntable: " + table)
    columns_info = connection.execute("PRAGMA table_info({})".format(table))
    for column in columns_info.fetchall():
        print(column[1:3])


# In[21]:


for table in table_list:
    print('\ntable: ', table)
    df_table = pd.read_sql_query(f"select * from {table}", connection)
    print(df_table.isnull().sum())


# # Basic Analysis

# How many planes have more than 100 seats

# In[25]:


pd.read_sql_query("""select aircraft_code, count(*) as num_seats from seats
group by aircraft_code having num_seats >100 """, connection)


# How the number of tickets booked and total amount earned changed with the time

# In[32]:


tickets= pd.read_sql_query("""select * from tickets inner join bookings on tickets.book_ref = bookings.book_ref""", connection)

tickets['book_date'] = pd.to_datetime(tickets['book_date'])
tickets['date']= tickets['book_date'].dt.date
x=tickets.groupby('date')[['date']].count()
plt.figure(figsize = (18,6))
plt.plot(x.index, x['date'], marker = '^')
plt.xlabel('Date', fontsize = 20)
plt.ylabel('Number of Tickets', fontsize=20)
plt.grid('b')
plt.show()


# In[38]:


bookings = pd.read_sql_query("select * from bookings", connection)

bookings['book_date'] = pd.to_datetime(bookings['book_date'])
bookings['date']= bookings['book_date'].dt.date
x=tickets.groupby('date')[['total_amount']].sum()
plt.figure(figsize = (18,6))
plt.plot(x.index, x['total_amount'], marker = '+')
plt.xlabel('Date', fontsize = 20)
plt.ylabel('Total amount earned', fontsize=20)
plt.grid('b')
plt.show()


# Calculate the average charges for each aircraft with different fare conditions

# In[43]:


df = pd.read_sql_query("""select fare_conditions, aircraft_code, avg(amount)
from ticket_flights join flights on
ticket_flights.flight_id= flights.flight_id 
group by aircraft_code, fare_conditions"""
                       , connection)
df


# In[48]:


sns.barplot(data = df, x='aircraft_code', y='avg(amount)', hue='fare_conditions')


# # Analyzing occupancy rate

# For each aircraft, calculate the total revenue per year and the average revenue per ticket

# In[52]:


pd.read_sql_query("""select aircraft_code, ticket_count, total_revenue, total_revenue/ticket_count as avg_revenue_per_ticket from
(select aircraft_code, count(*) as ticket_count, sum(amount) as total_revenue from ticket_flights join
flights on ticket_flights.flight_id= flights.flight_id group by aircraft_code)""", connection)


# Calculate the average occupancy per aircraft

# In[59]:


occupancy_rate = pd.read_sql_query(f"""SELECT a.aircraft_code, AVG(a.seats_count) as booked_seats, b.num_seats, 
AVG(a.seats_count)/b.num_seats as occupancy_rate
                            FROM (
                                SELECT aircraft_code, flights.flight_id, COUNT(*) as seats_count
                                FROM boarding_passes
                                INNER JOIN flights 
                                ON boarding_passes.flight_id=flights.flight_id
                                GROUP BY aircraft_code, flights.flight_id
                                ) as a INNER JOIN
                                (
                                SELECT aircraft_code, COUNT(*) as num_seats FROM seats 
                                GROUP BY aircraft_code  
                                ) as b
                                ON a.aircraft_code = b.aircraft_code
                            GROUP BY a.aircraft_code""", connection)
occupancy_rate


# Calculate by how much the total annual turnover could increase by giving all aircraft a 10% higher occupancy rate

# In[61]:


occupancy_rate['Inc occupancy rate']= occupancy_rate['occupancy_rate']+occupancy_rate['occupancy_rate']*0.1
occupancy_rate


# In[69]:


pd.set_option("display.float_format", str)


# In[70]:


total_revenue = pd.read_sql_query("""select aircraft_code, sum(amount) as total_revenue from ticket_flights
join flights on ticket_flights.flight_id = flights.flight_id group by aircraft_code""", connection
                                 )
occupancy_rate['Inc Total Annual Turnover']=(total_revenue['total_revenue']/occupancy_rate['occupancy_rate'])/occupancy_rate['Inc occupancy rate']
occupancy_rate


# In[ ]:




