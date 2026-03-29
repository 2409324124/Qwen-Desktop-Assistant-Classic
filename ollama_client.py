import httpx
import json

class OllamaClient:
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "qwen2.5:1.5b"):
        self.base_url = base_url
        self.model = model

    async def generate(self, prompt: str, system: str = None):
        """
        Sends a non-streaming request to Ollama and returns the full response.
        """
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }
        if system:
            payload["system"] = system

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            return response.json().get("response", "")

    async def generate_stream(self, prompt: str, system: str = None):
        """
        Generates a stream of responses from Ollama.
        """
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": True
        }
        if system:
            payload["system"] = system

        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream("POST", url, json=payload) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if not line:
                        continue
                    try:
                        chunk = json.loads(line)
                        if "response" in chunk:
                            yield chunk["response"]
                        if chunk.get("done"):
                            break
                    except json.JSONDecodeError:
                        continue

if __name__ == "__main__":
    # Test script
    import asyncio

    async def test():
        client = OllamaClient()
        print("Testing Ollama Generate...")
        try:
            resp = await client.generate("Hello, who are you?")
            print(f"Response: {resp}")
        except Exception as e:
            print(f"Error: {e}")

    asyncio.run(test())
