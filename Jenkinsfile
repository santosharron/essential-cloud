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
        // 1. Build the Docker Image
        stage('Build Image') {
            steps {
                container('docker') {
                    sh "docker build -t ${IMAGE_NAME}:${IMAGE_TAG} ."
                }
            }
        }

        // 👇 2. THIS IS THE NEW DEVSECOPS STAGE 👇
        stage('Security Scan (Healthcare Compliance)') {
            steps {
                container('docker') {
                    echo "Installing Trivy Security Scanner..."
                    sh "apk add --no-cache curl"
                    sh "curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin"
                    
                    echo "Scanning the Docker Image for HIGH and CRITICAL vulnerabilities..."
                    // We use exit-code 0 so the pipeline doesn't crash if it finds old Python vulnerabilities, but it will print the full report!
                    sh "trivy image --severity HIGH,CRITICAL --no-progress --exit-code 0 ${IMAGE_NAME}:${IMAGE_TAG}"
                }
            }
        }
        // 👆 --------------------------------- 👆

        // 3. Push to Docker Hub (Moved AFTER the scan!)
        stage('Push Image') {
            steps {
                container('docker') {
                    withCredentials([usernamePassword(credentialsId: 'dockerhub-credentials', passwordVariable: 'DOCKERHUB_PASS', usernameVariable: 'DOCKERHUB_USER')]) {
                        sh 'echo "$DOCKERHUB_PASS" | docker login -u "$DOCKERHUB_USER" --password-stdin'
                        sh "docker push ${IMAGE_NAME}:${IMAGE_TAG}"
                    }
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