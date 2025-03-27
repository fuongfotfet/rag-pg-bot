'''
Task: 
Connect with the openAI model 

generate search results from search index 

feed into model 

write a prompt that includes: user's prompt, search results 

return model's response and evidence 
'''
from vectorize import client
from search import search_serive_key, search_service_endpoint, search_index_name
import os 
from dotenv import load_dotenv
load_dotenv(override = True)
chat_completion_model = os.getenv("OPENAI_CHAT_COMPLETION_MODEL_NAME")
from search import search

def chat_complete(user_query):
    search_results = search(user_query)
    '''
    results = [doc[KB_FIELDS_SOURCEPAGE] + ": " + doc[KB_FIELDS_CONTENT].replace("\n", "").replace("\r", "") for doc in r]
    content = "\n".join(results)
    '''
    data_source = [doc["sourcefile"] + ", page " + str(doc["page"]) +  ":" + doc["content"].replace("\n", "").replace("\r", "")  for doc in search_results]
    content = "\n".join(data_source)

    openai_client = client()
    response = openai_client.chat.completions.create(
        model = chat_completion_model, 
        messages = [
            {"role":"system", "content": "You are an AI assistant trained to answer queries based on the following information:" + content + "Provide sourcefile and the page number you used to answer the question."}, 
            {"role":"user", "content": user_query}
        ]
    )

    print(response.to_json())
    print(response.choices[0].message.content)

def inspections(): 
    print(os.getenv("OPENAI_KEY"))
    print(client())
    print(chat_completion_model)
    print(search_serive_key)
    print(search_service_endpoint)
    print(search_index_name)

if __name__ == "__main__": 
    user_query = "what are the 5 key challenges faced by Indian FIs"
    chat_complete(user_query)
    # inspections()
    