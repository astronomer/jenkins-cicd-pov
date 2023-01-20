pipeline {
    agent any
      stages {
        stage('Deploy to Astronomer') {
          when {
           expression {
             return env.GIT_BRANCH == "origin/main"
           }
          }
          steps {
            script {
              sh 'curl -LJO https://github.com/astronomer/astro-cli/releases/download/v1.9.0/astro_1.9.0_linux_amd64.tar.gz'
              sh 'tar xzf astro_1.9.0_linux_amd64.tar.gz'
              sh "./astro deploy"
            }
          }
        }
      }
    post {
      always {
        cleanWs()
      }
    }
}