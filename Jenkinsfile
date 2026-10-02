pipeline {
    agent any
    
    environment {
        DOCKER = "C:\\Users\\shree\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker.exe"
        DOCKER_COMPOSE = "C:\\Users\\shree\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker-compose.exe"
        DOCKER_IMAGE = "sit753-devops-app"
        DOCKER_TAG = "${env.BUILD_ID}"
        VERSION_TAG = "v1.0.${env.BUILD_ID}"
        SONAR_PROJECT_KEY = "sit753-devops-app-key"
    }
    
    stages {
        stage('Build') {
            steps {
                echo 'Building Docker Image artefact...'
                bat "${env.DOCKER} build -t ${DOCKER_IMAGE}:${DOCKER_TAG} ."
            }
        }
        
        stage('Test') {
            steps {
                echo 'Running automated PyTest suite inside container...'
                bat "if not exist reports mkdir reports"
                bat "${env.DOCKER} run --rm -v \"%cd%/reports:/app/reports\" ${DOCKER_IMAGE}:${DOCKER_TAG} env PYTHONPATH=. pytest tests/ --junitxml=reports/results.xml"
            }
            post {
                always {
                    junit 'reports/results.xml'
                }
            }
        }
        
        stage('Code Quality') {
            steps {
                echo 'Running SonarQube code quality analysis...'
                bat "sonar-scanner" 
            }
        }
        
        stage('Security') {
            steps {
                echo 'Running security scanning on code and dependencies...'
                bat "bandit -r app.py -f json -o reports/bandit-report.json"
                bat "trivy image --exit-code 1 --severity HIGH,CRITICAL ${DOCKER_IMAGE}:${DOCKER_TAG}"
            }
            post {
                always {
                    archiveArtifacts artifacts: 'reports/bandit-report.json', allowEmptyArchive: true
                }
            }
        }
        
        stage('Deploy') {
            steps {
                echo 'Deploying to staging environment using Docker Compose...'
                bat "${env.DOCKER_COMPOSE} up -d"
            }
        }
        
        stage('Release') {
            steps {
                echo 'Tagging release version and deploying to isolated production environment...'
                bat "${env.DOCKER} tag ${DOCKER_IMAGE}:${DOCKER_TAG} ${DOCKER_IMAGE}:${VERSION_TAG}"
                bat "${env.DOCKER} rm -f sit753-prod-app || exit 0"
                bat "${env.DOCKER} run -d --name sit753-prod-app -p 8080:8000 ${DOCKER_IMAGE}:${VERSION_TAG}"
            }
        }
        
        stage('Monitoring') {
            steps {
                echo 'Verifying live metrics and Prometheus integration...'
                sleep time: 10, unit: 'SECONDS'
                bat "curl -f http://localhost:8000/metrics"
                bat "curl -f http://localhost:8080/metrics"
                bat "curl -f http://localhost:9090/-/healthy"
            }
        }
    }
    
    post {
        always {
            cleanWs()
        }
    }
}
