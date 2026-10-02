pipeline {
    agent any

    environment {
        PROD_PORT  = '8081'  // Avoids host port conflict on 8080
        APP_PORT   = '8000'
        IMAGE_NAME = 'sit753-devops-app'
        DOCKER_TAG = "${BUILD_NUMBER}"
        
        // Explicit path definitions for binaries to resolve service account path issues
        DOCKER_BIN  = 'C:\\Users\\shree\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker.exe'
        COMPOSE_BIN = 'C:\\Users\\shree\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker-compose.exe'
        TRIVY_BIN   = 'C:\\Users\\shree\\AppData\\Local\\Microsoft\\WinGet\\Packages\\AquaSecurity.Trivy_Microsoft.Winget.Source_8wekyb3d8bbwe\\trivy.exe'
    }

    stages {
        stage('Build') {
            steps {
                echo 'Building Docker image...'
                bat "${env.DOCKER_BIN} build -t ${IMAGE_NAME}:${DOCKER_TAG} ."
            }
        }
        
        stage('Security Scan') {
            steps {
                echo 'Executing Trivy vulnerability scan...'
                bat "${env.TRIVY_BIN} image --exit-code 0 --severity HIGH,CRITICAL ${IMAGE_NAME}:${DOCKER_TAG}"
            }
        }

        stage('Test') {
            steps {
                echo 'Initializing test environment via Docker Compose...'
                bat "${env.COMPOSE_BIN} up -d --build --remove-orphans"
                
                echo 'Tearing down test environment...'
                bat "${env.COMPOSE_BIN} down"
            }
        }

        stage('Release') {
            steps {
                echo 'Tagging release version and deploying to production environment...'
                
                bat "${env.DOCKER_BIN} tag ${IMAGE_NAME}:${DOCKER_TAG} ${IMAGE_NAME}:v1.0.${DOCKER_TAG}"
                bat "${env.DOCKER_BIN} rm -f sit753-prod-app || exit 0"
                
                // Uses PROD_PORT '8081' to prevent socket bind collisions
                bat "${env.DOCKER_BIN} run -d --name sit753-prod-app -p ${PROD_PORT}:${APP_PORT} ${IMAGE_NAME}:v1.0.${DOCKER_TAG}"
                
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
            bat "${env.DOCKER_BIN} image prune -f"
        }
        success {
            echo "Pipeline executed successfully. Application running on port ${PROD_PORT}."
        }
        failure {
            echo 'Pipeline execution failed.'
        }
    }
}
