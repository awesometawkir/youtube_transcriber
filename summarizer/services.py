
import os
from openai import OpenAI

# Default models list to show in UI
MODELS = {
    'openai': [
        {'id': 'gpt-4o-mini', 'name': 'ChatGPT 4o Mini'},
        {'id': 'gpt-4o', 'name': 'ChatGPT 4o'},
    ],
    'openrouter': [
        {'id': 'openai/gpt-4o-mini', 'name': 'ChatGPT 4o Mini'},
        {'id': 'anthropic/claude-3.5-sonnet', 'name': 'Claude 3.5 Sonnet'},
        {'id': 'mistralai/devstral-2512:free', 'name': 'Mistral Devstral 2512 (Free)'},
        {'id': 'qwen/qwen3-coder:free', 'name': 'Qwen 3 Coder (Free)'},
        {'id': 'moonshotai/kimi-k2:free', 'name': 'Moonshot Kimi K2 (Free)'},
        {'id': 'meta-llama/llama-3.3-70b-instruct:free', 'name': 'Llama 3.3 70B (Free)'},
        {'id': 'meta-llama/llama-3-70b-instruct', 'name': 'Llama 3 70B'},
        {'id': 'google/gemini-pro-1.5', 'name': 'Gemini 1.5 Pro'},
        {'id': 'mistralai/mistral-large', 'name': 'Mistral Large'},
    ]
}

def get_client(provider, api_key):
    if provider == 'openai':
        return OpenAI(api_key=api_key)
    elif provider == 'openrouter':
        return OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key
        )
    else:
        raise ValueError("Invalid provider")

def generate_summary(text, context_list, model, api_key, provider):
    """
    text: The main text to summarize
    context_list: List of strings (other pdfs/transcripts) to use as context
    """
    if not api_key:
        return {'error': 'API Key is missing'}

    try:
        client = get_client(provider, api_key)
        
        # Prepare messages
        messages = [
            {"role": "system", "content": "You are a helpful AI assistant. Summarize the content provided by the user. Use the additional context provided if relevant."}
        ]

        # Add Context
        for i, ctx in enumerate(context_list):
            messages.append({"role": "user", "content": f"<Context_{i+1}>\n{ctx}\n</Context_{i+1}>"})

        # Add Main Text
        messages.append({"role": "user", "content": f"Please summarize the following text:\n\n{text}"})

        response = client.chat.completions.create(
            model=model,
            messages=messages,
            # sites like openrouter might need extra headers, but standard openai client usually works if base_url is set
        )
        
        return {'result': response.choices[0].message.content}

    except Exception as e:
        return {'error': str(e)}
