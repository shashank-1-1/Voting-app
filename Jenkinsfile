stage('Check Kubernetes Pods and Port Forward') {
    steps {
        script {
            withCredentials([file(credentialsId: 'kubeconfig', variable: 'KUBECONFIG_FILE')]) {
                sh '''
                    export KUBECONFIG=$KUBECONFIG_FILE
                    echo "Checking Kubernetes Cluster Info"
                    kubectl cluster-info

                    echo "Fetching service IP for voting-app-service"
                    SERVICE_IP=$(kubectl get svc voting-app-service --namespace ${K8S_NAMESPACE} -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
                    
                    # Set up cleanup trap for port forwarding
                    cleanup() {
                        echo "Cleaning up port-forwarding..."
                        pkill -f "kubectl port-forward" || true
                    }
                    trap cleanup EXIT

                    if [ -z "$SERVICE_IP" ]; then
                        echo "Service IP not available, using port-forwarding instead"
                        POD_NAME=$(kubectl get pods --namespace ${K8S_NAMESPACE} -l app=voting-app -o jsonpath='{.items[0].metadata.name}')
                        
                        echo "Waiting for pod to be in Running state..."
                        kubectl wait --for=condition=ready pod/$POD_NAME --namespace ${K8S_NAMESPACE} --timeout=180s
                        if [ $? -eq 0 ]; then
                            echo "Pod is now Running, starting port forwarding..."
                            kubectl port-forward pod/$POD_NAME 5000:80 --namespace ${K8S_NAMESPACE} &
                            sleep 10
                            echo "Testing application at http://localhost:5000"
                            curl --silent --fail http://localhost:5000 || exit 1
                        else
                            echo "Pod did not become ready in time."
                            exit 1
                        fi
                    else
                        echo "Testing application at http://$SERVICE_IP:5000"
                        curl --silent --fail http://$SERVICE_IP:5000 || exit 1
                    fi
                '''
            }
        }
    }
}
