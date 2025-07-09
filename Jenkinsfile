pipeline {
    agent any

    environment {
        IMAGE_NAME = 'my-streamlit-app'
        CONTAINER_NAME = 'streamlit-app-container'
        APP_PORT = '8501'
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'master', credentialsId: 'sellsavv', url: 'https://github.com/maheevarma/SellSavv.git'
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    sh "docker build -t ${IMAGE_NAME} ."
                }
            }
        }

        stage('Run Container') {
            steps {
                script {
                    // Remove existing container if it exists
                    sh "docker rm -f ${CONTAINER_NAME} || true"
                    
                    // Run new container with port mapping
                    sh "docker run -d -p ${APP_PORT}:${APP_PORT} --name ${CONTAINER_NAME} ${IMAGE_NAME}"
                }
            }
        }
    }

    post {
        success {
            echo "App deployed successfully at http://<your-server-ip>:${APP_PORT}/"
        }
        #this is latest#
        failure {
            echo 'Pipeline failed.'
        }
    }
}
