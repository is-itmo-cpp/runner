# This is our version of the official GitHub runner image. See the original:
# https://github.com/actions/runner/blob/8b65f5f9df6fd04c493f9350d90eba55eb53005f/images/Dockerfile
#
# Some things are stripped down, some are added. Here are the main differences:
#
# 1. We use Debian Noble instead of Jammy (for newer packages).
# 2. No docker-in-docker.
# 3. No sudo.
# 4. CMake, build-essential, clang-19, gtest, and gcovr come preinstalled.
# 5. Some python packages we need for generating the report are preinstalled too.

FROM mcr.microsoft.com/dotnet/runtime-deps:8.0-noble AS build

ARG RUNNER_VERSION
ARG RUNNER_CONTAINER_HOOKS_VERSION

ARG TARGETOS=linux
ARG TARGETARCH=amd64

RUN apt update -y && apt install curl unzip -y

WORKDIR /actions-runner
RUN test -n "${RUNNER_VERSION}" || (echo "RUNNER_VERSION is required" && false) \
    && export RUNNER_ARCH=${TARGETARCH} \
    && if [ "$RUNNER_ARCH" = "amd64" ]; then export RUNNER_ARCH=x64 ; fi \
    && curl -f -L -o runner.tar.gz https://github.com/actions/runner/releases/download/v${RUNNER_VERSION}/actions-runner-${TARGETOS}-${RUNNER_ARCH}-${RUNNER_VERSION}.tar.gz \
    && tar xzf ./runner.tar.gz \
    && rm runner.tar.gz

RUN test -n "${RUNNER_CONTAINER_HOOKS_VERSION}" || (echo "RUNNER_CONTAINER_HOOKS_VERSION is required" && false) \
    && curl -f -L -o runner-container-hooks.zip https://github.com/actions/runner-container-hooks/releases/download/v${RUNNER_CONTAINER_HOOKS_VERSION}/actions-runner-hooks-k8s-${RUNNER_CONTAINER_HOOKS_VERSION}.zip \
    && unzip ./runner-container-hooks.zip -d ./k8s \
    && rm runner-container-hooks.zip


FROM mcr.microsoft.com/dotnet/runtime-deps:8.0-noble

ENV DEBIAN_FRONTEND=noninteractive
ENV RUNNER_MANUALLY_TRAP_SIG=1
ENV ACTIONS_RUNNER_PRINT_LOG_TO_STDOUT=1
ENV ImageOS=ubuntu24

RUN apt update -y \
    && apt install -y adduser \
        cmake build-essential clang-19 clang-tidy-19 libgtest-dev libgmock-dev gcovr \
        nodejs python3 python3-pip python3-tabulate python3-wcwidth \
        git jq curl

COPY ./gha-helper /tmp/gha-helper
RUN pip install --no-cache-dir --break-system-packages /tmp/gha-helper \
    && rm -rf /tmp/gha-helper

RUN adduser --disabled-password --gecos "" --uid 1001 runner

WORKDIR /home/runner

COPY --chown=nobody:nobody --from=build /actions-runner .

USER runner
