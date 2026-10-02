pipeline {
    agent any

    environment {
        PROD_PORT  = '8081'  // Configured to avoid port conflict with Jenkins on 8080
        APP_PORT   = '8000'
        IMAGE_NAME = 'sit753-devops-app'
        DOCKER_TAG = "${BUILD_NUMBER}"
    }

    stages {
        stage('Build') {
            steps {
                echo 'Building Docker image...'
                bat "docker build -t ${IMAGE_NAME}:${DOCKER_TAG} ."
            }
        }
        
        stage('Security Scan') {
            steps {
                echo 'Executing Trivy vulnerability scan...'
                bat "trivy image --exit-code 0 --severity HIGH,CRITICAL ${IMAGE_NAME}:${DOCKER_TAG}"
            }
        }

        stage('Test') {
            steps {
                echo 'Initializing test environment via Docker Compose...'
                bat "docker-compose up -d --build --remove-orphans"
                
                // Add test execution commands here if applicable
                
                echo 'Tearing down test environment...'
                bat "docker-compose down"
            }
        }

        stage('Release') {
            steps {
                echo 'Tagging release version and deploying to production environment...'
                
                bat "docker tag ${IMAGE_NAME}:${DOCKER_TAG} ${IMAGE_NAME}:v1.0.${DOCKER_TAG}"
                bat "docker rm -f sit753-prod-app || exit 0"
                bat "docker run -d --name sit753-prod-app -p ${PROD_PORT}:${APP_PORT} ${IMAGE_NAME}:v1.0.${DOCKER_TAG}"
                
                echo 'Verifying application health...'
                retry(5) {
                    sleep time: 5, unit: 'SECONDS'
                    bat "curl -f http://localhost:${PROD_PORT}/ || exit 1"
                }
            }
        }
    }

    post {
        always {
            echo 'Cleaning up workspace and unused Docker resources...'
            cleanWs()
            bat "docker image prune -f"
        }
        success {
            echo "Pipeline executed successfully. Application running on port ${PROD_PORT}."
        }
        failure {
            echo 'Pipeline execution failed.'
        }
    }
}
