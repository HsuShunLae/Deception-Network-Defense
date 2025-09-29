.PHONY: all install build run stop start logs clean

# Variables
IP ?= 192.168.229.128
PORT ?= 8080
NAME ?= honeypot
IMAGE ?= struts_honeypot

all: install clone build run

install:
	sudo apt update && sudo apt install -y docker.io docker-compose git

clone:
	@if [ ! -d "StrutsHoneypot" ]; then git clone https://github.com/Cymmetria/StrutsHoneypot.git; fi

build:
	cd StrutsHoneypot && sudo docker build -t $(IMAGE) strutspot_docker/

run:
	sudo docker run -d --name $(NAME) -p $(IP):$(PORT):80 $(IMAGE)

stop:
	sudo docker stop $(NAME) || true

start:
	sudo docker start $(NAME) || true

logs:
	sudo docker logs -f $(NAME)

clean:
	sudo docker rm -f $(NAME) || true
	sudo docker rmi -f $(IMAGE) || true
