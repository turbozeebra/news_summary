from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

system_prompt = "Olet tekoälyavustaja. Vastaat aina mahdollisimman avuliaasti. Vastauksesi eivät saa sisältää mitään haitallista, epäeettistä, rasistista, seksististä, vaarallista tai laitonta sisältöä. Jos kysymyksessä ei ole mitään järkeä tai se ei ole asiasisällöltään johdonmukainen, selitä miksi sen sijaan, että vastaisit jotain väärin. Jos et tiedä vastausta kysymykseen, älä kerro väärää tietoa."

# Check if `torch.bfloat16` is available
dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16

tokenizer = AutoTokenizer.from_pretrained("Finnish-NLP/Ahma-7B-Instruct")
model = AutoModelForCausalLM.from_pretrained("Finnish-NLP/Ahma-7B-Instruct", torch_dtype=dtype, device_map="auto")

# use the chat template feature in the tokenizer to format your (multi-turn) inputs

messages = [
    {
        "role": "system",
        "content": system_prompt,
    },
    {"role": "user", "content": "Kerro kolme hyötyä, joita pienet avoimen lähdekoodin kielimallit tuovat?"},
]
inputs = tokenizer.apply_chat_template(
    messages, tokenize=True, return_tensors="pt"
)
inputs = inputs.to("cuda")

generated_ids = model.generate(
    inputs,
    temperature=0.6,
    do_sample=True,
    min_length=5,
    max_length=2048,
)
generated_text = tokenizer.batch_decode(
    generated_ids, skip_special_tokens=False, clean_up_tokenization_spaces=True
)[0]

print(generated_text.split('[/INST]')[1].strip())

'''
Pienten avointen kielten mallien käyttöönotolla voi olla useita etuja:

1. Lisääntynyt joustavuus ja sopeutumiskyky: Avoimen lähdekoodin mallit mahdollistavat suuremman joustavuuden ja mukauttamisen, jolloin kehittäjät voivat räätälöidä malleja omien tarpeidensa mukaan.
2. Lisääntynyt yhteistyö ja avoimuus: Avoimen lähdekoodin mallit helpottavat yhteistyötä kehittäjien välillä, jotka työskentelevät yhdessä mallin parantamiseksi ja päivittämiseksi, mikä edistää avointa ja yhteistyöhön perustuvaa ympäristöä.
3. Suurempi kehittäjäyhteisö: Avoimen lähdekoodin mallit tarjoavat mahdollisuuden osallistua laajempaan kehittäjäyhteisöön, joka jakaa ideoita, resursseja ja parhaita käytäntöjä, jolloin kaikki voivat hyötyä muiden kokemuksista ja asiantuntemuksesta.
'''
