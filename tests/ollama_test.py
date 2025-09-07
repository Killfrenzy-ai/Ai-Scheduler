from langchain_community.llms import Ollama

def test_ollama():
    # Create Ollama client
    llm = Ollama(model="mistral", temperature=0)

    # Simple test prompt
    response = llm.invoke("Extract name and date of birth from this text: 'My name is John Doe and I was born on May 15, 1980.'")

    print("✅ Ollama response:")
    print(response)

if __name__ == "__main__":
    test_ollama()
