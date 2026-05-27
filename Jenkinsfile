pipeline {
    agent none

    environment {
        // ECR registry derived from AWS account ID
        ECR_REGISTRY = '445529239852.dkr.ecr.ap-east-1.amazonaws.com'
        IMAGE_NAME   = 'flask-demo/flask-demo-1'
        IMAGE        = "${ECR_REGISTRY}/${IMAGE_NAME}"
        TAG          = "build-${BUILD_NUMBER}"
    }

    stages {
        stage('Python CI Check') {
            agent {
                label 'python'
            }

            stages {
                stage('Check Python') {
                    steps {
                        sh 'python3 --version'
                        sh 'pip3 --version'
                    }
                }

                stage('Create Virtualenv') {
                    steps {
                        sh 'python3 -m venv .venv'
                    }
                }

                stage('Install Dependencies') {
                    steps {
                        sh '''
                            . .venv/bin/activate
                            pip install --upgrade pip
                            pip install -r requirements.txt
                        '''
                    }
                }

                stage('Syntax Check') {
                    steps {
                        sh '''
                            . .venv/bin/activate
                            python -m py_compile app.py
                        '''
                    }
                }

                stage('Import Flask App') {
                    steps {
                        sh '''
                            . .venv/bin/activate
                            python -c "import app; print('Flask app import success')"
                        '''
                    }
                }

                stage('Run Flask App and Health Check') {
                    steps {
                        sh '''
                            . .venv/bin/activate

                            nohup python app.py > flask.log 2>&1 &
                            echo $! > flask.pid

                            sleep 5

                            echo "=== flask.log ==="
                            cat flask.log || true

                            echo "=== curl check ==="
                            curl -s http://127.0.0.1:8080/ | tee curl.out

                            grep -q "Hello from Flask Demo" curl.out
                        '''
                    }
                }
            }

            post {
                always {
                    sh '''
                        if [ -f flask.pid ]; then
                            kill $(cat flask.pid) || true
                        fi
                    '''
                }
            }
        }

        stage('Build and Push to ECR') {
            agent {
                label 'kaniko'
            }

            steps {
                container('kaniko') {
                    // No --registry-certificate needed: ECR uses public CA bundle
                    // No docker config needed: Kaniko on EKS auto-detects IRSA via IMDS
                    //   and exchanges the projected SA token for ECR auth tokens.
                    sh '''
                        /kaniko/executor \
                          --context "${WORKSPACE}" \
                          --dockerfile "${WORKSPACE}/Dockerfile" \
                          --destination "${IMAGE}:${TAG}" \
                          --destination "${IMAGE}:latest" \
                          --cache=true \
                          --cache-repo "${ECR_REGISTRY}/${IMAGE_NAME}/cache" \
                          --verbosity info
                    '''
                }
            }
        }

        // ----------------------------------------------------------------
        // GitOps stage commented out — will be enabled after ArgoCD setup.
        // When ready, replace Gitea with GitHub:
        //   - credentialsId: 'github-token' (already configured in JCasC)
        //   - CHART_REPO:    'github.com/jif718/flask-demo-1-chart.git'
        // ----------------------------------------------------------------
        // stage('Update Helm Chart Repo') {
        //     agent {
        //         label 'python'
        //     }
        //     steps {
        //         withCredentials([usernamePassword(
        //             credentialsId: 'github-token',
        //             usernameVariable: 'GIT_USER',
        //             passwordVariable: 'GIT_PASS'
        //         )]) {
        //             sh '''
        //                 set -e
        //                 rm -rf flask-demo-1-chart
        //                 git clone https://${GIT_USER}:${GIT_PASS}@github.com/jif718/flask-demo-1-chart.git
        //                 cd flask-demo-1-chart
        //                 git config user.name  "jenkins"
        //                 git config user.email "jenkins@jif-lab"
        //                 sed -i "s|^  repository:.*|  repository: ${IMAGE}|" values.yaml
        //                 sed -i "s|^  tag:.*|  tag: \\\"${TAG}\\\"|"          values.yaml
        //                 git add values.yaml
        //                 git commit -m "Update image tag to ${TAG}" || echo "No changes"
        //                 git push origin main
        //             '''
        //         }
        //     }
        // }
    }

    post {
        success {
            echo "Image pushed to ECR: ${IMAGE}:${TAG}"
            echo "Image pushed to ECR: ${IMAGE}:latest"
        }
        failure {
            echo 'Pipeline failed, check logs above'
        }
    }
}