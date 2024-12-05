stage('Check Kubernetes Cluster and Port Forward') {
    steps {
        script {
            withCredentials([file(credentialsId: 'kubeconfig', variable: 'KUBECONFIG_FILE')]) {
                sh '''
                    export KUBECONFIG=$KUBECONFIG_FILE

                    # Ensure the ngrok authtoken is passed correctly
                    ngrok authtoken $NGROK_AUTHTOKEN

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
