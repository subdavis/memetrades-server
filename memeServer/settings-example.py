# ! IMPORTANT !
# Create a copy called settings.py

# Mongo connection info
DATABASE = {
    "name":"memes"
}

LAG_ALLOWED=1.5
# Generate this once, and only change it when you want to forece everyone to be logged out.
SECRET_KEY="EXAMPLE" 
# Amount of money to give new users
INITIAL_MONEY=1000.0
# Length in characters of the generated API key.
API_KEY_LENGTH=32
# Number of memes per page for pagination
STOCKS_PER_PAGE=50
# Number of memebucks a referral gets you.
MONEY_PER_REFERRAL=300
# Number of requests per day to allow for api
RATE_LIMIT=1000

# Get this from developers.facebook.com 
FACEBOOK = {
    "APP_ID":"CHANGE",
    "APP_SECRET":"CHANGE",
  # "ACCESS_TOKEN":"CHANGE" # Not ucrrently used
}

#Used to tell facebook where to redirect
SERVER_NAME="http://my_server_name"
