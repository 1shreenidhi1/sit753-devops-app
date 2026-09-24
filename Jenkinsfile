pipeline {
    agent any
    
    environment {
        DOCKER_IMAGE = "sit753-devops-app"
        DOCKER_TAG = "${env.BUILD_ID}"
        SONAR_PROJECT_KEY = "sit753-devops-app-key"
    }
    
    stages {
        stage('Build') {
            steps {
                echo 'Building Docker Image artefact...'
                // Using double quotes so Groovy injects the variables correctly
                bat "docker build -t ${DOCKER_IMAGE}:${DOCKER_TAG} ."
            }
        }
        
        stage('Test') {
            steps {
                echo 'Running automated PyTest suite inside container...'
                bat "docker run --rm ${DOCKER_IMAGE}:${DOCKER_TAG} env PYTHONPATH=. pytest tests/ --junitxml=reports/results.xml"
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
                bat "trivy image --severity HIGH,CRITICAL ${DOCKER_IMAGE}:${DOCKER_TAG}"
            }
        }
        
        stage('Deploy') {
            steps {
                echo 'Deploying to staging environment using Docker Compose...'
                bat "docker-compose up -d"
            }
        }
        
        stage('Release') {
            steps {
                echo 'Promoting build to production release tag...'
                bat "docker tag ${DOCKER_IMAGE}:${DOCKER_TAG} ${DOCKER_IMAGE}:latest"
            }
        }
        
        stage('Monitoring') {
            steps {
                echo 'Verifying monitoring endpoints and health metrics...'
                bat "curl -f http://localhost:8000/metrics || exit /b 1"
            }
        }
    }
    
    post {
        always {
            cleanWs()
        }
    }
}
