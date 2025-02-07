V = 0
Q = $(if $(filter 1,$V),,@)

ifeq ($(OS),Windows_NT)
  VENV_PATH_DIR = Scripts
else
  VENV_PATH_DIR = bin
endif


publisher-run:
	$(Q) docker compose -f docker/docker-compose.yaml up --build sensor_publisher sensor_cache

publisher-run-detached:
	$(Q) docker compose -f docker/docker-compose.yaml up --build -d sensor_publisher sensor_cache

publisher-logs:
	$(Q) docker compose -f docker/docker-compose.yaml logs -f

publisher-down:
	$(Q) docker compose -f docker/docker-compose.yaml down

gira-test-run:
	$(Q) docker compose -f docker/docker-compose.yaml up --build gira_test
