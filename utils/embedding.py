import yaml
import openai


with open("config.yaml", "r") as stream:
    try:
        PARAM = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)

client = openai.OpenAI(api_key = PARAM['openai_api'])

def get_embedding(text, model=PARAM['vector_embedding_model']):
   text = text.replace("\n", " ")
   return client.embeddings.create(input = [text], model=model).data[0].embedding