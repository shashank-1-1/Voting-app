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
                git branch: 'main', url: 'https://github.com/shashank-1-1/Voting-app.git'
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
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
                    withCredentials([file(credentialsId: 'kubeconfig', variable: 'KUBECONFIG_FILE')]) {
                        sh '''
                            export KUBECONFIG=$KUBECONFIG_FILE
                            kubectl set image deployment/${K8S_DEPLOYMENT_NAME} voting-app=${DOCKER_IMAGE}:${BUILD_NUMBER}
                        '''
                    }
                }
            }
        }

        stage('Test Application Accessibility') {
            steps {
                script {
                    withCredentials([file(credentialsId: 'kubeconfig', variable: 'KUBECONFIG_FILE')]) {
                        sh '''
                            export KUBECONFIG=$KUBECONFIG_FILE

                            SERVICE_IP=$(kubectl get svc voting-app-service -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "")
                            if [ -z "$SERVICE_IP" ]; then
                                NODE_PORT=$(kubectl get svc voting-app-service -o jsonpath='{.spec.ports[0].nodePort}')
                                NODE_IP=$(kubectl get nodes -o jsonpath='{.items[0].status.addresses[?(@.type=="ExternalIP")].address}')
                                SERVICE_IP="${NODE_IP}:${NODE_PORT}"
                            fi

                            if [ -z "$SERVICE_IP" ]; then
                                echo "Service IP not available. Attempting port-forwarding..."
                                POD_NAME=$(kubectl get pods -l app=voting-app -o jsonpath='{.items[0].metadata.name}')
                                kubectl wait --for=condition=ready pod/$POD_NAME --timeout=180s
                                kubectl port-forward pod/$POD_NAME 5000:5000 &
                                PORT_FORWARD_PID=$!
                                sleep 10
                                curl --silent --fail http://localhost:5000 || exit 1
                                kill $PORT_FORWARD_PID
                            else
                                echo "Testing application at http://$SERVICE_IP"
                                curl --silent --fail http://$SERVICE_IP || exit 1
                            fi
                        '''
                    }
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
