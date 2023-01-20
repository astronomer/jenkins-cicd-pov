pipeline {
    agent any
      stages {
        stage('Dag Only Deploy to Astronomer') {
          when {
           expression {
             return env.GIT_BRANCH == "origin/main"
           }
          }
          when { changeset "dags/*"}
          steps {
            script {
              sh 'curl -LJO https://github.com/astronomer/astro-cli/releases/download/v1.9.0/astro_1.9.0_linux_amd64.tar.gz'
              sh 'tar xzf astro_1.9.0_linux_amd64.tar.gz'
              sh "./astro deploy --dags -f"
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