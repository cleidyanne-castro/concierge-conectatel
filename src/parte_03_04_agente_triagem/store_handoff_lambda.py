import os
import json
import boto3

dynamodb = boto3.resource("dynamodb")
TABLE_NAME = os.environ.get("TABLE_NAME", "concierge-conectatel-escalonamentos")
table = dynamodb.Table(TABLE_NAME)

def handler(event, context):
    """
    Recebe os dados do HandoffRecord e persiste no DynamoDB.
    Chave primária: trace_id
    """
    try:
        # Garante que o evento contenha os campos obrigatórios
        item = {
            "trace_id": event.get("trace_id"),
            "protocolo_atendimento": event.get("protocolo_atendimento"),
            "data_hora_abertura": event.get("data_hora_abertura"),
            "canal_origem": event.get("canal_origem", "chat"),
            "categoria_motivo": event.get("categoria_motivo"),
            "resumo_caso": event.get("resumo_caso"),
            "historico_ja_levantado": event.get("historico_ja_levantado"),
            "produto_servico_envolvido": event.get("produto_servico_envolvido"),
            "documento_fonte_consultado": event.get("documento_fonte_consultado"),
            "urgencia": event.get("urgencia", "media"),
            "dados_contato_retorno": event.get("dados_contato_retorno"),
        }

        table.put_item(Item=item)

        return {
            "statusCode": 200,
            "body": json.dumps({"status": "success", "trace_id": item["trace_id"]})
        }
    except Exception as e:
        print(f"Erro ao gravar no DynamoDB: {str(e)}")
        raise e