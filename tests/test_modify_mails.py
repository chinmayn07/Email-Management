import unittest
from unittest.mock import MagicMock
from app import modify_mails


class TestModifyMails(unittest.TestCase):
    def test_mark_as_read(self):
        # Mock the Gmail service object
        service = MagicMock()
        mail_row = [("mail_id_123")]
        action = {"action_type": "VIEW", "mark": "READ"}

        # Call the function
        modify_mails(service, [mail_row], {"actions": [action]})

        # Assert that the modify method was called with the correct parameters
        service.users().messages().modify.assert_called_once_with(
            userId="me", id="mail_id_123", body={"removeLabelIds": ["UNREAD"]}
        )

    def test_move_to_starred(self):
        service = MagicMock()
        mail_row = [("mail_id_456")]
        action = {"action_type": "MOVE", "destination": "STARRED"}

        modify_mails(service, [mail_row], {"actions": [action]})

        service.users().messages().modify.assert_called_once_with(
            userId="me", id="mail_id_456", body={"addLabelIds": ["STARRED"]}
        )


if __name__ == "__main__":
    unittest.main()
