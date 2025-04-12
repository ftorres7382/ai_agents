from app_code.Utilities import OLM
from app_code.Agents import secretary_agent


def run() -> None:
    '''
    This function runs the main application
    '''

    check_requirements()

    secretary_agent(
        name="Quinn",
        model_name="qwen2.5-coder"
    ).start()

    



def check_requirements() -> None:

    '''
    This function checks all content and third party content required to run the app
    '''

    # Implement it later, right now the only requirement is ollama and that could change to something else later, not worth the time implementing
    pass



if __name__ == "__main__":
    run()