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
                sh 'docker build -t ${DOCKER_IMAGE}:${DOCKER_TAG} .'
            }
        }
        
        stage('Test') {
            steps {
                echo 'Running automated PyTest suite inside container...'
                sh 'docker run --rm ${DOCKER_IMAGE}:${DOCKER_TAG} pytest tests/ --junitxml=reports/results.xml'
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
                // Analyzes maintainability, style, and code smells
                withSonarQubeEnv('SonarQube') {
                    sh 'sonar-scanner -Dsonar.projectKey=${SONAR_PROJECT_KEY} -Dsonar.sources=app.py'
                }
            }
        }
        
        stage('Security') {
            steps {
                echo 'Running security scanning on code and dependencies...'
                sh 'bandit -r app.py -f json -o reports/bandit-report.json || true'
                sh 'trivy image --severity HIGH,CRITICAL ${DOCKER_IMAGE}:${DOCKER_TAG}'
            }
        }
        
        stage('Deploy') {
            steps {
                echo 'Deploying to staging environment using Docker Compose...'
                sh 'docker-compose up -d'
            }
        }
        
        stage('Release') {
            steps {
                echo 'Promoting build to production release tag...'
                sh 'docker tag ${DOCKER_IMAGE}:${DOCKER_TAG} ${DOCKER_IMAGE}:latest'
            }
        }
        
        stage('Monitoring') {
            steps {
                echo 'Verifying monitoring endpoints and health metrics...'
                // Pings the metrics route we built in app.py to ensure the monitoring tool can track it
                sh 'curl -f http://localhost:8000/metrics || exit 1'
            }
        }
    }
    
    post {
        always {
            cleanWs()
        }
    }
}
