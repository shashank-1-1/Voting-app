pipeline {
    agent any

    environment {
        DOCKER_IMAGE = 'shashank325/voting-app'
        DOCKER_REGISTRY = 'docker.io'
        K8S_NAMESPACE = 'default'
        K8S_DEPLOYMENT_NAME = 'voting-app'
        SONARQUBE_URL = 'http://192.168.216.27:9000'  // Update with your SonarQube URL
        SONARQUBE_TOKEN = credentials('sonar-token')  // Jenkins credentials for SonarQube token
        SONAR_PROJECT_KEY = 'Qwertyuiop.'  // Update with your project key in SonarQube
        SONAR_PROJECT_NAME = 'voting-app'  // Update with your project name in SonarQube
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
                    sh "docker build -t ${DOCKER_IMAGE}:${BUILD_NUMBER} ."
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

        stage('SonarQube Analysis') {
            steps {
                script {
                    // Run SonarQube analysis using the official Docker image for sonar-scanner
                    sh '''
                        docker run --rm \
                          -v $(pwd):/usr/src \
                          -e SONAR_HOST_URL=${SONARQUBE_URL} \
                          -e SONAR_LOGIN=${SONARQUBE_TOKEN} \
                          sonarsource/sonar-scanner-cli \
                          -Dsonar.projectKey=${SONAR_PROJECT_KEY} \
                          -Dsonar.projectName=${SONAR_PROJECT_NAME} \
                          -Dsonar.sources=/usr/src
                    '''
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                script {
                    withCredentials([file(credentialsId: 'kubeconfig', variable: 'KUBECONFIG_FILE')]) {
                        sh '''
                            export KUBECONFIG=$KUBECONFIG_FILE
                            kubectl set image deployment/${K8S_DEPLOYMENT_NAME} ${K8S_DEPLOYMENT_NAME}=${DOCKER_IMAGE}:${BUILD_NUMBER}
                        '''
                    }
                }
            }
        }

        stage('Check Kubernetes Cluster and Port Forward') {
            steps {
                script {
                    withCredentials([file(credentialsId: 'kubeconfig', variable: 'KUBECONFIG_FILE')]) {
                        sh '''
                            export KUBECONFIG=$KUBECONFIG_FILE
                            SERVICE_IP=$(kubectl get svc voting-app-service -o jsonpath='{.status.loadBalancer.ingress[0].ip}' || echo "")
                            if [ -z "$SERVICE_IP" ]; then
                                echo "Service IP not available, using port-forwarding instead"
                                POD_NAME=$(kubectl get pods -l app=${K8S_DEPLOYMENT_NAME} -o jsonpath='{.items[0].metadata.name}')
                                echo "Waiting for pod to be in Running state..."
                                kubectl wait --for=condition=ready pod/$POD_NAME --timeout=180s
                                if [ $? -eq 0 ]; then
                                    echo "Pod is now Running, starting port forwarding..."
                                    kubectl port-forward pod/$POD_NAME 5000:5000 &
                                    sleep 10  # Allow time for the port-forward to start
                                fi
                            else
                                echo "Testing application at http://$SERVICE_IP:5000"
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
