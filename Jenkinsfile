pipeline {
  agent { label 'docker' }
  options { timestamps() }

  environment {
    // Nexus is a container exposed on the host
    NEXUS_REGISTRY = "host.docker.internal:8083"
    DOCKER_CREDS   = "nexus-creds"

    APP_IMAGE   = "cookiejar-api"
    NGINX_IMAGE = "cookiejar-nginx"

    IMAGE_TAG    = "${BUILD_NUMBER}"
    COMPOSE_FILE = "deployment/docker-compose.yml"
    COMPOSE_PROJECT_NAME = "cookiejar-ci-${BUILD_NUMBER}"

    // Nginx is exposed on the host (from compose)
    BASE_URL = "http://host.docker.internal:8080"
  }

  stages {
    stage("Checkout") { steps { checkout scm } }

    stage("Build images") {
      steps {
        sh '''#!/bin/bash
set -euo pipefail
docker build -t ${APP_IMAGE}:${IMAGE_TAG} .
docker build -t ${NGINX_IMAGE}:${IMAGE_TAG} deployment/nginx
'''
      }
    }

    stage("Integration tests (nginx routing, tests from Jenkins)") {
      steps {
        sh '''#!/bin/bash
set -euo pipefail
export IMAGE_TAG=${IMAGE_TAG}
export COMPOSE_PROJECT_NAME=${COMPOSE_PROJECT_NAME}

docker compose --project-directory "$WORKSPACE" -f ${COMPOSE_FILE} up -d

# Wait until nginx answers (better than sleep)
for i in {1..30}; do
  if curl -fsS ${BASE_URL}/version >/dev/null; then
    echo "Nginx is up"
    break
  fi
  sleep 2
done

echo "== Integration tests =="
curl -fsS ${BASE_URL}/health
curl -fsS -X POST ${BASE_URL}/db/populate
curl -fsS ${BASE_URL}/stats

echo "Integration tests PASSED"
'''
      }
      post {
        always {
          sh '''#!/bin/bash
set +e
export COMPOSE_PROJECT_NAME=${COMPOSE_PROJECT_NAME}
docker compose --project-directory "$WORKSPACE" -f ${COMPOSE_FILE} down -v --remove-orphans || true
'''
        }
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
echo "$NEXUS_PASS" | docker login --username "$NEXUS_USER" --password-stdin http://${NEXUS_REGISTRY}

for img in ${APP_IMAGE} ${NGINX_IMAGE}; do
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
