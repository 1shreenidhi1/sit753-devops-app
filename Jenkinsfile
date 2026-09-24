pipeline {
    agent any
    
    environment {
        DOCKER_IMAGE = "sit753-devops-app"
        DOCKER_TAG = "${env.BUILD_ID}"
        SONAR_PROJECT_KEY = "sit753-devops-app-key"
        // Explicit absolute path to Docker executable to bypass Windows service PATH restrictions
        DOCKER_PATH = "C:\\Program Files\\Docker\\Docker\\resources\\bin\\docker.exe"
    }
    
    stages {
        stage('Build') {
            steps {
                echo 'Building Docker Image artefact...'
                bat "\"%DOCKER_PATH%\" build -t ${DOCKER_IMAGE}:${DOCKER_TAG} ."
            }
        }
        
        stage('Test') {
            steps {
                echo 'Running automated PyTest suite inside container...'
                bat "\"%DOCKER_PATH%\" run --rm ${DOCKER_IMAGE}:${DOCKER_TAG} pytest tests/ --junitxml=reports/results.xml"
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
                withSonarQubeEnv('SonarQube') {
                    bat "sonar-scanner -Dsonar.projectKey=${SONAR_PROJECT_KEY} -Dsonar.sources=app.py"
                }
            }
        }
        
        stage('Security') {
            steps {
                echo 'Running security scanning on code and dependencies...'
                bat "bandit -r app.py -f json -o reports/bandit-report.json || exit 0"
                bat "\"%DOCKER_PATH%\" image --severity HIGH,CRITICAL ${DOCKER_IMAGE}:${DOCKER_TAG}"
            }
        }
        
        stage('Deploy') {
            steps {
                echo 'Deploying to staging environment using Docker Compose...'
                bat 'docker-compose up -d'
            }
        }
        
        stage('Release') {
            steps {
                echo 'Promoting build to production release tag...'
                bat "\"%DOCKER_PATH%\" tag ${DOCKER_IMAGE}:${DOCKER_TAG} ${DOCKER_IMAGE}:latest"
            }
        }
        
        stage('Monitoring') {
            steps {
                echo 'Verifying monitoring endpoints and health metrics...'
                bat 'curl -f http://localhost:8000/metrics || exit /b 1'
            }
        }
    }
    
    post {
        always {
            cleanWs()
        }
    }
}
