.PHONY: setup start ingest algorithms demo benchmark stop reset help

help: ## Show this help message
	@echo "═══════════════════════════════════════════════════"
	@echo "  PhoneGraph: Supply Chain Intelligence Engine"
	@echo "═══════════════════════════════════════════════════"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m  %-15s\033[0m %s\n", $$1, $$2}'

setup: ## Install all Python dependencies
	pip install -r requirements.txt

start: ## Start Memgraph + all services via Docker Compose
	docker-compose up -d
	@echo "⏳ Waiting for Memgraph to be healthy..."
	@sleep 10
	@echo "✅ Services started. Memgraph Lab: http://localhost:3000"

ingest: ## Load all supply chain data into Memgraph
	python -m ingestion.graph_builder
	@echo "✅ Supply chain graph loaded into Memgraph"

algorithms: ## Run all graph algorithms and cache results
	python -m algorithms.pagerank
	python -m algorithms.betweenness
	python -m algorithms.community_detection
	@echo "✅ All graph algorithms executed"

demo: ## Open Streamlit dashboard in browser
	streamlit run dashboard/app.py

api: ## Start FastAPI backend only
	uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

benchmark: ## Run RAG vs GraphRAG comparison benchmark
	python -m evaluation.benchmark

stop: ## Stop all Docker Compose services
	docker-compose down

reset: ## Wipe database and start fresh
	docker-compose down -v && make start && sleep 15 && make ingest
	@echo "✅ Database reset and reloaded"

lint: ## Check code quality
	python -m py_compile graph/connection.py
	python -m py_compile ingestion/graph_builder.py
	python -m py_compile graphrag/chain.py
	python -m py_compile api/main.py
	@echo "✅ All files compile successfully"
