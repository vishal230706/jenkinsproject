pipeline {
    agent any

    environment {
        APP_NAME        = 'coworking-booking-app'
        DOCKER_IMAGE    = "myrepo/${APP_NAME}"
        DEPLOY_PORT     = '8000'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Unit Tests') {
            steps {
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                    pytest tests/
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    sh "docker build -t ${DOCKER_IMAGE}:${BUILD_NUMBER} -t ${DOCKER_IMAGE}:latest ."
                }
            }
        }

        // Optional: Uncomment if pushing to DockerHub / private registry
        /*
        stage('Push to Registry') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'docker-registry-creds', passwordVariable: 'DOCKER_PASS', usernameVariable: 'DOCKER_USER')]) {
                    sh '''
                        echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin
                        docker push ${DOCKER_IMAGE}:${BUILD_NUMBER}
                        docker push ${DOCKER_IMAGE}:latest
                    '''
                }
            }
        }
        */

        stage('Deploy') {
            steps {
                sh """
                    # Stop and remove existing container if running
                    docker stop ${APP_NAME} || true
                    docker rm ${APP_NAME} || true

                    # Run new container
                    docker run -d \
                        --name ${APP_NAME} \
                        -p ${DEPLOY_PORT}:8000 \
                        --restart always \
                        ${DOCKER_IMAGE}:${BUILD_NUMBER}
                """
            }
        }
    }

    post {
        always {
            sh "rm -rf venv"
        }
        success {
            echo "Pipeline deployed successfully to http://localhost:${DEPLOY_PORT}/docs"
        }
        failure {
            echo "Pipeline failed. Review build logs."
        }
    }
}
