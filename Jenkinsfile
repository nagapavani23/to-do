pipeline {
    agent any

    environment {
        DOCKERHUB_USER = "nagapavani2301"
        DOCKERHUB_PASS = credentials('dockerhub-creds') // Jenkins credential ID
        AKS_RG = "pavani"
        AKS_NAME = "webapp"
    }

    stages {
        stage('Checkout') {
            steps {
                git 'https://github.com/nagapavani23/to-do.git'
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
