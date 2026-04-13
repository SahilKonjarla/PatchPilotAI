APP_MODULE=main:app
HOST=127.0.0.1
PORT=8000
PID_FILE=.uvicorn.pid
LOG_FILE=uvicorn.log
UVICORN=uvicorn

.PHONY: help run start stop restart status

help:
	@echo "PatchPilotAI commands:"
	@echo "  make run      Run Uvicorn in the foreground"
	@echo "  make start    Start Uvicorn in the background"
	@echo "  make stop     Stop the background Uvicorn process"
	@echo "  make restart  Restart the background Uvicorn process"
	@echo "  make status   Show background process status"

run:
	$(UVICORN) $(APP_MODULE) --host $(HOST) --port $(PORT) --reload

start:
	@if [ -f $(PID_FILE) ] && kill -0 $$(cat $(PID_FILE)) 2>/dev/null; then \
		echo "Uvicorn is already running with PID $$(cat $(PID_FILE))"; \
	else \
		echo "Starting Uvicorn on http://$(HOST):$(PORT)"; \
		$(UVICORN) $(APP_MODULE) --host $(HOST) --port $(PORT) > $(LOG_FILE) 2>&1 & echo $$! > $(PID_FILE); \
		sleep 1; \
		if kill -0 $$(cat $(PID_FILE)) 2>/dev/null; then \
			echo "Started Uvicorn with PID $$(cat $(PID_FILE))"; \
		else \
			echo "Uvicorn failed to start. See $(LOG_FILE):"; \
			cat $(LOG_FILE); \
			rm -f $(PID_FILE); \
			exit 1; \
		fi; \
	fi

stop:
	@if [ -f $(PID_FILE) ] && kill -0 $$(cat $(PID_FILE)) 2>/dev/null; then \
		echo "Stopping Uvicorn with PID $$(cat $(PID_FILE))"; \
		kill $$(cat $(PID_FILE)); \
		rm -f $(PID_FILE); \
	else \
		echo "Uvicorn is not running"; \
		rm -f $(PID_FILE); \
	fi

restart: stop start

status:
	@if [ -f $(PID_FILE) ] && kill -0 $$(cat $(PID_FILE)) 2>/dev/null; then \
		echo "Uvicorn is running with PID $$(cat $(PID_FILE))"; \
	else \
		echo "Uvicorn is not running"; \
	fi
