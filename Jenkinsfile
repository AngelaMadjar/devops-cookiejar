pipeline {
  agent { label 'docker' }

  options { timestamps() }

  environment {
    // IMPORTANT: use a host-reachable name because the docker CLI talks to the host daemon via /var/run/docker.sock
    // and the host daemon cannot resolve container-only DNS names like "nexus" on ci-net.
    NEXUS_REGISTRY = "host.docker.internal:8083"
    DOCKER_CREDS   = "nexus-creds"

    APP_IMAGE   = "cookiejar-api"
    NGINX_IMAGE = "cookiejar-nginx"
    SMOKE_IMAGE = "cookiejar-smoke"

    IMAGE_TAG    = "${BUILD_NUMBER}"
    COMPOSE_FILE = "deployment/docker-compose.yml"
    COMPOSE_PROJECT_NAME = "cookiejar-ci-${BUILD_NUMBER}"
  }

  stages {

    stage("Checkout") {
      steps { checkout scm }
    }

    stage("Build app images") {
      steps {
        sh '''#!/bin/bash
set -euo pipefail
docker build -t ${APP_IMAGE}:${IMAGE_TAG} .
docker tag ${APP_IMAGE}:${IMAGE_TAG} ${APP_IMAGE}:blue
docker tag ${APP_IMAGE}:${IMAGE_TAG} ${APP_IMAGE}:green
'''
      }
    }

    stage("Build infra images") {
      steps {
        sh '''#!/bin/bash
set -euo pipefail
docker build -t ${NGINX_IMAGE}:${IMAGE_TAG} deployment/nginx
docker build -t ${SMOKE_IMAGE}:${IMAGE_TAG} deployment/smoke
'''
      }
    }

    stage("Integration tests (docker compose)") {
      steps {
        sh '''#!/bin/bash
set -euo pipefail
export COMPOSE_PROJECT_NAME=${COMPOSE_PROJECT_NAME}

docker compose --project-directory "$WORKSPACE" \
  -f ${COMPOSE_FILE} up -d

docker compose --project-directory "$WORKSPACE" \
  -f ${COMPOSE_FILE} run --rm smoke
'''
      }
      post {
        always {
          sh '''#!/bin/bash
set +e
export COMPOSE_PROJECT_NAME=${COMPOSE_PROJECT_NAME}
docker compose --project-directory "$WORKSPACE" \
  -f ${COMPOSE_FILE} down -v --remove-orphans || true
'''
        }
      }
    }

    // Optional but recommended while you're validating the setup
    stage("Debug Nexus Docker endpoint") {
      steps {
        sh '''#!/bin/bash
set -euo pipefail
echo "== DNS inside agent container =="
getent hosts nexus || true
echo "== Nexus Docker endpoint from agent (host-exposed) =="
curl -i http://${NEXUS_REGISTRY}/v2/ || true
'''
      }
    }

    stage("Push images to Nexus") {
      steps {
        withCredentials([usernamePassword(
          credentialsId: DOCKER_CREDS,
          usernameVariable: "NEXUS_USER",
          passwordVariable: "NEXUS_PASS"
        )]) {
          sh '''#!/bin/bash
set -euo pipefail

# Explicit http:// avoids client confusion with insecure registries
echo "$NEXUS_PASS" | docker login --username "$NEXUS_USER" --password-stdin http://${NEXUS_REGISTRY}

for img in ${APP_IMAGE} ${NGINX_IMAGE} ${SMOKE_IMAGE}; do
  docker tag $img:${IMAGE_TAG} ${NEXUS_REGISTRY}/$img:${IMAGE_TAG}
  docker push ${NEXUS_REGISTRY}/$img:${IMAGE_TAG}
done
'''
        }
      }
    }
  }

  post {
    always {
      sh '''#!/bin/bash
set +e
docker logout ${NEXUS_REGISTRY} || true
'''
    }
  }
}