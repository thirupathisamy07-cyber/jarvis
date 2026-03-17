pipeline {
    agent any

    stages {
        stage('Clone') {
            steps {
                git branch: 'main', url: 'https://github.com/thirupathisamy07-cyber/jarvis.git'
            }
        }

        stage('Install Dependencies') {
            steps {
                bat 'pip install requests pyttsx3 SpeechRecognition psutil pillow'
            }
        }

        stage('Run Jarvis') {
            steps {
                bat 'python jarvis.py'
            }
        }
    }
}
