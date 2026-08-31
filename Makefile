install:
	python -m pip install -r requirements.txt

test:
	python -m pytest -q

run:
	python -m src.cli --question "teste local"

# Semeia o bucket S3 (que ja deve existir) com embeddings.json e chunks.json.
# Requer S3_BUCKET_NAME no ambiente ou no .env.
seed-kb:
	python src/parte_02_rag/upload_to_s3.py

# Build + deploy da infra serverless (retrieve_kb + API). Primeira vez: use
# `sam deploy --guided` para gravar o samconfig.toml.
deploy:
	sam build && sam deploy --parameter-overrides KnowledgeBaseBucketName=$$S3_BUCKET_NAME
