# news_summary


In ths repo you can find code for my news summary project.

to run the program: 
```
python3 main.py --model_path your-path-to-model
```

By running "main.py" the code first fetches new news from yle.fi and then it parses the news so that it can be added to the [prompt template](prompts/summary_template.txt) after which the prompt is given to an llm that understands finnish. We use llama cpp to run the model. I used this model: https://huggingface.co/Finnish-NLP/llama-7b-finnish-instruct-v0.2 . This model was quatized.