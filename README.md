# prompt-shield
This is a middleware firewall that blocks malicious prompts before they even get to the LLM for inference. I'm using DistillBERT model for detecting unsafe prompts, Streamlit for frontend, and Ollama for local LLMs. The dataset contains aorund 10k safe and 10k unsafe prompts.

<span style="color:red">NOTE:</span> This app requires the relevant checkpoint folder to run. DOWNLOAD IT HERE: https://drive.google.com/drive/folders/1-9VjeK6Bgsq-UhNWj0eGaprFKk82HgJ6?usp=sharing

## How to run
To run this app, you must do the following:
* Create a virtual environment: `python -m venv .venv`
* Activate the virtual environment:
  * For Windows: `.\.venv\Scripts\Activate`
  * For Linux: `source .venv/bin/activate`
* Install the necesssary packages from the requirements.txt file present in the repo: `pip install -r requirements.txt`
  * NOTE: If there are issues in installing packages from requirements.txt, then directly install each package. The list of packages is present in the file 'venv_list_of_imp_packages.txt'.
* If you wish to go through the dataset collection or model training process, or if you would like to change any details, run 'comp8420_project_v2.ipynb'.
* If you would like to run the app, then open a terminal with the virtual environment activated, and type: `streamlit run main.py`.

## How the app works
* The app demonstrates the usage of PromptShield as a prompt firewall, that blocks malicious prompts before they get to the LLM.
* On the sidebar, there are two key options:
  * **Rewrite checkbox**: checking this will rewrite any malicious prompts into sanitised prompts.
  * **Personalities selectbox**: you can select from several personalities.
    * Currently, there are two, besides the vanilla chatbot: "Shodan" and "Clippy". If you wish to change them or add more, you can edit 'personalities.py'.
    * "Clippy" is inspired by the same character from MS Word. Clippy is supposed to be very easy-going and friendly.
    * "Shodan" is designed to be a more risky, threatening version. This is to contrast how an LLM with more risky system prompts deals with rewritten malicious prompts.
