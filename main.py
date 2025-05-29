import os
from openai import OpenAI
from openai import APIError, RateLimitError, AuthenticationError, OpenAIError

client = OpenAI()

try:
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Hello!"}]
    )
    print("✅ Success! Got a response:")
    print(response.choices[0].message.content)

except AuthenticationError as e:
    print("❌ Authentication failed — your API key may be invalid.")
    print(e)

except RateLimitError as e:
    print("⚠️ Quota error — you may be out of credits or on a free tier that's exhausted.")
    print(e)

except APIError as e:
    print("❗ OpenAI API error (temporary or invalid request):")
    print(e)

except OpenAIError as e:
    print("❗ General OpenAI error:")
    print(e)

except Exception as e:
    print("❗ Unknown error:")
    print(e)
