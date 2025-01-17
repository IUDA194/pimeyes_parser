pipeline {
    agent any

    environment {
        GIT_CREDENTIALS = credentials('gitlab-iuda-sitera')
        DOCKERHUB_CREDENTIALS = credentials('docker-iuda')
        IMAGE_NAME = "iuda194/find_face_parser:prod"
    }
    stages {
        stage('Build Docker Image') {
            steps {
                script {
                    sh 'echo $DOCKERHUB_CREDENTIALS_PSW | docker login -u $DOCKERHUB_CREDENTIALS_USR --password-stdin'
                    // Выполнение команды docker build . в корне проекта
                    sh 'docker build -t ${IMAGE_NAME} .'
                }
            }
        }

        stage('Push Docker Image') {
            steps {
                script {
                    // Логин в Docker Hub и пуш образа
                    sh '''
                    echo $DOCKERHUB_CREDENTIALS_PSW | docker login -u $DOCKERHUB_CREDENTIALS_USR --password-stdin
                    docker push ${IMAGE_NAME}
                    '''
                }
            }
        }
    }

    post {
        always {
            // Очистка рабочего пространства после выполнения
            cleanWs()
        }
    }
}
