pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                git 'https://github.com/your-repo/jarvis.git'
            }
        }

        stage('Install Dependencies') {
            steps {
                sh 'pip install -r requirements.txt'
            }
        }

        stage('Run JARVIS') {
            steps {
                sh 'python main.py'
            }
        }

        stage('Deploy') {
            steps {
                echo 'Jarvis deployed successfully!'
            }
        }
    }
}