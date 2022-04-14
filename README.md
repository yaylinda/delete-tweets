# Delete Tweets

Do you have hundreds of embarrassing tweets on your Twitter profile, that you tweeted over a decade ago as an innocent high schooler, that is now causing you to cringe any time you think about them?

No?

Well, [me](https://twitter.com/lindazheng) either. (With the help of this script!)

## Prerequisits
### Dev Environment
`python3`

### Get Twitter API credentials
Follow the instructions [here](https://developer.twitter.com/en/docs/twitter-api/getting-started/getting-access-to-the-twitter-api) to generate the bearer and access tokens for the Twitter API. Verify that your access tokens allow read and write operations.

You should see something like this on your [Twitter Developer Dashboard](https://developer.twitter.com/en/portal/dashboard) for your Project/App.
![Screen Shot 2022-04-13 at 2 48 54 AM](https://user-images.githubusercontent.com/10225317/163126753-dfcb719a-b27f-441d-abca-c2b619c9ae9d.png)

Make sure you copy and paste the `Consumer API and Secret Keys`, `Bearer Token`, and `Access Token and Secret Keys`, and store them in a safe place! 

### Export Twitter API keys as environment variables
In your terminal (or `.bashrc`, `.bash_profile`, `.zshrc`, etc.) export the API keys keys as evironment variables. These will be used by the python script.
```
export 'BEARER_TOKEN'='<your_bearer_token>'
export 'CONSUMER_KEY'='<your_consumer_key>'
export 'CONSUMER_SECRET'='<your_consumer_secret>'
export 'ACCESS_TOKEN'='<your_access_token>'
export 'ACCESS_SECRET'='<your_access_secret>'
```

### Install Python modules
```
cd <your_local_path>/delete-tweets
pip install -r requirements.txt
```

## Running the Script

The script will delete all your tweets that were authored before a given date. If you would like to delete tweets by another criteria, feel free to implement it, or create an issue / ask questions if you need help.

### Set the Cutoff Date
Open `main.py` and update the `DATE_CUTOFF` variable to any date you would like. Save the file.

### Run main.py
```
python main.py
```

Voila! All embrassing tweets removed!

### Limitations
Due to the rate limits of the Twitter API, this script might take a while to complete depending on how many embarassing tweets you have. The `DELETE` operation can only do 50 requests every 15 minutes. This script has automatic back-off, so just let it run in the background and do its thing. 
