from langchain.llms import OpenAI

llm = OpenAI(temperature=0.3)

def generate_code(prompt):
    return llm(f"Write Python code for: {prompt}")

available_tools = type('toolkit', (), {'llm': llm})