from utils.local_llm import generate_with_ollama

prompt = "Write a professional resume summary for a data analyst with 2 years of experience in Python, SQL, and Power BI."
result = generate_with_ollama(prompt)
print(result)
