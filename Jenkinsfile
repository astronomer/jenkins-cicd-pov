pipeline {
    agent any
      stages {
        stage('checkout'){
            steps{
                git branch: 'main', url: 'https://github.com/astronomer/jenkins-cicd-pov.git'
            }
        }
        stage('Dag Only Deploy to Astronomer') {
          when {
           expression {
             return env.GIT_BRANCH == "origin/main"
           }
          }
          steps {
              sh '''
              curl -LJO https://github.com/astronomer/astro-cli/releases/download/v1.9.0/astro_1.9.0_linux_amd64.tar.gz'
              tar xzf astro_1.9.0_linux_amd64.tar.gz
              files=($(git diff-tree HEAD --name-only --no-commit-id))
              find="dags"
              if [[ ${files[*]} =~ (^|[[:space:]])"$find"($|[[:space:]]) && ${#files[@]} -eq 1 ]]; then
                ./astro deploy --dags -f;
              else
                ./astro deploy -f;
              fi
              '''
          }
        }
      }
    post {
      always {
        cleanWs()
      }
    }
}