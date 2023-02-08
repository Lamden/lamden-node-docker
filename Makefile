COMPOSE_FILE = docker/docker-compose.yml

boot:
ifeq ($(LAMDEN_NETWORK),arko)
	export LAMDEN_BOOTNODES="64.225.32.184:170.64.178.113:134.122.98.27"; \
	docker compose -f $(COMPOSE_FILE) up -d
else ifeq ($(LAMDEN_NETWORK),testnet)
	export LAMDEN_BOOTNODES="128.199.9.156:178.62.52.51:142.93.210.208"; \
	docker compose -f $(COMPOSE_FILE) up -d
else
	docker compose -f $(COMPOSE_FILE) up -d
endif
	@sleep 3
	nohup python manager.py > ./manager.log 2>&1 &

teardown:
	docker compose -f $(COMPOSE_FILE) down
	- pkill -f manager

stop:
	docker compose -f $(COMPOSE_FILE) down

build:
ifeq ($(LAMDEN_NETWORK),arko)
	export LAMDEN_TAG="v2.0.0" CONTRACTING_TAG="v2.0.0"; \
	docker compose -f $(COMPOSE_FILE) build --no-cache
else ifeq ($(LAMDEN_NETWORK),testnet)
	export LAMDEN_TAG="v2.0.0" CONTRACTING_TAG="v2.0.0"; \
	docker compose -f $(COMPOSE_FILE) build --no-cache
else
	docker compose -f $(COMPOSE_FILE) build --no-cache
endif

deploy: build boot

redeploy: teardown deploy

reboot: teardown boot

enter:
	docker compose -f $(COMPOSE_FILE) exec $(service) bash

clean:
	docker rmi lamden
