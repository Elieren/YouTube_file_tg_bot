pipeline {
    agent any

    stages {
        stage('Prepare Environment') {
            steps {
                script {
                    // Загрузка переменных окружения из файла .env
                    def envVars = readProperties file: '/opt/env/.env.youtube_bot'

                    // Импорт переменных окружения в среду Jenkins job
                    envVars.each {
                        env."${it.key}" = "${it.value}"
                    }
                }
            }
        }
        stage('Get Old Image Tag') {
            steps {
                script {
                    // Получаем тег старого образа youtube-file-async
                    env.OLD_IMAGE_TAG = sh(script: "docker images youtube-file-async --format '{{.Tag}}' | head -n 1", returnStdout: true).trim()
                }
            }
        }
        stage('Build New Image') {
            steps {
                script {
                    // Создание уникального имени для нового образа
                    def timestamp = new Date().getTime()
                    env.NEW_IMAGE_NAME = "youtube-file-async:${timestamp}"

                    echo "# Собираем новый Docker образ"
                    sh "docker build -t ${env.NEW_IMAGE_NAME} ."
                }
            }
        }
        stage('Cleanup Old Container and Image') {
            steps {
                echo "# Принудительно останавливаем и удаляем старый контейнер, если он существует"
                sh "docker rm -f youtube-file-async || true"

                echo "# Удаляем старый Docker образ, если он существует"
                sh "docker rmi youtube-file-async:${env.OLD_IMAGE_TAG} || true"
            }
        }
        stage('Deploy New Container') {
            steps {
                echo "# Запускаем новый контейнер"
                sh "docker run -d --restart unless-stopped --network host --name youtube-file-async -e USER=$USER -e PASSWORD=$PASSWORD -e HOST=$HOST -e KEY=$KEY -e URL_HOST=$URL_HOST -e ACCESS_KEY=$ACCESS_KEY -e SECRET_ACCESS_KEY=$SECRET_ACCESS_KEY -e BUCKET=$BUCKET -e SERVER_AWS_URL=$SERVER_AWS_URL ${env.NEW_IMAGE_NAME}"
            }
        }
    }
}
