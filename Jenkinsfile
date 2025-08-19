pipeline {
    agent any

    environment {
        DOCKERHUB_USER = "nagapavani2301"
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
                // Using withCredentials to mask password safely
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
