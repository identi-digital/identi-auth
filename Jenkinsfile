pipeline {
    agent {
        kubernetes {
            yaml '''
            apiVersion: v1
            kind: Pod
            spec:
              serviceAccountName: jenkins-admin
              containers:
              
              - name: cicd-agent
                image: codigonet/jnk-agent
                command:
                - sleep
                args:
                - infinity
                tty: true

              - name: kaniko
                image: gcr.io/kaniko-project/executor:debug
                command:
                - sleep
                args:
                - infinity
                tty: true
                env:
                - name: AWS_SDK_LOAD_CONFIG
                  value: true
                - name: AWS_EC2_METADATA_DISABLED
                  value: true
            '''
            defaultContainer 'cicd-agent'
        }
    }
    environment{
        def IMAGE_NAME='NO-IMAGE'
        def SONAR_TOKEN='squ_USER-TOKEN'
    }
    stages {

        stage('SonarQube Analysis') {
            steps{
                script{
                    def scannerHome = tool 'sonarqube';
                    withSonarQubeEnv() {
                      sh "${scannerHome}/bin/sonar-scanner"
                    }
                }
            }
        }

        stage('SonarQube Quality Gate') {
            steps{
                script{
                    echo "Ejecución de QualityGate"
                    // def scannerHome = tool 'sonarqube';
                    // withSonarQubeEnv() {
                    //   sh "${scannerHome}/bin/sonar-scanner"
                    // }
                }
            }
        }

        stage('Compile') {
            steps {
                script {
                    sh '''
                    echo "Ejecutar Build necesario..."
                    '''
                }
            }
        }

        stage('Testing') {
            steps {
                script {
                    echo "Ejecución de Pruebas Unitarias"
                    // sh '''
                    // pytest
                    // '''
                    echo "Ejecución de Pruebas Selenium"
                    // sh '''
                    // selenium-cli -f test/panel.json --level 3
                    // '''
                }
            }
        }

        stage('QA Plan') {
            steps {
                script {
                    echo "Obtener scripts de Test https://github.com/codigonet/simple-scripts"
                    sh 'curl https://raw.githubusercontent.com/codigonet/simple-scripts/master/test-1.sh -o test-1.sh'
                    sh 'curl https://raw.githubusercontent.com/codigonet/simple-scripts/master/test-2-error.sh -o test-2-error.sh'
                    
                    echo "Ejecución de Pruebas Integradas"
                    sh 'chmod +x test-1.sh'
                    sh './test-1.sh'

                    // echo "Ejecución de Pruebas Integradas (con error)"
                    // sh 'chmod +x test-2-error.sh'
                    // sh './test-2-error.sh'

                }
            }
        }

        stage('Build') {
            steps {
                script {
                    sh 'touch docker-image.txt'
                    container(name: 'kaniko', shell: '/busybox/sh') {
                        sh '''#!/busybox/sh
                        dockerConfig=\${DOCKER_CONFIG:-/kaniko/.docker}
                        [ -d \${dockerConfig} ] && echo "Docker directory Exists" || mkdir -p \${dockerConfig}
                        echo '{"credsStore":"ecr-login"}' > \${dockerConfig}/config.json
                        '''

                        withCredentials([string(credentialsId: 'ECR_HOST', variable: 'ECR_HOST')]){
                            // For ECR, IMAGE_NAME needs to append ECR repository full path
                            IMAGE_NAME = "${ECR_HOST}/identi-authx:v1.0.0-${env.BUILD_NUMBER}"
                            // IMAGE_NAME = "identi-authx:v1.0.0-${env.BUILD_NUMBER}"
                        }
                        
                        sh "echo ${IMAGE_NAME} >> docker-image.txt"

                        echo "Imagen [${IMAGE_NAME}]"
                        
                        sh '''
                        cd src
                        ls -l
                        '''
                        withCredentials([aws(credentialsId: 'ECR_AUTH')]){
                            sh "/kaniko/executor --destination $IMAGE_NAME"
                        }
                    }

                    sh """
                    echo "Image build [${IMAGE_NAME}]"
                    """
                }
            }
        }

    }
    
    post {
        failure {
            echo "Proceso [$env.BUILD_NUMBER] con error."
        }
        always {
            echo "Proceso [$env.BUILD_NUMBER] finalizado."
            // Informar resultado por Slack #
        }
    }
}
