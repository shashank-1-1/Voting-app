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
                            kubectl set image deployment/voting-app voting-app=${DOCKER_IMAGE}:${BUILD_NUMBER} --namespace default
                        '''
                    }
                }
            }
        }

        stage('Check Pods and Port Forward') {
            steps {
                script {
                    // Use kubectl to check the status of the pods
                    sh '''
                        echo "Checking Kubernetes Pods..."
                        kubectl get pods --namespace ${K8S_NAMESPACE}
                    '''

                    // Get the name of the pod (assuming you only have one pod)
                    def podName = sh(script: "kubectl get pods --namespace ${K8S_NAMESPACE} -o jsonpath='{.items[0].metadata.name}'", returnStdout: true).trim()

                    // Use kubectl to port-forward the pod to access the app
                    if (podName) {
                        echo "Port-forwarding pod ${podName}..."
                        sh """
                            kubectl port-forward pod/${podName} 5000:80 --namespace ${K8S_NAMESPACE} &
                            sleep 5  # Give port-forwarding a moment to establish
                            curl http://localhost:5000  # Test if the app is accessible via port 5000
                            pkill -f "kubectl port-forward" || true  # Clean up port-forwarding process
                        """
                    } else {
                        error "Pod not found!"
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
