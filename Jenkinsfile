pipeline {
    agent any

    environment {
        DOCKER_IMAGE = 'shashank325/voting-app'
        DOCKER_REGISTRY = 'docker.io'
        K8S_NAMESPACE = 'default'
        K8S_DEPLOYMENT_NAME = 'voting-app'
        SONARQUBE_URL = 'http://192.168.216.27:9000/projects'  // Update with your SonarQube URL
        SONARQUBE_TOKEN = credentials('SonarQube Token')  // Jenkins credentials for SonarQube token
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
                    // Run SonarQube analysis
                    withCredentials([string(credentialsId: 'sonar-token', variable: 'SONARQUBE_TOKEN')]) {
                        sh '''
                            sonar-scanner \
                              -Dsonar.projectKey=${SONAR_PROJECT_KEY} \
                              -Dsonar.projectName=${SONAR_PROJECT_NAME} \
                              -Dsonar.sources=. \
                              -Dsonar.host.url=${SONARQUBE_URL} \
                              -Dsonar.login=${SONARQUBE_TOKEN}
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

                            # Ensure the ngrok authtoken is passed correctly
                            ngrok authtoken "$NGROK_AUTHTOKEN"

                            SERVICE_IP=$(kubectl get svc voting-app-service -o jsonpath='{.status.loadBalancer.ingress[0].ip}' || echo "")
                            if [ -z "$SERVICE_IP" ]; then
                                echo "Service IP not available, using port-forwarding instead"
                                POD_NAME=$(kubectl get pods -l app=${K8S_DEPLOYMENT_NAME} -o jsonpath='{.items[0].metadata.name}')
                                echo "Waiting for pod to be in Running state..."
                                kubectl wait --for=condition=ready pod/$POD_NAME --timeout=180s
                                if [ $? -eq 0 ]; then
                                    echo "Pod is now Running, starting port forwarding..."
                                    kubectl port-forward pod/$POD_NAME 5000:5000 &

                                    # Start ngrok to tunnel to the port
                                    ngrok http 5000 --log=stdout &  # Ngrok will tunnel the app at port 5000

                                    sleep 10  # Allow time for ngrok to start
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
