build-multimodal-rag:
	docker compose build

start-multimodal-rag:
	docker compose up --build -d

stop-multimodal-rag:
	docker compose stop