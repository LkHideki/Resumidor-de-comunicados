import unittest
import os
import tempfile
import dotenv
from helpers import read_tickers_from_txt, certify_aux_folder_exists, get_folder_size, delete_negative_files_if_folder_is_huge
from meu_email import email_me

class TestHelpers(unittest.TestCase):

    def test_read_tickers_from_txt(self):
        with tempfile.NamedTemporaryFile(delete=False) as tf:
            tf.write(b"ABCD\nEFGH\n#IGNORE\n-IGNORE\n123\n")
            tf.close()
            tickers = read_tickers_from_txt(tf.name)
            self.assertEqual(tickers, ["ABCD", "EFGH"])
            os.unlink(tf.name)

    def test_certify_aux_folder_exists(self):
        with tempfile.TemporaryDirectory() as td:
            os.chdir(td)
            certify_aux_folder_exists("aux")
            self.assertTrue("aux" in os.listdir())
            self.assertTrue(os.path.isdir("aux"))

    def test_get_folder_size(self):
        with tempfile.TemporaryDirectory() as td:
            os.chdir(td)
            with open("file1.txt", "w") as f:
                f.write("Hello, world!")
            with open("file2.txt", "w") as f:
                f.write("Hello, again!")
            size = get_folder_size(".")
            self.assertEqual(size, len("Hello, world!") + len("Hello, again!"))

    def test_delete_negative_files_if_folder_is_huge(self):
        with tempfile.TemporaryDirectory() as td:
            os.chdir(td)
            with open("file1.txt", "w") as f:
                f.write("Hello, world!")
            with open("-file2.txt", "w") as f:
                f.write("Hello, again!")
            delete_negative_files_if_folder_is_huge(".", 10)
            self.assertTrue("file1.txt" in os.listdir())
            self.assertFalse("-file2.txt" in os.listdir())

class TestEmailer(unittest.TestCase):
    def test_email_me(self):
        dotenv.load_dotenv()
        # Test if the email_me function is working
        result = email_me(os.getenv('EMAIL'), "Test Subject", "Test Body")
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()
