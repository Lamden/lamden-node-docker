.PHONY: boot teardown build restart upgrade login-node login-ws login-events clean

boot:
	docker compose -f docker/docker-compose.yml up -d
	@sleep 3
	@nohup python upgrade_manager.py > upgrade-manager.log 2>&1 &
teardown:
	docker compose -f docker/docker-compose.yml down
	- pkill -f upgrade_manager
build:
	docker compose -f docker/docker-compose.yml build --no-cache
reboot:
	docker compose -f docker/docker-compose.yml down
	- pkill -f upgrade_manager
	docker compose -f docker/docker-compose.yml up -d
	@sleep 3
	@nohup python upgrade_manager.py > upgrade-manager.log 2>&1 &
upgrade:
	docker compose -f docker/docker-compose.yml build --no-cache
	docker compose -f docker/docker-compose.yml down
	docker compose -f docker/docker-compose.yml up -d
login-node:
	docker compose -f docker/docker-compose.yml exec node /bin/bash
login-ws:
	docker compose -f docker/docker-compose.yml exec webserver /bin/bash
login-events:
	docker compose -f docker/docker-compose.yml exec events /bin/bash
clean:
	docker compose -f docker/docker-compose.yml down
	docker rmi lamden
