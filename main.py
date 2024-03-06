import os
import openai
import dotenv
import pickle
from flask import Flask, request
import sys
from flask_cors import CORS
import re

PLATFORM = sys.platform

os.environ["AZURE_OPENAI_API_KEY"] = ""
os.environ["AZURE_AI_SEARCH_API_KEY"] = ""
os.environ["AZURE_OPENAI_ENDPOINT"] = ""
os.environ["OPENAI_API_VERSION"] = "2023-08-01-preview"
os.environ["AZURE_OPEN_AI_DEPLOYMENT_ID"] = ""
os.environ["AZURE_AI_SEARCH_ENDPOINT"] = ""
os.environ["AZURE_AI_SEARCH_INDEX"] = ""

dotenv.load_dotenv()

endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
api_key = os.environ.get("AZURE_OPENAI_API_KEY")
deployment = os.environ.get("AZURE_OPEN_AI_DEPLOYMENT_ID")

client = openai.AzureOpenAI(
    base_url=f"{endpoint}/openai/deployments/{deployment}/extensions",
    api_key=api_key,
    api_version="2023-08-01-preview",
)
messages = [{"role": "system", "content": "You are helpful"}]

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})
app.config['DEBUG'] = True


def continue_chat():
    completion = client.chat.completions.create(
        model=deployment,
        messages=messages,
        extra_body={
            "dataSources": [
                {
                    "type": "AzureCognitiveSearch",
                    "parameters": {
                        "endpoint": os.environ["AZURE_AI_SEARCH_ENDPOINT"],
                        "key": os.environ["AZURE_AI_SEARCH_API_KEY"],
                        "indexName": os.environ["AZURE_AI_SEARCH_INDEX"],
                        "semanticConfiguration": "default",
                        "queryType": "simple",
                        "fieldsMapping": {},
                        "inScope": True,
                        "roleInformation": "You are an AI assistant that helps people find information.",
                        "filter": "",
                        "strictness": 1,
                        "topNDocuments": 30
                    }
                }
            ]
        },
        temperature=0.5,
        top_p=0.5,
        max_tokens=5387,
        # stream=True
    )
    # For Stream = True
    # return_data=""
    # for chunk in completion:
    #     if chunk.choices[0].delta.content != None:
    #         return_data += chunk.choices[0].delta.content
    #         print(chunk.choices[0].delta.content, end="")
    return {
        "role": "assistant",
        "content": re.sub("doc[0-9]+", "", completion.choices[0].message.content).replace("[]", "").replace("\n",
                                                                                                            "<br/>"),
    }


# For terminal interaction
# while True:
#     print()
#     query = input("Enter query:")
#     messages.append({
#                 "role": "user",
#                 "content": query,
#             })
#     response = continue_chat()
#     messages.append(response)
#     messages.append({"role": "system", "content": "You are helpful"})
#     if "quit" in query or "exit" in query or "bye" in query:
#         with open('pickleFile', 'wb') as fp:
#             pickle.dump(messages, fp)
#         exit(0)


@app.route('/ask', methods=['POST'])
def ask():
    data = request.json
    messages.append(data)
    response = continue_chat()
    messages.clear()
    # messages.append(response)
    messages.append({"role": "system", "content": "You are helpful"})
    return response


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8081)
