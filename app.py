import os
import pickle
import json
import sys
import time
import datetime
from dateutil.relativedelta import relativedelta
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import db

# Constants
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.modify",
]
FILTERS_FILE = "filters.json"
TOKEN_FILE = "token.pickle"
CREDS_FILE = "creds.json"


def authenticate():
    """Authenticate using OAuth 2.0."""
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "rb") as token_file:
            creds = pickle.load(token_file)
        if creds.valid and not creds.expiry.timestamp() > time.time():
            return creds
        elif creds.refresh_token:
            try:
                creds.refresh(Request())
                with open(TOKEN_FILE, "wb") as token_file:
                    pickle.dump(creds, token_file)
                return creds
            except:
                print("Refresh token expired. Re-authorizing...")
                return perform_authorization()

    return perform_authorization()


def perform_authorization():
    """Perform OAuth 2.0 authorization flow."""
    flow = InstalledAppFlow.from_client_secrets_file(CREDS_FILE, scopes=SCOPES)
    creds = flow.run_local_server(port=0)
    with open(TOKEN_FILE, "wb") as token_file:
        pickle.dump(creds, token_file)
    return creds


def fetch_emails(service):
    """Fetch emails from Gmail."""
    print("Fetching mails")
    results = (
        service.users()
        .messages()
        .list(userId="me", labelIds=["INBOX"], maxResults=50)
        .execute()
    )
    messages = results.get("messages", [])

    if messages:
        dbConn = db.DBHandler()
        for message in messages:
            email = (
                service.users().messages().get(userId="me", id=message["id"]).execute()
            )
            print("Extracting mail data")
            email_data = extract_mail_details(email)
            print("Email Subject: ", email_data["subject"])
            dbConn.insert_data(email_data)
    else:
        print("No messages found.")


def extract_mail_details(mail):
    """Extract mail details from the fetched email."""
    headers = mail["payload"]["headers"]
    mail_id = mail["id"]
    sender = next(
        (header["value"] for header in headers if header["name"] == "From"),
        None,
    )
    receiver = next(
        (header["value"] for header in headers if header["name"] == "To"), None
    )
    mail_date = mail["internalDate"]
    mail_date = int(mail_date) / 1000  # convert milliseconds to seconds
    subject = next(
        (header["value"] for header in headers if header["name"] == "Subject"),
        None,
    )

    return {
        "mail_id": mail_id,
        "sender": sender,
        "receiver": receiver,
        "mail_date": mail_date,
        "subject": subject,
    }


def query_mails_with_filters(service):
    """Query mails based on filters from filters.json."""
    input_data = None
    with open(FILTERS_FILE, "r") as file:
        input_data = json.load(file)

    query_statement = "WHERE "
    conditions = []

    for condition in input_data["condition_list"]:
        field = condition["field"]
        comparison_type = condition["comparison_type"]
        value = condition["value"]
        if comparison_type == "equals":
            conditions.append(f"{field} = '{value}'")
        elif comparison_type == "not equals":
            conditions.append(f"{field} != '{value}'")
        elif comparison_type == "includes":
            conditions.append(f"{field} LIKE '%{value}%'")
        elif comparison_type == "not includes":
            conditions.append(f"{field} NOT LIKE '%{value}%'")
        elif comparison_type == "lesser than":
            time_limit = compute_time_limit(value)
            conditions.append(f"{field} < {time_limit}")

    query_statment = query_statement + (
        " OR ".join(conditions)
        if input_data["condition_type"].upper() == "ANY"
        else " AND ".join(conditions)
    )

    dbConn = db.DBHandler()
    mail_rows = dbConn.query_table(query_statment)
    modify_mails(service, mail_rows, input_data)


def compute_time_limit(date_ranges):
    """Compute the time limit based on date ranges."""
    current_dt = datetime.datetime.now()
    limit_date = current_dt - relativedelta(
        days=-int(date_ranges["days"] or 0), months=-int(date_ranges["months"] or 0)
    )

    time_limit = int(limit_date.timestamp())
    return time_limit


def modify_mails(service, mail_rows, input_data):
    """Modify mails based on specified actions."""
    print("Modifying Mails")
    for mr in mail_rows:
        print("Modifying Mail Subject :", mr[4])
        mail_id = mr[0]
        for action in input_data["actions"]:
            body = None
            if action["action_type"] == "VIEW":
                print("Marking eamil:", action["mark"])
                body = (
                    {"removeLabelIds": ["UNREAD"]}
                    if action["mark"] == "READ"
                    else {"addLabelIds": ["UNREAD"]}
                )
            elif action["action_type"] == "MOVE":
                print("Marking eamil:", action["destination"])
                body = {"addLabelIds": [action["destination"]]}  # Move to folder

            try:
                service.users().messages().modify(
                    userId="me", id=mail_id, body=body
                ).execute()
                print("Email action applied successfully.")
            except Exception as e:
                print("An error occurred:", e)


if __name__ == "__main__":
    creds = authenticate()
    service = build("gmail", "v1", credentials=creds)
    if len(sys.argv) < 2:
        query_mails_with_filters(service)
    else:
        if sys.argv[1] == "fetch_mails":
            fetch_emails(service)
