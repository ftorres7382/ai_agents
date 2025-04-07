from app_code.enums import *
from app_code.agents.secretary_agent import secretary_agent

# ollama settings
ollama_url = "http://localhost"
ollama_api_port: int =  11434 
complete_ollama_api_url = f"{ollama_url}:{ollama_api_port}"

# app settings
requirements_check_verbose = True

# This is the agent that will be run
selected_agent = secretary_agent(
    name="Quinn",
    model_name=VALID_MODEL_NAMES.deepseek_r1_14b
)