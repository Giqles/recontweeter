# Recontweeter

This code is for a bot to retweet content on twitter using the #econtwitter hashtag.
It follows some basic rules. Tweets must:

* Be original content (ie, not retweets or replies)
* Not use more than 3 hashtags themselves
* Be in English
* Be sent in the last couple of days

Among tweets matching the above criteria, the bot does a weighted random sample
according to the number of favourites and retweets the tweets have already received.

It also retweets the most popular tweet in the last 7 days on a Friday morning, UTC time. Popularity 
is defined as likes + retweets.

## Background

This set up isn't particularly original! You'll find lots of guides online on how
to do this. I found these three got me pretty much all the way there:

* [Real Python](https://realpython.com/twitter-bot-python-tweepy/)
* [Dev.to](https://dev.to/lorenzotenti/how-to-build-a-serverless-twitter-bot-lph)
* [Anne K Johnson](https://annekjohnson.com/blog/2017/06/python-twitter-bot-on-aws-lambda/index.html)

## Prerequisites

If you want to run one of these yourself, you'll need:

* An AWS account and the AWS CLI configured on your local machine
* To apply for a Twitter developer account

Beyond that you'll obviously need python installed, and node installed.
installed.

### Python config

To get a local version of the python environment set up:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

You'll need to match up your python version with to the runtime in `serverless.yml`.

### Serverless config

Install the serverless package globally (ie, not just for this project):

```bash
npm install -g serverless
```

And then run (from the top level of this directory):

```bash
npm ci
```

To install the exact dependencies I used from `package-lock.json`.

## Credentials

To handle your credentials for the Twitter API, you'll need to make a file: `creds.json`
that contains your consumer key and access token information. It should look something like:

```json
{
    "API_KEY": "XXXXXXXXXXXXXX",
    "API_SECRET": "XXXXXXXXXXXXXX",
    "ACCESS_TOKEN": "XXXXXXXXXXXXXX",
    "ACCESS_SECRET": "XXXXXXXXXXXXXX"
}
```

This is where the `config.py` script is going to load these from.

## Making changes

The main place things happen is in `retweet.py`. It should be fairly obvious which bits to
fiddle with for a different hashtag, more/less tweets etc. The frequency is controlled by
`serverless.yml`.

You should be able to run `retweet.py` locally, but you'll need to add a couple of lines to
actually call the `retweet` function rather than just define it.

## Deploying

With everything installed, it should be a case of running (from the root directory of the project):

```bash
serverless deploy -v
```

To deploy to your AWS account. If you don't want to wait two hours for the function to
fire, run:

```bash
serverless invoke -f retweet
serverless invoke -f popular
```

And if you want to delete it from your AWS account:

```bash
serverless remove
```
