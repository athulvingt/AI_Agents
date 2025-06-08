from .agent import study_agent_chain


def generate_summary_quiz(raw_text):
    response = study_agent_chain.invoke(raw_text)
    return response.model_dump()


if __name__ == "__main__":
    user_input = "Prompt engineering involves designing and refining inputs to language models to achieve desired outputs. In the context of agents, prompt engineering allows for better control over how an agent interacts with the environment and solves specific tasks. This is particularly useful in domains like robotics and conversational AI. By adjusting the structure and content of the prompts, users can enhance an agent's performance on specific tasks."
    generate_summary_quiz(user_input)