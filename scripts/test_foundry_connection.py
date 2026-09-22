"""Quick verification script to test live Microsoft Foundry / Azure OpenAI connection."""

import os
import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from config.settings import settings


def test_foundry_connection():
    print("=" * 70)
    print("  Testing Microsoft Foundry / Azure OpenAI Live Connection")
    print("=" * 70)

    endpoint = settings.AZURE_OPENAI_ENDPOINT
    api_key = settings.AZURE_OPENAI_API_KEY
    deployment = settings.AZURE_OPENAI_CHAT_DEPLOYMENT
    api_version = settings.AZURE_OPENAI_API_VERSION

    print(f"[*] Azure OpenAI Endpoint: {endpoint or '[NOT SET]'}")
    print(f"[*] API Key Configured:   {'[YES - ' + api_key[:5] + '...' + api_key[-4:] + ']' if api_key and len(api_key) > 8 else '[NOT SET]'}")
    print(f"[*] Chat Deployment Name:  {deployment}")
    print(f"[*] API Version:           {api_version}")
    print(f"[*] Mock Mode:             {settings.AZURE_MOCK_MODE}")

    if not endpoint or not api_key:
        print("\n[ERROR] Missing AZURE_OPENAI_ENDPOINT or AZURE_OPENAI_API_KEY in .env!")
        print("Please edit your .env file with the values from your Microsoft Foundry portal.")
        return False

    print("\n[*] Sending lightweight probe request to Azure OpenAI...")
    try:
        from openai import AzureOpenAI
        client = AzureOpenAI(
            azure_endpoint=endpoint,
            api_key=api_key,
            api_version=api_version,
            timeout=15.0
        )

        resp = client.chat.completions.create(
            model=deployment,
            messages=[
                {"role": "system", "content": "You are a placement tutor test assistant."},
                {"role": "user", "content": "Ping"}
            ],
            max_completion_tokens=20
        )

        reply = resp.choices[0].message.content
        tokens = resp.usage.total_tokens if resp.usage else 0
        print(f"\n[SUCCESS] Connected to Microsoft Foundry successfully!")
        print(f"[*] Model Response: \"{reply.strip()}\"")
        print(f"[*] Tokens Used: {tokens} (approx. $0.000002)")
        print("\nYour live Microsoft Foundry agent is now ready to use across all 10 pages!")
        return True

    except Exception as e:
        print(f"\n[ERROR] Connection failed: {e}")
        print("\nTroubleshooting tips:")
        print("1. Click 'View deployments' in your Microsoft Foundry portal to check your exact deployment name.")
        print("   Set AZURE_OPENAI_CHAT_DEPLOYMENT=<your-deployment-name> in .env.")
        print("2. Ensure the API key was copied correctly.")
        print("3. Ensure endpoint matches: https://<resource>.openai.azure.com/")
        return False


if __name__ == "__main__":
    test_foundry_connection()
