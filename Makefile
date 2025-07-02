build:
	docker build \
		--platform=linux/x86_64 \
		-f Dockerfile \
		-t fastapi_template:latest .

start: build
	docker run -d -p 8000:8000 \
		--name fastapi_template \
		--env-file .env\
		fastapi_template:latest

stop:
	docker stop fastapi_template
	docker rm fastapi_template

clean:
	docker rm -f fastapi_template
	docker rmi -f fastapi_template:latest

restart: stop start

.PHONY: logs
logs:
	docker logs -f fastapi_template