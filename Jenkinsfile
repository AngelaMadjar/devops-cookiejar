pipeline {
  agent { label 'docker' }
  options { timestamps() }

  environment {
    APP_IMAGE     = "cookiejar-api"
    IMAGE_TAG     = "${BUILD_NUMBER}"

    COMPOSE_FILE  = "deployment/docker-compose.yml"
    COMPOSE_PROJECT_NAME = "cookiejar-ci-${BUILD_NUMBER}"

    // Optional if you push later
    NEXUS_REGISTRY = "host.docker.internal:8083"
    DOCKER_CREDS   = "nexus-creds"
  }

  stages {
    stage("Checkout") {
      steps { checkout scm }
    }

    stage("Build image") {
      steps {
        sh '''#!/bin/bash
set -euo pipefail
docker build -t ${APP_IMAGE}:${IMAGE_TAG} .
'''
      }
    }

    stage("Integration tests (compose network)") {
      steps {
        sh '''#!/bin/bash
set -euo pipefail

export IMAGE_TAG="${IMAGE_TAG}"
export COMPOSE_PROJECT_NAME="${COMPOSE_PROJECT_NAME}"

# Bring up stack (db + app)
docker compose --project-directory "$WORKSPACE" -f "${COMPOSE_FILE}" up -d

# Compute the actual compose network name (project + network)
NET="${COMPOSE_PROJECT_NAME}_cookiejar-net"

echo "Using network: $NET"
docker network inspect "$NET" >/dev/null

echo "== Wait for app health =="
# Wait for the app to respond on its internal port from inside the compose network
for i in {1..60}; do
  if docker run --rm --network "$NET" curlimages/curl:8.6.0 -fsS "http://app:8080/health" >/dev/null; then
    echo "App is up"
    break
  fi

  # Helpful debug every 10 tries
  if (( i % 10 == 0 )); then
    echo "Still waiting... (try $i)"
    docker compose --project-directory "$WORKSPACE" -f "${COMPOSE_FILE}" ps || true
    docker compose --project-directory "$WORKSPACE" -f "${COMPOSE_FILE}" logs --tail=80 app || true
  fi

  sleep 2
done

# Fail hard if it never came up
docker run --rm --network "$NET" curlimages/curl:8.6.0 -fsS "http://app:8080/health" >/dev/null

echo "== Integration tests =="
docker run --rm --network "$NET" curlimages/curl:8.6.0 -fsS "http://app:8080/health"
docker run --rm --network "$NET" curlimages/curl:8.6.0 -fsS -X POST "http://app:8080/db/populate"
docker run --rm --network "$NET" curlimages/curl:8.6.0 -fsS "http://app:8080/stats"

echo "Integration tests PASSED"
'''
      }
      post {
        always {
          sh '''#!/bin/bash
set +e
export COMPOSE_PROJECT_NAME="${COMPOSE_PROJECT_NAME}"
docker compose --project-directory "$WORKSPACE" -f "${COMPOSE_FILE}" down -v --remove-orphans || true
'''
        }
      }
    }

    // Optional push stage — keep/remove as needed
    stage("Push image to Nexus (optional)") {
      when { expression { return env.DOCKER_CREDS?.trim() } }
      steps {
        withCredentials([usernamePassword(
          credentialsId: DOCKER_CREDS,
          usernameVariable: "NEXUS_USER",
          passwordVariable: "NEXUS_PASS"
        )]) {
          sh '''#!/bin/bash
set -euo pipefail

echo "$NEXUS_PASS" | docker login \
  --username "$NEXUS_USER" \
  --password-stdin \
  "http://${NEXUS_REGISTRY}"

docker tag "${APP_IMAGE}:${IMAGE_TAG}" "${NEXUS_REGISTRY}/${APP_IMAGE}:${IMAGE_TAG}"
docker push "${NEXUS_REGISTRY}/${APP_IMAGE}:${IMAGE_TAG}"
'''
        }
      }
    }
  }

  post {
    always {
      sh '''#!/bin/bash
set +e
docker logout "${NEXUS_REGISTRY}" || true
'''
    }
  }
}
