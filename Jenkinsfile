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
        IMAGE_NAME = 'santoshvp/essential-cloud-app'
        IMAGE_TAG = "${env.BUILD_NUMBER}"
    }

    stages {
        stage('Build & Push') {
            steps {
                container('docker') {
                    // 1. Build the image
                    sh "docker build -t ${IMAGE_NAME}:${IMAGE_TAG} ."
                    
                    // 2. Log in and Push
                    // 👇 REPLACE your old withCredentials block with this one 👇
                    withCredentials([usernamePassword(credentialsId: 'dockerhub-credentials', passwordVariable: 'DOCKERHUB_PASS', usernameVariable: 'DOCKERHUB_USER')]) {
                        
                        sh 'echo "$DOCKERHUB_PASS" | docker login -u "$DOCKERHUB_USER" --password-stdin'
                        sh "docker push ${IMAGE_NAME}:${IMAGE_TAG}"
                        
                    }
                    // 👆 -------------------------------------------------------- 👆
                }
            }
        }

        stage('Deploy') {
            steps {
                container('kubectl') {
                    sh "kubectl apply -f deployment.yaml"
                    sh "kubectl apply -f service.yaml"
                    sh "kubectl set image deployment/simple-app-deployment web-container=${IMAGE_NAME}:${IMAGE_TAG}"
                }
            }
        }

        // 👇 THIS IS THE NEW BLUE-GREEN DEPLOY STAGE 👇
        stage('Deploy (Blue-Green)') {
            steps {
                container('kubectl') {
                    sh """
                    # 1. Figure out which color is currently live
                    ACTIVE_COLOR=\$(kubectl get svc simple-app-service -o=jsonpath='{.spec.selector.color}' || echo "none")
                    
                    # 2. Decide the target environment (the idle one)
                    if [ "\$ACTIVE_COLOR" = "blue" ]; then
                        TARGET_COLOR="green"
                    else
                        TARGET_COLOR="blue"
                    fi
                    
                    echo "Currently active is \$ACTIVE_COLOR. Deploying new code to \$TARGET_COLOR..."
                    
                    # 3. Deploy the new image to the idle environment
                    kubectl apply -f deployment-\$TARGET_COLOR.yaml
                    kubectl set image deployment/simple-app-\$TARGET_COLOR web-container=${IMAGE_NAME}:${IMAGE_TAG}
                    
                    # 4. Wait for the new pods to be fully ready
                    kubectl rollout status deployment/simple-app-\$TARGET_COLOR
                    
                    # 5. Flip the traffic router to the new environment
                    kubectl patch svc simple-app-service -p "{\\"spec\\":{\\"selector\\":{\\"color\\":\\"\$TARGET_COLOR\\"}}}"
                    
                    echo "Traffic successfully switched to \$TARGET_COLOR!"
                    """
                }
            }
        }
        // 👆 --------------------------------------- 👆
    }
}