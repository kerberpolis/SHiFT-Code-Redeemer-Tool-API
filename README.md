# BorderlandsCodeScraper
Simple Python application that uses the Twitter API to steam tweets from a twitter account dedicated to posting SHiFT and VIP codes for the  borderlands game series and extract information and insert into a database. An archive off the codes is also used as a second source to confirm the validity of the codes. Selenium simulates a user redeeming the SHiFT or VIP codes using the gearbox or vip.borderlands websites. 

This application is run on my Raspberry Pi 3b+ and Selenium 3.4.3 with geckodriver 0.18.0 arm7hf and Firefox ESR 60.8. 
[Compatibiliy between tools found here](https://firefox-source-docs.mozilla.org/testing/geckodriver/Support.html) 

To use Twitter API you must have a Twitter Developer account and fill credentials in credentials.py file as well as login details for gearbox website. 

# Requirements

* Python 3.6
* Sqlite3
* Selenium >= 3.4
* geckodriver 0.18.0-arm7hf
* Firefox ESR 53>=x<=62 

# Setup

## Pre-commit and pre-push hooks
Every Git repository has a .git/hooks folder. Add basic bash script to .git/hooks/pre-commit to run flake8 before each commit to check for PEP8 errors:
```
#!/bin/sh
flake8 .
```
And .git/hooks/pre-push to run tests before you push your code:
```
#!/bin/sh
pytest -vs tests
```
## Local Setup
Install dev requirements for project:
```
pip install -r requirements.txt
```
Run app locally by running the following in your command line
```
uvicorn app.main:app
```
Go to localhost:8000 to view app Hello World message.

## Docker Setup
Build docker image:
```
docker build -t borderlands_app .
```
Run borderlands_app image in docker container locally
```
docker run -p 8000:80 --rm -d --name borderlands_app borderlands_app
```
Go to localhost:8000 to view app Hello World message.
