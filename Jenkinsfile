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
                // Safe Docker Hub login using "Username with password" credentials
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
                sh """
                docker build -t $DOCKERHUB_USER/frontend:latest ./frontend
                docker push $DOCKERHUB_USER/frontend:latest
                """
            }
        }

        stage('Build & Push Backend') {
            steps {
                sh """
                docker build -t $DOCKERHUB_USER/backend:latest ./backend
                docker push $DOCKERHUB_USER/backend:latest
                """
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
                    az aks get-credentials -g $AKS_RG -n $AKS_NAME --overwrite-existing
                    kubectl create secret docker-registry dockerhub-secret \\
                        --docker-username=$DOCKERHUB_USER \\
                        --docker-password=$DOCKERHUB_PASS \\
                        --docker-server=https://index.docker.io/v1/ \\
                        --dry-run=client -o yaml | kubectl apply -f -
                    """
                }
            }
        }

        stage('Deploy to AKS') {
            steps {
                sh """
                az aks get-credentials -g $AKS_RG -n $AKS_NAME --overwrite-existing
                kubectl apply -f k8s/frontend-deployment.yaml
                kubectl apply -f k8s/backend-deployment.yaml
                """
            }
        }
    }
}
