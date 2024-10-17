pipeline {
    agent any

    environment {
        GIT_REPO = 'https://github.com/shashank-1-1/Voting-app.git'
        BRANCH = 'main'
        SONARQUBE_SERVER = 'sonar' // Replace with your SonarQube server name in Jenkins
        SONARQUBE_PROJECT_KEY = 'voting-app' // Replace with your SonarQube project key
        VENV_DIR = 'venv'
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: "${BRANCH}", url: "${GIT_REPO}"
            }
        }

        stage('Setup Python Environment') {
            steps {
                sh 'python3 -m venv ${VENV_DIR}'
                sh '. ${VENV_DIR}/bin/activate'
                sh 'pip install -r requirements.txt'
            }
        }

        stage('Run Tests') {
            steps {
                sh '. ${VENV_DIR}/bin/activate && pytest'
            }
        }

        stage('SonarQube Analysis') {
            steps {
                script {
                    withSonarQubeEnv("${SONARQUBE_SERVER}") {
                        sh """
                        . ${VENV_DIR}/bin/activate
                        sonar-scanner \
                        -Dsonar.projectKey=${SONARQUBE_PROJECT_KEY} \
                        -Dsonar.sources=. \
                        -Dsonar.host.url=$SONAR_HOST_URL \
                        -Dsonar.login=$SONAR_AUTH_TOKEN
                        """
                    }
                }
            }
        }

        stage('Quality Gate') {
            steps {
                waitForQualityGate abortPipeline: true
            }
        }
    }

    post {
        always {
            cleanWs()
        }
    }
}


