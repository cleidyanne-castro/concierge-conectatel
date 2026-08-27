"""Adaptador Amazon Bedrock. Mantém a chamada externa isolada para facilitar QA local."""
import json
import boto3

class BedrockClient:
    def __init__(self, region_name: str, model_id: str):
        self.model_id=model_id
        self.client=boto3.client('bedrock-runtime', region_name=region_name)

    def generate(self, question: str, context: str) -> str:
        body={'messages':[{'role':'user','content':[{'text':f'Responda somente com base no contexto.\nContexto:\n{context}\nPergunta: {question}'}]}], 'inferenceConfig':{'maxTokens':300,'temperature':0}}
        response=self.client.invoke_model(modelId=self.model_id, body=json.dumps(body), contentType='application/json', accept='application/json')
        data=json.loads(response['body'].read())
        return data.get('output',{}).get('message',{}).get('content',[{'text':''}])[0]['text']

