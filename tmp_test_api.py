"""Find which models actually work with this HF token."""
import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv()
token = os.getenv("HF_TOKEN", "")

client = InferenceClient(api_key=token)

# Models known to work on HF free tier via router
candidates = [
    "mistralai/Mistral-7B-Instruct-v0.3",
    "mistralai/Mistral-7B-Instruct-v0.2",
    "microsoft/Phi-3-mini-4k-instruct",
    "microsoft/Phi-3.5-mini-instruct",
    "meta-llama/Llama-3.1-8B-Instruct",
    "meta-llama/Meta-Llama-3-8B-Instruct",
    "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
    "Qwen/Qwen2.5-7B-Instruct",
    "google/gemma-2-2b-it",
    "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B",
]

print("Testing models...\n")
for model in candidates:
    try:
        resp = client.chat_completion(
            model=model,
            messages=[{"role": "user", "content": "Say OK"}],
            max_tokens=10,
            temperature=0.1,
        )
        content = resp.choices[0].message.content
        print(f"[OK]   {model} -> {content!r}")
        break  # Stop at first working model
    except Exception as e:
        err = str(e)
        if "model_not_supported" in err:
            print(f"[SKIP] {model} -> not supported")
        elif "402" in err or "payment" in err.lower():
            print(f"[PAY]  {model} -> requires payment")
        elif "403" in err:
            print(f"[AUTH] {model} -> permission denied")
        else:
            print(f"[ERR]  {model} -> {err[:120]}")
