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
                image: codigonet/jnk-agent:latest
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
                    echo "QualityGate Plan"
                }
            }
        }

        stage('Compile') {
            steps {
                script {
                    sh '''
                    echo "Build steps..."
                    '''
                }
            }
        }

        stage('Testing') {
            steps {
                script {
                    echo "Unit testing Plan"
                    // sh '''
                    // pytest
                    // '''
                    echo "Selenium Unit testing Plan"
                    // sh '''
                    // selenium-cli -f test/panel.json --level 3
                    // '''
                }
            }
        }

        stage('QA Plan') {
            steps {
                script {
                    echo "Download Base QA scripts https://github.com/codigonet/simple-scripts"
                    sh 'curl https://raw.githubusercontent.com/codigonet/simple-scripts/master/test-1.sh -o test-1.sh'
                    sh 'curl https://raw.githubusercontent.com/codigonet/simple-scripts/master/test-2-error.sh -o test-2-error.sh'
                    
                    echo "Integration Tests Plan"
                    sh 'chmod +x test-1.sh'
                    sh './test-1.sh'

                    // echo "Integration Tests Plan (with error)"
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

                        withCredentials([string(credentialsId: 'ECR-Host', variable: 'ECR_HOST')]){
                            IMAGE_NAME = "${ECR_HOST}/identi-authx:v1.0.0-${env.BUILD_NUMBER}"
                        }
                        
                        sh "echo ${IMAGE_NAME} >> docker-image.txt"

                        echo "Imagen [${IMAGE_NAME}]"
                        
                        sh '''
                        ls -l
                        '''
                        withCredentials([aws(credentialsId: 'ECR-Auth')]){
                            sh "/kaniko/executor --context `pwd` --destination $IMAGE_NAME"
                        }
                    }

                    sh """
                    echo "Image build [${IMAGE_NAME}]"
                    """
                }
            }
        }

        stage('Deploy') {
            steps {
                script {
                    echo "Image to DEPLOY [${IMAGE_NAME}]"
                    sh """
                    cp deploy/deploy.template-yaml deploy/deploy.yaml
                    sed -i -e '/image: /s|identi-authx:latest|${IMAGE_NAME}|g' deploy/deploy.yaml
                    """
                    sh 'kubectl apply -f deploy/deploy.yaml -n identi-auth'
                }
            }
        }

    }
    
    post {
        success{
            echo "Process [$env.BUILD_NUMBER] OK."
        }
        failure {
            echo "Process [$env.BUILD_NUMBER] with errors."
        }
        always {
            echo "Process [$env.BUILD_NUMBER] finished."
        }
    }
}
