pipeline {
    agent any

    environment {
        OC_SERVER = 'oc login --token=sha256~ZQSsFlKOcEFjpYc8LHZBrCoQ1uVfuqVEzkrEypL-YZU --server=https://api.cacheocpnode.cacheocp.com:6443'
        NAMESPACE = 'voting-app'
        DEPLOYMENT_NAME = 'voting-app-deployment'
    }

    stages {
        stage('Clone Repository') {
            steps {
                git branch: 'main', url: 'https://github.com/shashank-1-1/Voting-app.git'
            }
        }

        stage('Build') {
            steps {
                script {
                    echo "Building the Python Application..."
                    // Place any Python build commands here, e.g., linting or tests
                    sh 'python -m unittest discover -s tests'
                }
            }
        }

        stage('Deploy to OpenShift') {
            steps {
                script {
                    echo "Deploying to OpenShift..."
                    withCredentials([string(credentialsId: 'openshift-token', variable: 'TOKEN')]) {
                        sh """
                            oc login $OC_SERVER --token=$TOKEN --insecure-skip-tls-verify
                            oc project $NAMESPACE
                            oc new-app --name=$DEPLOYMENT_NAME https://github.com/shashank-1-1/Voting-app.git
                        """
                    }
                }
            }
        }

        stage('Verify Deployment') {
            steps {
                script {
                    echo "Verifying the deployment..."
                    sh "oc get pods -n $NAMESPACE"
                }
            }
        }
    }
}
