# Two Six Capital Data Engineering Challenge

## Problem Statement

This data engineering challenge reflects the kind of tasks we undertake when working on private equity deals. A Data Engineer is someone who has specialized their skills in creating software solutions around big data. This means that the Data Engineer must be capable of adapting to many situations and working with a vast panoply of tools. 

The challenge is split into two parts.  

**First**, setup a REST API that is accessible from the web in order to compute metrics against a given the dataset. The data received should be cleaned, processed, and stored in a SQL database that feeds the REST API.  

**Second,** answer a few short follow-up technical questions.  

## REST API Development

### Objective

Develop a globally accessible REST API that could connect to a database and respond to the specific queries based on following metrics evaluation:

1. `Revenue`
2. `Active User Count` - Number of users who have made at least one transaction in the given year.
3. `New User Count` - Number of users who have joined in a the given year
4. `Average Revenue per Active User` - Revenue / Active User Count

### Given Data

Each CSV file has the following columns:  

- `transaction_date`  – date when transaction was made
- `user`  – unique customer identifier
	 `amount` 	– gross revenue, i.e., how much a customer spent
- `join_date` – date of a customer’s first purchase
- `region` – geographical region where the transaction was made

### Database Configuration

There were many options to connect a SQL database. Some of them that I was considering while writing API were MYSQL, POSTGRES, PANDAS(python) and SQLITE (flask). Due to the size of the dataset provided, I opted for PANDAS dataframes to query directly from the csv file. This is method uses servers RAM so the operation is quicker. But the trade off is that PANDAS can lead to memory overflow. Hence, this is not a scalable option but it definitely gives relatively quick response time for smaller API's. 

The idea here was to create an instance wise query based on class (DB) while REST API is live. The overall implementation is present in the file - `utils/db_tools.py`

### Preprocessing Data

#### Cleaning Data

The provided data has 4 files corresponding to year-wise transactions from 2013 to 2016. The files have two major issues : One of the files is comma separated and the rest were tab separated. The other issue was that the one of the file have additional delimiters in between. 

To handle the first issue, following python script is used to convert from one delimited type to another delimited type file (the script is available @ utils/tabconvert_script.py)

```python
#!/usr/bin/env python
import sys,csv
for row in csv.reader(sys.stdin):
  print "\t".join(row)
```

The other issue was also critical to handle because inconsistent rows in a data file would cause runtime issues during database configuring. This issue was handled by manual cleaning as this was across few rows. 

Additionally, fields name are inconsistent across the data files. This issue got resolved in processing step.

#### Processing Data

 Fields like `joining date` and `transaction date`was formatted differently than usual. Hence, I used standard `datetime`format (it is also supported in pandas dataframe). Additionally, I created few more sub fields like `year`, `month`and `day` from transaction and joining field. Below is the snippet of one of such example (for detailed implementation, refer utils/db_tools.py)

```python
temp = df['transaction date'].str.split('/', expand=True)
temp[0] = temp[0].map(month)
temp[3] = pd.to_datetime(temp[1] + '-' + temp[0] + '-' + temp[2])
temp[0] = pd.to_numeric(temp[0])
temp[1] = pd.to_numeric(temp[1])
temp[2] = pd.to_numeric(temp[2])
df['transaction_date_datetime'] = temp[3]
df['transaction_date_date'] = temp[1]
df['transaction_date_month'] = temp[0]
df['transaction_date_year'] = temp[2]
df = df.drop(columns=['transaction date'])
```

Apart from this, I also used numeric data types for fields like `user` and `sales amount`which were originally strings (as per pandas read function).  The snippet is shown below:

```python
df['user'] = pd.to_numeric(df['user'])
df['sales_amount'] = pd.to_numeric(df['sales_amount']) 
```

Lastly, I have dropped few rows where some field values were missing.  Here is the snapshot of the of such file cleaning : 

| user  | transaction date | sales amount      | join date | region          |      |
| ----- | ---------------- | ----------------- | --------- | --------------- | ---- |
| 786   | 7253             | February/01/2013  | 59.50     | NaN             | C    |
| 2146  | 202              | March/09/2013     | NaN       | January/25/2003 | B    |
| 5525  | 3362             | June/01/2013      | 23.47     | NaN             | B    |
| 5545  | 7253             | June/01/2013      | 11.31     | NaN             | C    |
| 6017  | 7253             | June/11/2013      | 20.23     | NaN             | C    |
| 7235  | 7253             | July/06/2013      | 34.02     | NaN             | C    |
| 11156 | 4080             | September/27/2013 | 56.52     | NaN             | D    |
| 14344 | 3362             | December/08/2013  | 6.89      | NaN             | B    |
| 14704 | 7253             | December/13/2013  | 34.01     | NaN             | C    |

Finally, the single data frame is create which is a concatenation of the all the processed dataframes. This final dataframe has the following fields : *'user', 'region', 'transaction_date_datetime', 'transaction_date_date',  'transaction_date_month', 'transaction_date_year', 'join_date_datetime', 'join_date_date', 'join_date_month', 'join_date_year', 'sales_amount'* . This data frame can be accessed through the instance of the class DB.

### DB Queries Logic

#### Revenue:

To get the revenue in a time series format, following logic is used:

- Group by `transaction_date_year`
- Sum over `sales_amount`

```python
revenue = handler.data.groupby(['transaction_date_year']).sum()['sales_amount']
```

