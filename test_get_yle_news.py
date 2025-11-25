from yle_news import create_json_from_yle_news, should_fetch_new_news, extract_timestamp, get_yle_news
from yle_news import configs 
import os
import shutil
import unittest
from datetime import datetime, timedelta

# python3 -m unittest test_get_yle_news.py
configs['LATEST_NEWS_PATH'] = f"./test{configs['LATEST_NEWS_PATH'][1:]}"
configs['OLD_NEWS_PATH'] = f"./test{configs['OLD_NEWS_PATH'][1:]}"
class TestGetYleNews(unittest.TestCase):
    def setUp(self):
        self.test_dir = "./test"
        os.makedirs(self.test_dir, exist_ok=True)
        os.makedirs(configs['OLD_NEWS_PATH'], exist_ok=True)
        os.makedirs(configs['LATEST_NEWS_PATH'], exist_ok=True)
        #os.chdir(self.test_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_create_json_from_yle_news(self):
        current_time = datetime.now().strftime(configs['TIMESTAMP_FORMAT'])
        file_path = f"{configs['LATEST_NEWS_PATH']}/news_{current_time}.json"
        create_json_from_yle_news(file_path)
        files = os.listdir(configs['LATEST_NEWS_PATH'])
        self.assertTrue(len(files) > 0)

    def test_should_fetch_new_news(self):
        files = [f"news_{datetime.now().strftime(configs['TIMESTAMP_FORMAT'])}.json"]
        timestamp = extract_timestamp(files[0])
        self.assertFalse(should_fetch_new_news(timestamp))
        self.assertTrue(should_fetch_new_news(timestamp - timedelta(hours=configs['HOURS_THRESHOLD'] + 1)))

    def test_extract_timestamp(self):
        filename = "news_2020_01_01_12_00_00.json"
        timestamp = extract_timestamp(filename)
        self.assertEqual(timestamp, datetime(2020, 1, 1, 12, 0, 0))

    def test_main(self):
        # add old file to the latest news 
        filename = f"{configs['LATEST_NEWS_PATH']}/news_2020_01_01_12_00_00.json"
        with open(filename, 'w', encoding='utf-8') as file:
            file.write("test data")
        get_yle_news(None)
        files = os.listdir(configs['LATEST_NEWS_PATH'])
        self.assertTrue(len(files) == 1)
        files = os.listdir(configs['OLD_NEWS_PATH'])
        self.assertTrue(len(files) == 1)

if __name__ == "__main__":
    unittest.main()