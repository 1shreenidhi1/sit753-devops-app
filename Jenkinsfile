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
                bat "${env.DOCKER} run --rm -v \"${env.WORKSPACE}/reports:/app/reports\" ${DOCKER_IMAGE}:${DOCKER_TAG} env PYTHONPATH=. pytest tests/ --junitxml=reports/results.xml"
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
                // Uses -Dsonar.login for SonarQube v9.9 LTS authentication
                catchError(buildResult: 'SUCCESS', stageResult: 'UNSTABLE') {
                    bat "${env.DOCKER} run --rm -v \"${env.WORKSPACE}:/usr/src\" sonarsource/sonar-scanner-cli -Dsonar.projectKey=${SONAR_PROJECT_KEY} -Dsonar.sources=. -Dsonar.host.url=http://host.docker.internal:9000 -Dsonar.login=sqp_1139504258e8d9aa887c392e66ea83b66d551fc6"
                }
            }
        }
        
        stage('Security') {
            steps {
                echo 'Running security scanning on code and dependencies...'
                bat "if not exist reports mkdir reports"
                
                // Bandit code vulnerability scan
                catchError(buildResult: 'SUCCESS', stageResult: 'UNSTABLE') {
                    bat "${env.DOCKER} run --rm -v \"${env.WORKSPACE}/reports:/app/reports\" ${DOCKER_IMAGE}:${DOCKER_TAG} python -m bandit -r app.py -f json -o reports/bandit-report.json"
                }
                
                // Trivy container image vulnerability scan
                catchError(buildResult: 'SUCCESS', stageResult: 'UNSTABLE') {
                    bat "${env.DOCKER} save ${DOCKER_IMAGE}:${DOCKER_TAG} -o reports/image.tar"
                    bat "${env.DOCKER} run --rm -v \"${env.WORKSPACE}/reports:/reports\" aquasec/trivy:latest image --input /reports/image.tar --severity HIGH,CRITICAL"
                }
            }
            post {
                always {
                    archiveArtifacts artifacts: 'reports/bandit-report.json', allowEmptyArchive: true
                }
            }
        }
        
        stage('Deploy') {
            steps {
                echo 'Deploying staging environment with Docker Compose using built artefact...'
                // Added --remove-orphans to clear port 8000 conflicts automatically
                bat "set DOCKER_TAG=${DOCKER_TAG}&& ${env.DOCKER_COMPOSE} up -d --remove-orphans"
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
