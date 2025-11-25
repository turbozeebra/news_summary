import requests
from bs4 import BeautifulSoup
import debugpy

import json
from datetime import datetime, timedelta
import os 
import re

from remove_markdown_links import remove_markdown_links, unbold

configs = {
    'TAG_TO_REMOVE': "window.__INITIAL__STATE__=", # Removes the window.__INITIAL__STATE__ variable 
    'REMOVED_FROM_SINGLE': r"<script id='ukko-initial-state' type='text/javascript'>window.__INITIAL__STATE__=",
    'OLD_NEWS_PATH' : "./old_news",
    'LATEST_NEWS_PATH': "./latest_news",
    'HOURS_THRESHOLD':6, # this determines how old the latest news can be before fetching more news 
    'TIMESTAMP_FORMAT': "%Y_%m_%d_%H_%M_%S",
    'LINK_DETERMINOR': "https://"
}

def save_file(file_name, content):
    with open(file_name, 'w', encoding='utf-8') as file:
        file.write(content)

def get_data_from_url_as_soup(url, save=False):
    response = requests.get(url)

    html_content = response.content
    soup = BeautifulSoup(html_content, 'html.parser')
    if save:
        file_path = f"{url.split('/')[-1]}.txt"
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(str(soup))

    return soup

def create_json_from_yle_news(file_path):
    url = 'https://yle.fi/'
    soup = get_data_from_url_as_soup(url)
    
    # find the data from the main page 
    script_tag = soup.find('script', {'id': 'ukko-initial-state'})
    script_text = script_tag.string
    remove_until = len(configs['TAG_TO_REMOVE'])

    state_data = json.loads(script_text[remove_until:])
    page_layout_content_data = state_data["pageData"]["layout"] # this is a list 
    main_page_news_urls = [] 
    for item in page_layout_content_data:
        if item['type'] == 'article':
            main_page_news_urls.append(item['url'])
    
    content_list = []
    i=0
    newline = os.linesep
    for news_url in main_page_news_urls:
        soup_main_page = get_data_from_url_as_soup(news_url)
        i +=1
        section = soup_main_page.find('section', class_='yle__article__content')
        if section != None:
            script_tag = soup_main_page.find('script', id='ukko-initial-state', type='text/javascript')
            json_string = script_tag.string.strip()[len(configs['TAG_TO_REMOVE']):]
            
            data = json.loads(json_string)
            bread_text = ""
            if 'content' in data['pageData']['article'].keys(): 
                for cont in data['pageData']['article']['content']:
                    if cont['type'] == 'heading':
                        bread_text += cont['text']
                        bread_text += newline
                    if cont['type'] == 'text':
                        bread_text += cont['text']
                bread_text_links_removed_unbolded = unbold(remove_markdown_links(bread_text))
                title_text = soup_main_page.title.get_text().split('|')[0].strip()
                content_list.append({"title": title_text, "url": news_url, "content": bread_text_links_removed_unbolded}) 
                   
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(content_list, file, indent=4, ensure_ascii=False)
    
    return content_list
        
def should_fetch_new_news(latest_timestamp):
    current_time = datetime.now()
    time_difference = current_time - latest_timestamp
    return time_difference > timedelta(hours=configs['HOURS_THRESHOLD'])
    
def extract_timestamp(filename):
    file_ext_removed = filename.split('.')
    parts = file_ext_removed[0].split('_')
    timestamp_str = '_'.join(parts[1:7])
    timestamp = datetime.strptime(timestamp_str, configs['TIMESTAMP_FORMAT'])
    return timestamp

def get_yle_news(verbose=False):
    
    # create a folder 
    os.makedirs(configs['OLD_NEWS_PATH'], exist_ok=True)
    os.makedirs(configs['LATEST_NEWS_PATH'], exist_ok=True)
    # check if there is any new files 
    contents = os.listdir(configs['LATEST_NEWS_PATH'])
    # Filter out only the files (excluding subdirectories)
    files = [f for f in contents if os.path.isfile(os.path.join(configs['LATEST_NEWS_PATH'], f))]
    fetch_news = False
    if files:
        #there should be only one file
        if len(files)>1:
            AssertionError(f"There is more than one file in {configs['LATEST_NEWS_PATH']}")
        for file in files:
            timestamp = extract_timestamp(file)
            if(should_fetch_new_news(timestamp)):
                fetch_news = True
                # move file from latest news to old news
                os.rename(os.path.join(configs['LATEST_NEWS_PATH'], file), os.path.join(configs['OLD_NEWS_PATH'], file))

    else : # we don't have any files in the latest_news
        fetch_news = True
    news_list = [] 
    if fetch_news:
        current_time = datetime.now().strftime(configs['TIMESTAMP_FORMAT'])
        file_path = f"{configs['LATEST_NEWS_PATH']}/news_{current_time}.json"
        news_list = create_json_from_yle_news(file_path)
    if verbose:
        if fetch_news:
            print(f"{len(news_list)} news found")
            print("Topics:")
            for news_obj in news_list:
                print(f"\ttitle: {news_obj['title']}")
                print(f"\turl: {news_obj['url']}")
                print("-----------------------------------------------------------")
    return

