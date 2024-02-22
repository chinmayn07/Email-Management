# Gmail API Email Management

This script allows you to retrieve emails from Gmail, store them in an SQLite database, and perform queries and modifications based on specified criteria. It utilizes the Gmail API for email retrieval and the SQLite database for storage and querying.

## Prerequisites

Before running the script, ensure you have the following Python packages installed:

- `google-api-python-client`
- `google-auth-oauthlib`
- `python-dateutil`

You can install these packages using pip:

```bash
pip install google-api-python-client google-auth-oauthlib python-dateutil
```

Additionally, you need to create a Google service account with the Gmail API enabled and generate an OAuth Client ID. Configure the consent screen for the Authorization Code Flow and add the required scopes during the configuration.

## About Code Functionality

The script performs the following tasks:

1. Fetches emails from the Gmail API and stores them in an SQLite database.
2. Allows querying of the database for matches in fields such as sender, receiver, date, and subject.
3. Modifies queried emails to be marked as read or starred based on specified actions, which are provided via a JSON configuration file.

## How to Run the Script

1. Run `app.py` with the argument `"fetch_mails"` initially to fetch and store email data to the database:

   ```bash
   python app.py fetch_mails
   ```

2. After fetching emails, you can alter the `filters.json` file to specify query criteria and modification actions on emails.

3. Run `app.py` again without any arguments to apply the modifications specified in the `filters.json` file:

   ```bash
   python app.py
   ```

## Example Usage

1. Fetch emails:

   ```bash
   python app.py fetch_mails
   ```

2. Modify emails based on specified criteria in `filters.json`:

   ```bash
   python app.py
   ```

## Note

Ensure that you have appropriate permissions and have consented to the requested scopes when running the script.
