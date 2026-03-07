include versions.env

build:
	docker build \
		--build-arg RUNNER_VERSION=$(RUNNER_VERSION) \
		--build-arg RUNNER_CONTAINER_HOOKS_VERSION=$(RUNNER_CONTAINER_HOOKS_VERSION) \
		-t runner .
