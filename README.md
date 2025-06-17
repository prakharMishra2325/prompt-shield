# prompt-shield
This is a middleware firewall that blocks malicious prompts before they even get to the LLM for inference. I'm using DistillBERT model for detecting unsafe prompts, Streamlit for frontend, and Ollama for local LLMs. The dataset contains aorund 10k safe and 10k unsafe prompts.
