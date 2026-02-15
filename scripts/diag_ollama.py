import ollama
import asyncio
import time

async def test_ollama():
    print("--- Testing Ollama Synchronous Client ---")
    start = time.time()
    try:
        client = ollama.Client(host="http://localhost:11434")
        response = client.chat(model="llama3.1:latest", messages=[{'role': 'user', 'content': 'hi'}])
        print(f"Sync Result: {response['message']['content']}")
        print(f"Sync Time: {time.time() - start:.2f}s")
    except Exception as e:
        print(f"Sync Error: {e}")

    print("\n--- Testing Ollama Asynchronous Client ---")
    start = time.time()
    try:
        async_client = ollama.AsyncClient(host="http://localhost:11434")
        response = await async_client.chat(model="llama3.1:latest", messages=[{'role': 'user', 'content': 'hi'}])
        print(f"Async Result: {response['message']['content']}")
        print(f"Async Time: {time.time() - start:.2f}s")
    except Exception as e:
        print(f"Async Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_ollama())
