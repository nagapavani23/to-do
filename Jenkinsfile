pipeline {
    agent any

    environment {
        AKS_RG = "pavani"
        AKS_NAME = "webapp"
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/nagapavani23/to-do.git'
                script {
                    env.IMAGE_TAG = sh(script: "git rev-parse --short HEAD", returnStdout: true).trim()
                }
            }
        }

        stage('AKS Login') {
            steps {
                withCredentials([string(credentialsId: 'azure-sp-sdk-auth', variable: 'AZURE_SP_JSON')]) {
                    sh '''
                    AZURE_CLIENT_ID=$(echo $AZURE_SP_JSON | jq -r '.clientId')
                    AZURE_CLIENT_SECRET=$(echo $AZURE_SP_JSON | jq -r '.clientSecret')
                    AZURE_TENANT_ID=$(echo $AZURE_SP_JSON | jq -r '.tenantId')

                    az login --service-principal -u $AZURE_CLIENT_ID -p $AZURE_CLIENT_SECRET --tenant $AZURE_TENANT_ID
                    az aks get-credentials -g $AKS_RG -n $AKS_NAME --overwrite-existing

                    kubectl config current-context || true
                    kubectl get nodes || true
                    '''
                }
            }
        }

        stage('Docker Login') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-creds',
                    usernameVariable: 'DOCKERHUB_USER',
                    passwordVariable: 'DOCKERHUB_PASS'
                )]) {
                    sh 'echo $DOCKERHUB_PASS | docker login -u $DOCKERHUB_USER --password-stdin'
                }
            }
        }

        stage('Build & Push Frontend') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-creds',
                    usernameVariable: 'DOCKERHUB_USER',
                    passwordVariable: 'DOCKERHUB_PASS'
                )]) {
                    sh '''
                    docker build --no-cache -t $DOCKERHUB_USER/frontend:${IMAGE_TAG} ./frontend
                    docker push $DOCKERHUB_USER/frontend:${IMAGE_TAG}
                    '''
                }
            }
        }

        stage('Build & Push Backend') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-creds',
                    usernameVariable: 'DOCKERHUB_USER',
                    passwordVariable: 'DOCKERHUB_PASS'
                )]) {
                    sh '''
                    docker build --no-cache -t $DOCKERHUB_USER/backend:${IMAGE_TAG} ./backend
                    docker push $DOCKERHUB_USER/backend:${IMAGE_TAG}
                    '''
                }
            }
        }

        stage('Create Docker Secret on AKS') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-creds',
                    usernameVariable: 'DOCKERHUB_USER',
                    passwordVariable: 'DOCKERHUB_PASS'
                )]) {
                    sh '''
                    kubectl delete secret dockerhub-secret --ignore-not-found
                    kubectl create secret docker-registry dockerhub-secret \
                        --docker-username=$DOCKERHUB_USER \
                        --docker-password=$DOCKERHUB_PASS \
                        --docker-server=https://index.docker.io/v1/ \
                        --dry-run=client -o yaml | kubectl apply -f -
                    '''
                }
            }
        }

        stage('Deploy to AKS') {
            steps {
                sh '''
                sed -i "s|IMAGE_TAG|${IMAGE_TAG}|g" k8s/frontend.yaml
                sed -i "s|IMAGE_TAG|${IMAGE_TAG}|g" k8s/backend.yaml

                kubectl apply -f k8s/frontend.yaml
                kubectl rollout status deployment/frontend

                kubectl apply -f k8s/backend.yaml
                kubectl rollout status deployment/fastapi-backend
                '''
            }
        }

        stage('Force Rollout') {
            steps {
                sh '''
                # Force new pods even if nothing changed
                kubectl rollout restart deployment/frontend
                kubectl rollout restart deployment/fastapi-backend

                # Wait until rollout completes
                kubectl rollout status deployment/frontend
                kubectl rollout status deployment/fastapi-backend
                '''
            }
        }
    }
}
