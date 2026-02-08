pipeline {
  agent { label 'docker' }

  options { timestamps() }

  environment {
    NEXUS_REGISTRY = "nexus:8083"
    NEXUS_REPO     = "docker-hosted"  
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
        sh '''
          set -e
          docker build -t ${APP_IMAGE}:${IMAGE_TAG} .
          docker tag ${APP_IMAGE}:${IMAGE_TAG} ${APP_IMAGE}:blue
          docker tag ${APP_IMAGE}:${IMAGE_TAG} ${APP_IMAGE}:green
        '''
      }
    }

    stage("Build infra images") {
      steps {
        sh '''
          set -e
          docker build -t ${NGINX_IMAGE}:${IMAGE_TAG} deployment/nginx
          docker build -t ${SMOKE_IMAGE}:${IMAGE_TAG} deployment/smoke
        '''
      }
    }

    stage("Integration tests (docker compose)") {
      steps {
        sh '''
          set -e
          export COMPOSE_PROJECT_NAME=${COMPOSE_PROJECT_NAME}

          docker compose --project-directory "$WORKSPACE" \
            -f ${COMPOSE_FILE} up -d

          docker compose --project-directory "$WORKSPACE" \
            -f ${COMPOSE_FILE} run --rm smoke
        '''
      }
      post {
        always {
          sh '''
            export COMPOSE_PROJECT_NAME=${COMPOSE_PROJECT_NAME}
            docker compose --project-directory "$WORKSPACE" \
              -f ${COMPOSE_FILE} down -v --remove-orphans || true
          '''
        }
      }
    }
    stage("Debug Docker /v2") {
      steps {
        withCredentials([usernamePassword(
          credentialsId: DOCKER_CREDS,
          usernameVariable: "NEXUS_USER",
          passwordVariable: "NEXUS_PASS"
        )]) {
          sh(label: 'debug-v2', script: """#!/bin/bash
            set -euxo pipefail

            echo "== DNS =="
            getent hosts nexus || true

            echo "== Curl /v2 (no auth) =="
            curl -i http://nexus:8083/v2/ || true

            echo "== Curl /v2 (basic auth) =="
            curl -i -u "$NEXUS_USER:$NEXUS_PASS" http://nexus:8083/v2/ || true
            """)
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
          sh '''
            set -e

            echo "$NEXUS_PASS" | docker login ${NEXUS_REGISTRY} \
              -u "$NEXUS_USER" --password-stdin

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
      sh 'docker logout ${NEXUS_REGISTRY} || true'
    }
  }
}
