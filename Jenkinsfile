pipeline {
    agent any

    environment {
        DOCKERHUB_USER = "your-dockerhub-username"
        DOCKERHUB_PASS = credentials('dockerhub-password') // Jenkins credential ID
        AKS_RG = "myResourceGroup"
        AKS_NAME = "myAKSCluster"
    }

    stages {
        stage('Checkout') {
            steps {
                git 'https://github.com/your-repo/2tier-aks.git'
            }
        }

        stage('Docker Login') {
            steps {
                sh """
                echo $DOCKERHUB_PASS | docker login -u $DOCKERHUB_USER --password-stdin
                """
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

        stage('Deploy to AKS') {
            steps {
                sh """
                az aks get-credentials -g $AKS_RG -n $AKS_NAME --overwrite-existing
                kubectl apply -f k8s/
                """
            }
        }
    }
}
