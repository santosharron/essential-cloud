pipeline {
    agent any // This tells Jenkins to run on any available server space

    environment {
        // Variables you will use in the pipeline
        DOCKERHUB_CREDENTIALS = 'dockerhub-credentials' // We will set this up in Jenkins later
        IMAGE_NAME = 'santosharron/essential-cloud-app' // REPLACE with your username
        IMAGE_TAG = "${env.BUILD_NUMBER}" // Tags the image with the Jenkins build number
    }

    stages {
        stage('Clone Repository') {
            steps {
                // This step pulls your latest code from GitHub
                checkout scm 
            }
        }

        stage('Build Docker Image') {
            steps {
                // Tells Docker to build the image using your Dockerfile
                sh "docker build -t ${IMAGE_NAME}:${IMAGE_TAG} -t ${IMAGE_NAME}:latest ."
            }
        }

        stage('Push to Docker Hub') {
            steps {
                // Logs into Docker Hub and pushes your newly built image
                withCredentials([usernamePassword(credentialsId: env.DOCKERHUB_CREDENTIALS, passwordVariable: 'DOCKERHUB_PASS', usernameVariable: 'DOCKERHUB_USER')]) {
                    sh "echo \$DOCKERHUB_PASS | docker login -u \$DOCKERHUB_USER --password-stdin"
                    sh "docker push ${IMAGE_NAME}:${IMAGE_TAG}"
                    sh "docker push ${IMAGE_NAME}:latest"
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                // Uses your YAML files to tell Kubernetes to run the new image
                sh "kubectl apply -f deployment.yaml"
                sh "kubectl apply -f service.yaml"
                
                // Forces Kubernetes to use the brand new image we just pushed
                sh "kubectl set image deployment/essential-cloud-app essential-cloud-app=${IMAGE_NAME}:${IMAGE_TAG}"
            }
        }
    }
}