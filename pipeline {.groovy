pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/thirupathisamy07-cyber/jarvis.git'
            }
        }

        stage('Test') {
            steps {
                bat 'echo Jenkins working with main branch!'
            }
        }
    }
}