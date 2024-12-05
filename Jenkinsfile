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
                            kubectl set image deployment/voting-app voting-app=shashank325/voting-app:${BUILD_NUMBER} --namespace default
                        '''
                    }
                }
            }
        }

        stage('Check Kubernetes Pods and Port Forward') {
    steps {
        script {
            // Use the Secret File with ID 'kubeconfig' and set the KUBECONFIG environment variable
            withCredentials([file(credentialsId: 'kubeconfig', variable: 'KUBECONFIG_FILE')]) {
                // Set the KUBECONFIG environment variable to the file path of the secret
                sh '''
                    export KUBECONFIG=$KUBECONFIG_FILE
                    echo "Checking Kubernetes Cluster Info"
                    kubectl cluster-info

                    echo "Fetching service IP for voting-app-service"
                    SERVICE_IP=$(kubectl get svc voting-app-service --namespace ${K8S_NAMESPACE} -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
                    
                    if [ -z "$SERVICE_IP" ]; then
                        echo "Service IP not available, using port-forwarding instead"
                        POD_NAME=$(kubectl get pods --namespace ${K8S_NAMESPACE} -l app=voting-app -o jsonpath='{.items[0].metadata.name}')
                        
                        # Wait for the pod to be in Running state
                        echo "Waiting for pod to be in Running state..."
                        kubectl wait --for=condition=ready pod/$POD_NAME --namespace ${K8S_NAMESPACE} --timeout=180s
                        if [ $? -eq 0 ]; then
                            echo "Pod is now Running, starting port forwarding..."
                            kubectl port-forward pod/$POD_NAME 5000:80 --namespace ${K8S_NAMESPACE} &
                            sleep 5  # Give port-forwarding a moment to establish
                            curl http://localhost:5000  # Test if the app is accessible via port 5000
                            pkill -f "kubectl port-forward" || true  # Clean up port-forwarding process
                        else
                            echo "Pod did not become ready in time."
                            exit 1
                        fi
                    else
                        # Use the external service IP for testing
                        curl http://$SERVICE_IP:5000  # Assuming the service is available on port 5000
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
