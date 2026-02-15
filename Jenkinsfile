pipeline {
  agent { label 'docker' }

  options {
    timestamps()
  }

  environment {
    // Nexus Docker registry (host-exposed)
    NEXUS_REGISTRY = "host.docker.internal:8083"
    DOCKER_CREDS   = "nexus-creds"

    APP_IMAGE     = "cookiejar-api"
    NGINX_IMAGE = "cookiejar-nginx" // Homework 4
    SMOKE_IMAGE = "cookiejar-smoke" // Homework 4

    IMAGE_TAG     = "${BUILD_NUMBER}"

    COMPOSE_FILE  = "deployment/docker-compose.yml"
    COMPOSE_PROJECT_NAME = "cookiejar-ci-${BUILD_NUMBER}"
  }

  stages {

    stage("Checkout") {
      steps {
        checkout scm
      }
    }

    stage("Build Docker image") { // Homework 4: building nginx image as well
      steps {
        sh '''#!/bin/bash
set -euo pipefail
docker build -t ${APP_IMAGE}:${IMAGE_TAG} .
docker build -t ${NGINX_IMAGE}:${IMAGE_TAG} deployment/nginx
docker build -t ${SMOKE_IMAGE}:${IMAGE_TAG} deployment/smoke 

'''
      }
    }

stage("Integration tests (smoke container)") {
  steps {
    sh '''#!/bin/bash
set -euo pipefail

export IMAGE_TAG=${IMAGE_TAG}
export COMPOSE_PROJECT_NAME=${COMPOSE_PROJECT_NAME}

# Start dependencies
docker compose -f ${COMPOSE_FILE} up -d db migrate app nginx

# Run smoke tests as a one-off container.
# --exit-code-from makes compose return the smoke container exit code.
docker compose -f ${COMPOSE_FILE} up --no-deps --abort-on-container-exit --exit-code-from smoke smoke
'''
  }
  post {
    always {
      sh '''#!/bin/bash
set +e
export COMPOSE_PROJECT_NAME=${COMPOSE_PROJECT_NAME}
docker compose -f ${COMPOSE_FILE} down -v --remove-orphans || true
'''
    }
  }
}



    stage("Push image to Nexus") {
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
  http://${NEXUS_REGISTRY}

docker tag ${APP_IMAGE}:${IMAGE_TAG} \
  ${NEXUS_REGISTRY}/${APP_IMAGE}:${IMAGE_TAG}

docker push ${NEXUS_REGISTRY}/${APP_IMAGE}:${IMAGE_TAG}
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