#### Active Users

To get the active users in a time series format, following logic is used:

- Select all unique `user` and `transaction_date_year` - Achieved by dropping remaining duplicates.
- Group by `transaction_date_year`
- Count over `user`

```python
df = handler.data.drop_duplicates(subset=['user', 'transaction_date_year'],keep='first')
activeusers = df.groupby(['transaction_date_year']).count()['user']
```

#### New User Count

To get the new user count in a time series format, following logic is used:

- Select all unique `user` and `join_date_year` - Achieved by dropping remaining duplicates.
- Group by `join_date_year`
- Count over `user`

```python
df = handler.data.drop_duplicates(subset=['user', 'join_date_year'], keep='first')
newusercount = df.groupby(['join_date_year']).count()['user']
```

#### Average Revenue per Active User

To get the Average Revenue per Active User in a time series format, following logic is used:

- Get revenue from the previous logic. 
- Get Active users from the previous logic.
- Divide the two queries

```python
revenue = handler.data.groupby(['transaction_date_year']).sum()['sales_amount']
df = handler.data.drop_duplicates(subset=['user', 'transaction_date_year'],keep='first')
activeusers = df.groupby(['transaction_date_year']).count()['user']
arpau = revenue / activeusers
```

### API Configuration

To build the REST API, I have used python's flask. The application configuration is default and I am using it on DEBUG mode for convince. 

```python
app = Flask(__name__)
```

```python
@app.route('/revenue/', methods=['GET'])
def api_get_revenue():
    revenue = handler.data.groupby(['transaction_date_year']).sum()['sales_amount']
    reply = ('{"revenue" : %s}' % (revenue.to_json()))
    return Response(reply, status=200, mimetype='application/json')
```

```python
@app.route('/activeusers/', methods=['GET'])
def api_get_activeusers():
    df = handler.data.drop_duplicates(subset=['user', 'transaction_date_year'], keep='first')
    activeusers = df.groupby(['transaction_date_year']).count()['user']
    reply = ('{"activeusers" : %s}' % (activeusers.to_json()))
    return Response(reply, status=200, mimetype='application/json
```

```python
@app.route('/newusercount/', methods=['GET'])
def api_get_newusercount():
    df = handler.data.drop_duplicates(subset=['user', 'join_date_year'], keep='first')
    newusercount = df.groupby(['join_date_year']).count()['user']
    reply = ('{"newusercount" : %s}' % (newusercount.to_json()))
    return Response(reply, status=200, mimetype='application/json')
```

```python
@app.route('/arpau/', methods=['GET'])
def api_get_arpau():
    revenue = handler.data.groupby(['transaction_date_year']).sum()['sales_amount']
    df = handler.data.drop_duplicates(subset=['user', 'transaction_date_year'], keep='first')
    activeusers = df.groupby(['transaction_date_year']).count()['user']
    arpau = revenue / activeusers
    reply = ('{"arpau" : %s}' % (arpau.to_json()))
    return Response(reply, status=200, mimetype='application/json')
```

### Testing API

I have used Chrome HTML Response debugger and Postman application. Average response time for each query was 30ms. Here is the link for a [demo](https://gfycat.com/TiredMasculineAnemonecrab). 

### Hosting Platform

My priority choice to host the flask app was to use HEROKU. Unfortunately, HEROKU's servers have some issue hosting the app. Hence, I used another cloud hosting service - NGORK.

Here's the URL to access the index: `http://5fe07145.ngrok.io`

## Technical Questions

1. **What changes would you make in order to be able to segment each metric:**

2. 1. **By region** 

      I would have used nested *groupby* operation in pandas to first query the metric via logic explained above (which include a *groupby* operation) and then query with respect to region.

   2. **By year joined**

      same as above.

3. **What tests would you write in order to check for:**

4. 1. **Correctness of data**

      I would first test the ambiguous entities present in the field (ex : extra fields, additional delimiters). This can be tested with standard template matching. Also, I would check for NAN's or inconsistent data type within dataframe (this operation is quite fast).  

   2. **Correctness of metrics**

      I would write unit tests (via unittest module in python) for each metric for deterministic row operations.

   3. **Correctness of API behavior**

      This can be done via multiple calls to API for different metric via postman. This will also validate the index URL. Unit test (python unittest module) can be used here as well.

5. **Suppose additional data were to be sent daily, what changes would you make to allow for the API to report updated numbers daily?**

   My current implementation of instance of DB can incorporate dynamic data. I have created a class function (demo) for reading through a data from a directory which can be updated via live feed. Hence, the dataframe can be updated as any new file arrive. To complete this process, another function is needed with can update the current dataframe initiated by the DB instance. 

	. **What would you add to the API you have built to give more value to a business?**  	

   We can always build on a baseline model (current model). For starters, we can connect to NoSQL database like MongoDB for faster queries. Also, we can add additional interface to API which can return multiple formats besides JSON. 

## References

1. [Flask project for REST API documentation.](http://flask.pocoo.org/docs/1.0/)
2. [Postman API platform](https://www.getpostman.com/docs/v6/postman/api_documentation/intro_to_api_documentation)
3. [Testing REST API (additional resource)](https://www.guru99.com/testing-rest-api-manually.html)

## 

Naman Shukla

Masters of Science in Advanced Analytics (ISE)

University of Illinois at Urbana Champaign

Illinois - IL, USA