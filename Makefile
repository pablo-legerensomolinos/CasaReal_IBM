build:
	docker build \
		--platform=linux/x86_64 \
		-f Dockerfile \
		-t backend_database_query:latest .

start: build
	docker run -d -p 8000:8000 \
		--name backend_database_query \
		--env-file .env\
		backend_database_query:latest

stop:
	docker stop backend_database_query
	docker rm backend_database_query

clean:
	docker rm -f backend_database_query
	docker rmi -f backend_database_query:latest

restart: stop start

.PHONY: logs
logs:
	docker logs -f backend_database_query