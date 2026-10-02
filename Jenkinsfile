pipeline {
    agent any

    environment {
        PROD_PORT  = '8081'  // Avoids host port conflict on 8080
        APP_PORT   = '8000'
        IMAGE_NAME = 'sit753-devops-app'
        DOCKER_TAG = "${BUILD_NUMBER}"
        
        // Explicit path definitions for binaries to resolve service account path issues
        DOCKER_BIN    = 'C:\\Users\\shree\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker.exe'
        COMPOSE_BIN   = 'C:\\Users\\shree\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker-compose.exe'
        TRIVY_BIN     = 'C:\\Users\\shree\\AppData\\Local\\Microsoft\\WinGet\\Packages\\AquaSecurity.Trivy_Microsoft.Winget.Source_8wekyb3d8bbwe\\trivy.exe'
    }

    stages {
        stage('Code Quality (SonarQube)') {
            steps {
                echo 'Running SonarQube static code analysis...'
                script {
                    // Dynamically fetches the tool path configured in Jenkins Global Tool Configuration
                    def scannerHome = tool 'sonar-scanner'
                    bat "${scannerHome}\\bin\\sonar-scanner.bat"
                }
            }
        }

        stage('Security Scan (Bandit)') {
            steps {
                echo 'Running Bandit Python security linter...'
                // Scans Python files for vulnerabilities and insecure coding patterns
                bat "bandit -r . -ll -ii"
            }
        }

        stage('Build') {
            steps {
                echo 'Building Docker image...'
                bat "${env.DOCKER_BIN} build -t ${IMAGE_NAME}:${DOCKER_TAG} ."
            }
        }
        
        stage('Container Vulnerability Scan (Trivy)') {
            steps {
                echo 'Executing Trivy vulnerability scan...'
                // Enforces failure on High/Critical vulnerabilities (--exit-code 1)
                bat "${env.TRIVY_BIN} image --exit-code 1 --severity HIGH,CRITICAL ${IMAGE_NAME}:${DOCKER_TAG}"
            }
        }

        stage('Test') {
            steps {
                echo 'Initializing test environment via Docker Compose...'
                // Passes the unique build tag so compose validates the exact built artifact
                bat "set TAG=${DOCKER_TAG} && ${env.COMPOSE_BIN} up -d --build --remove-orphans"
                
                echo 'Running automated tests inside container...'
                bat "set TAG=${DOCKER_TAG} && ${env.COMPOSE_BIN} exec -T test-app pytest"

                echo 'Tearing down test environment...'
                bat "set TAG=${DOCKER_TAG} && ${env.COMPOSE_BIN} down"
            }
        }

        stage('Release') {
            steps {
                echo 'Tagging release version and deploying to production environment...'
                
                bat "${env.DOCKER_BIN} tag ${IMAGE_NAME}:${DOCKER_TAG} ${IMAGE_NAME}:v1.0.${DOCKER_TAG}"
                bat "${env.DOCKER_BIN} rm -f sit753-prod-app || exit 0"
                
                // Deploy versioned container artifact to the designated production port
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
            echo 'Pipeline execution failed due to quality or security gate violations.'
        }
    }
}
