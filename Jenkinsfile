pipeline {
    agent {
        kubernetes {
            yaml '''
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: docker
    image: docker:dind
    securityContext:
      privileged: true
    volumeMounts:
    - name: dind-storage
      mountPath: /var/lib/docker
  - name: kubectl
    image: lachlanevenson/k8s-kubectl:latest
    command:
    - cat
    tty: true
  volumes:
  - name: dind-storage
    emptyDir: {}
'''
        }
    }

    environment {
        // This binds the credentials securely. 
        // Jenkins automatically creates DOCKERHUB_CREDS_USR and DOCKERHUB_CREDS_PSW
        DOCKERHUB_CREDS = credentials('dockerhub-credentials')
        IMAGE_NAME = 'santosharron/essential-cloud-app'
        IMAGE_TAG = "${env.BUILD_NUMBER}"
    }

    stages {
        stage('Build & Push') {
            steps {
                container('docker') {
                    // 1. Build the image
                    sh "docker build -t ${IMAGE_NAME}:${IMAGE_TAG} ."
                    
                    // 2. Log in and Push
                    // Note: Single quotes on the outside, double quotes around the shell variables
                    sh 'echo "$DOCKERHUB_CREDS_PSW" | docker login -u "$DOCKERHUB_CREDS_USR" --password-stdin'
                    sh "docker push ${IMAGE_NAME}:${IMAGE_TAG}"
                }
            }
        }

        stage('Deploy') {
            steps {
                container('kubectl') {
                    sh "kubectl apply -f deployment.yaml"
                    sh "kubectl apply -f service.yaml"
                    sh "kubectl set image deployment/essential-cloud-app essential-cloud-app=${IMAGE_NAME}:${IMAGE_TAG}"
                }
            }
        }
    }
}