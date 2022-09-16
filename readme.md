
# NoteApp

Demonstration project to deepen my skills with FastAPI, Flask, DynamoDB and the web stack *(I'm not frontend dev)*

All this code is made for educational purposes, take and make of it what you want!

If you want to improve some parts and have them uploaded to this repo just commit!

## Python libraries used
* FastAPI: Used for the API with which the database interacts with Flask.
* Flask: Used to render HTML documents (using Jinja2) and receive frontend requests.
* Boto3: Used to interact with the database (AWS DynamoDB).

## How to test it with your database
This tutorial is only going to work if you use **DynamoDB**!

You need create an IAM user with application access.

Then copy the login data and paste it into the `credentials.json` file. 

This file must be inside the `db/.aws` folder (create the last folder).

Now you must apply the rot-13 algorithm to this data. So that they are not exposed to the naked eye in your project.


Let's think of your login data as looking like this **without** the rot-13 algorithm:
```
{
    "aws_access_key_id": "KeyIDExposed",
    "aws_secret_access_key": "ThiIstheacceskey",
    "region_name": "your-aws-region"
}

```
After applying the rot-13 algorithm it should look like this:
```
{
    "aws_access_key_id": "XrlVQRkcbfrq",
    "aws_secret_access_key": "GuvVfgurnpprfxrl",
    "region_name": "lbhe-njf-ertvba"
}

```
Finally, your file structure for the database should look like this:

![image](https://s3.us-west-2.amazonaws.com/aleph-content/photos/435/81ad17f7-d0a5-4bbc-8d3e-9ee6982d9bbe)

## Running the Web App!
1. Make a Virtual Enviroment
```
python -m venv venv
```
2. Activate the Virtual Enviroment
```
# Windows
.\venv\Scripts\activate

# Linux
source venv/bin/activate
```
3. Install dependencies
```
pip install -r requirements.txt
```
4. Execute the `webapp.py` program
```
python webapp.py
```
5. In other terminal execute the `api.py` program.
```
python api.py
```
6. Check in your browser `localhost:5000`
![image](https://s3.us-west-2.amazonaws.com/aleph-content/photos/435/9efd25bf-fdf1-4daa-a81e-b0b038e12776)

7. Sign up on the app!