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
            }
        }

        stage('Docker Login') {
            steps {
                withCredentials([
                    string(credentialsId: 'azure-client-id', variable: 'AZURE_CLIENT_ID'),
                    string(credentialsId: 'azure-client-secret', variable: 'AZURE_CLIENT_SECRET'),
                    string(credentialsId: 'azure-tenant-id', variable: 'AZURE_TENANT_ID')
                ]) {
                    sh """
                    az login --service-principal -u $AZURE_CLIENT_ID -p $AZURE_CLIENT_SECRET --tenant $AZURE_TENANT_ID
                    az aks get-credentials -g $AKS_RG -n $AKS_NAME --overwrite-existing
                    """
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
                    sh """
                    docker build -t \$DOCKERHUB_USER/frontend:latest ./frontend
                    docker push \$DOCKERHUB_USER/frontend:latest
                    """
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
                    sh """
                    docker build -t \$DOCKERHUB_USER/backend:latest ./backend
                    docker push \$DOCKERHUB_USER/backend:latest
                    """
                }
            }
        }

        stage('AKS Login') {
    steps {
        withCredentials([string(credentialsId: 'azure-sp-adk-auth', variable: 'AZURE_SP_JSON')]) {
            sh '''
            # Parse JSON from the secret
            AZURE_CLIENT_ID=$(echo $AZURE_SP_JSON | jq -r '.clientId')
            AZURE_CLIENT_SECRET=$(echo $AZURE_SP_JSON | jq -r '.clientSecret')
            AZURE_TENANT_ID=$(echo $AZURE_SP_JSON | jq -r '.tenantId')

            # Login to Azure
            az login --service-principal -u $AZURE_CLIENT_ID -p $AZURE_CLIENT_SECRET --tenant $AZURE_TENANT_ID

            # Get AKS credentials
            az aks get-credentials -g $AKS_RG -n $AKS_NAME --overwrite-existing
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
                    sh """
                    kubectl create secret docker-registry dockerhub-secret \\
                        --docker-username=\$DOCKERHUB_USER \\
                        --docker-password=\$DOCKERHUB_PASS \\
                        --docker-server=https://index.docker.io/v1/ \\
                        --dry-run=client -o yaml | kubectl apply -f -
                    """
                }
            }
        }

        stage('Deploy to AKS') {
            steps {
                sh """
                kubectl apply -f k8s/frontend-deployment.yaml
                kubectl apply -f k8s/backend-deployment.yaml
                """
            }
        }
    }
}
