import argparse
import json
import os
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from yle_news import configs, get_yle_news

def read_text_file(file_name):
    content = ""
    with open(file_name, 'r', encoding='utf-8') as file:
        content = file.read()
    return content

def write_text_file(file_path, content):
     with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def read_news(path):
    with open(path, 'r') as f:
        data = json.load(f)
    return data

def write_one_news_prompt(news_json, path_prompt_template,final_prompt_path):
    prompt_template = read_text_file(path_prompt_template)
    input = news_json['title'] + '\n' + news_json['content']
    prompt = prompt_template.replace('$(INPUT)', input)
    write_text_file(final_prompt_path,prompt)

def find_latest_news():
    contents = os.listdir(configs['LATEST_NEWS_PATH'])
    files = [f for f in contents if os.path.isfile(os.path.join(configs['LATEST_NEWS_PATH'], f))]
    # check that there is only one file in latest_news dir
    if len(files) != 1:
        print(f"there should be only one file in directory {configs['LATEST_NEWS_PATH']}")
        return 
    latest_news_file_path = os.path.join(configs['LATEST_NEWS_PATH'], files[0])
    return latest_news_file_path


def main(args):
    
    # final_prompt_location = "./final_prompt.txt"
    # # prepare the data 
    get_yle_news()
    prompt_template_path = "prompts/summary_template.txt"
    model_path = "~/Projects/Lama/Models/llama-7b-finnish-instruct-v0.2/model.q8.gguf"

    latest_news_file_path = find_latest_news()
    news_json = read_news(latest_news_file_path)
    
    for i, news_obj in enumerate(news_json):
        final_prompt_path = f"./tmp/prompt{i}.txt"
        response_location = f"./tmp/response{i}.txt"
        write_one_news_prompt(news_obj, prompt_template_path, final_prompt_path)
        run_LLM_command = f"llama-cli -m {model_path} -f ./{final_prompt_path} -n -2 --temp 0.4 --repeat_penalty 1.3 > {response_location}"
        print(f"-----------ITERATING {i}-----------")
        os.system(run_LLM_command)
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="An example Python script")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--verbose", action="store_true", help="Tells some statistics")
    args = parser.parse_args()
    # Call the main function with the args parameter set
    main(args)


    # models--deepseek-ai--DeepSeek-R1-Distill-Qwen-1.5B 