# huggingface_utils.py

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

def generate_prompt(question, prompt_file="prompt.md", metadata_file="metadata.sql"):
    with open(prompt_file, "r") as f:
        prompt = f.read()
    
    with open(metadata_file, "r") as f:
        table_metadata_string = f.read()

    prompt = prompt.format(
        user_question=question, table_metadata_string=table_metadata_string
    )
    return prompt

def get_tokenizer_model(model_name):
    print(f"Pobieranie modelu {model_name}...")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        trust_remote_code=True,
        torch_dtype=torch.float16,
        device_map="auto",
        use_cache=True,
    )
    print("Model pobrany.")
    return tokenizer, model

def run_inference(question, prompt_file=r"C:\Users\Alek\Desktop\PerroScout\Django\PerroScout\main\prompt.md", metadata_file=r"C:\Users\Alek\Desktop\PerroScout\Django\PerroScout\main\metadata.sql"):
    tokenizer, model = get_tokenizer_model("defog/sqlcoder-7b-2")
    prompt = generate_prompt(question, prompt_file, metadata_file)
    
    eos_token_id = tokenizer.eos_token_id
    pipe = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        max_new_tokens=300,
        do_sample=False,
        return_full_text=False,
        num_beams=5,
    )
    generated_query = (
        pipe(
            prompt,
            num_return_sequences=1,
            eos_token_id=eos_token_id,
            pad_token_id=eos_token_id,
        )[0]["generated_text"]
        .split(";")[0]
        .split("```")[0]
        .strip()
        + ";"
    )
    return generated_query
