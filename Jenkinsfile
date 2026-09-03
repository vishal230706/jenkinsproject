pipeline {
    agent any

    environment {
        APP_IMAGE = "coworking-booking-app"
        REGISTRY_TAG = "${BUILD_NUMBER}"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Static Analysis & Test') {
            steps {
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                    pytest tests/ --junitxml=test-results.xml
                '''
            }
            post {
                always {
                    junit 'test-results.xml'
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                sh "docker build -t ${APP_IMAGE}:${REGISTRY_TAG} -t ${APP_IMAGE}:latest ."
            }
        }

        stage('Container Scan / Verification') {
            steps {
                sh '''
                    docker run --rm -d --name temp_test_app -p 8000:8000 ${APP_IMAGE}:${REGISTRY_TAG}
                    sleep 5
                    curl --fail http://localhost:8000/health || exit 1
                    docker stop temp_test_app
                '''
            }
        }

        stage('Deploy') {
            steps {
                sh '''
                    docker compose down || true
                    docker compose up -d --build
                '''
            }
        }
    }

    post {
        failure {
            echo "CI/CD Pipeline failed on build ${BUILD_NUMBER}"
        }
        success {
            echo "Deployment completed successfully for build ${BUILD_NUMBER}"
        }
    }
}
