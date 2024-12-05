pipeline {
    agent any

    environment {
        DOCKER_IMAGE = 'shashank325/voting-app'
        DOCKER_REGISTRY = 'docker.io'
        K8S_NAMESPACE = 'default'
        K8S_DEPLOYMENT_NAME = 'voting-app'
    }

    stages {
        stage('Clone Repository') {
            steps {
                // Checkout your Git repository containing the Dockerfile and app
                git branch: 'main', url: 'https://github.com/shashank-1-1/Voting-app.git'
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    // Build Docker image
                    sh 'docker build -t ${DOCKER_IMAGE}:${BUILD_NUMBER} .'
                }
            }
        }

        stage('Push Docker Image to Docker Hub') {
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: 'docker-hub-credentials', usernameVariable: 'DOCKER_USERNAME', passwordVariable: 'DOCKER_PASSWORD')]) {
                        sh '''
                            docker login -u $DOCKER_USERNAME -p $DOCKER_PASSWORD
                            docker push ${DOCKER_IMAGE}:${BUILD_NUMBER}
                        '''
                    }
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                script {
                    // Use the Secret File with ID 'kubeconfig' and set the KUBECONFIG environment variable
                    withCredentials([file(credentialsId: 'kubeconfig', variable: 'KUBECONFIG_FILE')]) {
                        // Set the KUBECONFIG environment variable to the file path of the secret
                        sh '''
                            export KUBECONFIG=$KUBECONFIG_FILE
                            kubectl set image deployment/voting-app voting-app=${DOCKER_IMAGE}:${BUILD_NUMBER} --namespace ${K8S_NAMESPACE}
                        '''
                    }
                }
            }
        }

        stage('Post-Deployment Tests') {
            steps {
                script {
                    // Access the Kubernetes service IP dynamically or use port-forward
                    sh '''
                    # Fetch the Kubernetes service IP (ClusterIP or EXTERNAL-IP)
                    SERVICE_IP=$(kubectl get svc voting-app-service --namespace ${K8S_NAMESPACE} -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
                    
                    if [ -z "$SERVICE_IP" ]; then
                        # If EXTERNAL-IP is pending, fall back to using port-forward
                        echo "EXTERNAL-IP is pending, using port-forwarding..."
                        kubectl port-forward svc/voting-app-service 5000:80 --namespace ${K8S_NAMESPACE} &
                        sleep 5  # Give port-forwarding a moment to establish
                        
                        # Ensure the app is accessible before testing
                        until curl -s http://localhost:5000; do
                            echo "Waiting for the app to become available..."
                            sleep 5
                        done
                        echo "App is up and running!"
                        pkill -f "kubectl port-forward" || true  # Clean up port-forwarding process
                    else
                        # Use the external service IP for testing
                        echo "Using service external IP: $SERVICE_IP"
                        until curl -s http://$SERVICE_IP:5000; do
                            echo "Waiting for the app to become available at $SERVICE_IP..."
                            sleep 5
                        done
                        echo "App is up and running!"
                    fi
                    '''
                }
            }
        }
    }

    post {
        success {
            echo "Deployment successful!"
        }
        failure {
            echo "Deployment failed!"
        }
    }
}
