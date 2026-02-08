pipeline {
  agent { label 'docker' }

  options {
    timestamps()
    skipDefaultCheckout(true)
  }

  environment {
    NEXUS_DOCKER_REGISTRY = "nexus:8083"
    DOCKER_CREDS_ID       = "nexus-creds"
    IMAGE_REPO            = "cookiejar-api"

    COMPOSE_FILE          = "deployment/docker-compose.yml"
    COMPOSE_PROJECT_NAME  = "cookiejar-ci-${BUILD_NUMBER}"
    IMAGE_TAG             = "${BUILD_NUMBER}"
  }

  stages {
    stage("Checkout") {
      steps { checkout scm }
    }

    stage("Build image") {
      steps {
        sh '''
          set -e
          docker build -t ${IMAGE_REPO}:${IMAGE_TAG} -f dockerfile .
          docker tag ${IMAGE_REPO}:${IMAGE_TAG} ${IMAGE_REPO}:blue
          docker tag ${IMAGE_REPO}:${IMAGE_TAG} ${IMAGE_REPO}:green
        '''
      }
    }

    stage("Integration tests (compose + smoke)") {
    steps {
        sh '''
        set -e
        export COMPOSE_PROJECT_NAME=${COMPOSE_PROJECT_NAME}

        # Map container workspace -> macOS host workspace
        export HOST_WORKSPACE="$WORKSPACE"
        export HOST_WORKSPACE="${HOST_WORKSPACE#/home/jenkins/agent}"
        export HOST_WORKSPACE="/Users/angela.madjar/Angela/Finki-Masters/DevOps/Homework-2/jenkins-agent${HOST_WORKSPACE}"

        echo "WORKSPACE=$WORKSPACE"
        echo "HOST_WORKSPACE=$HOST_WORKSPACE"
        ls -la "$HOST_WORKSPACE/deployment/nginx/default.conf"
        ls -la "$HOST_WORKSPACE/deployment/smoke.sh"

        docker compose -f ${COMPOSE_FILE} up -d
        docker compose -f ${COMPOSE_FILE} run --rm smoke
        '''
    }
    post {
        always {
        sh '''
            export COMPOSE_PROJECT_NAME=${COMPOSE_PROJECT_NAME}

            export HOST_WORKSPACE="$WORKSPACE"
            export HOST_WORKSPACE="${HOST_WORKSPACE#/home/jenkins/agent}"
            export HOST_WORKSPACE="/Users/angela.madjar/Angela/Finki-Masters/DevOps/Homework-2/jenkins-agent${HOST_WORKSPACE}"

            docker compose -f ${COMPOSE_FILE} down -v --remove-orphans || true
        '''
        }
    }
    }
    stage("Publish image to Nexus") {
      steps {
        withCredentials([usernamePassword(
          credentialsId: "${DOCKER_CREDS_ID}",
          usernameVariable: "NEXUS_USER",
          passwordVariable: "NEXUS_PASS"
        )]) {
          sh '''
            set -e
            echo "$NEXUS_PASS" | docker login ${NEXUS_DOCKER_REGISTRY} -u "$NEXUS_USER" --password-stdin

            docker tag ${IMAGE_REPO}:${IMAGE_TAG} ${NEXUS_DOCKER_REGISTRY}/${IMAGE_REPO}:${IMAGE_TAG}
            docker push ${NEXUS_DOCKER_REGISTRY}/${IMAGE_REPO}:${IMAGE_TAG}

            docker tag ${IMAGE_REPO}:${IMAGE_TAG} ${NEXUS_DOCKER_REGISTRY}/${IMAGE_REPO}:latest
            docker push ${NEXUS_DOCKER_REGISTRY}/${IMAGE_REPO}:latest
          '''
        }
      }
    }
  }

  post {
    always {
      sh 'docker logout ${NEXUS_DOCKER_REGISTRY} || true'
    }
  }
}
