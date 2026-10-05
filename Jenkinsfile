// =====================================================================
// Jenkinsfile — DECLARATIVE PIPELINE for DevOps Training Login App
// =====================================================================
// Triggered by: GitHub webhook on every push to main branch
// What it does: Checkout → Build → Test → Push Image → Deploy
// =====================================================================

pipeline {
    agent any

    environment {
        DOCKERHUB_USER     = 'krishna98967'   // CHANGE THIS
        IMAGE_NAME         = 'devops-login-app'
        IMAGE_TAG          = "${BUILD_NUMBER}"           
        FULL_IMAGE         = "${DOCKERHUB_USER}/${IMAGE_NAME}:${IMAGE_TAG}"
    }

    options {
        timeout(time: 15, unit: 'MINUTES')          
        buildDiscarder(logRotator(numToKeepStr: '10'))  
    }

    stages {
        // ---------- Stage 1: Checkout code from GitHub ----------
        stage('Checkout') {
            steps {
                echo "🔄 Pulling latest code from GitHub..."
                checkout scm   
                sh 'ls -la'
            }
        }

        // ---------- Stage 2: Build the Docker image ----------
        stage('Build Image') {
            steps {
                echo "🏗️  Building Docker image: ${FULL_IMAGE}"
                sh "docker build -t ${FULL_IMAGE} -t ${DOCKERHUB_USER}/${IMAGE_NAME}:latest ."
            }
        }

        // ---------- Stage 3: Run a smoke test ----------
        stage('Test') {
            steps {
                echo "🧪 Running smoke test on the image..."
                sh '''
                    # Spin up a quick container, hit /health, then kill it
                    docker run -d --name smoke-test -p 5555:5000 -e DB_HOST=dummy ${FULL_IMAGE} || true
                    sleep 5
                    # /health returns 200 now since we fixed the missing route in app.py
                    curl -fsS http://localhost:5555/health || (docker logs smoke-test && exit 1)
                    docker rm -f smoke-test
                '''
            }
        }

        // ---------- Stage 4: Push image to Docker Hub ----------
        stage('Push to Docker Hub') {
            steps {
                echo "📤 Pushing image to Docker Hub..."
                // Safely extract username and password fields directly through Jenkins engine mapping
                withCredentials([usernamePassword(credentialsId: 'dockerhub-credentials', usernameVariable: 'USER', passwordVariable: 'PASS')]) {
                    sh '''
                        echo "$PASS" | docker login -u "$USER" --password-stdin
                        docker push ${FULL_IMAGE}
                        docker push ${DOCKERHUB_USER}/${IMAGE_NAME}:latest
                        docker logout
                    '''
                }
            }
        }

        // ---------- Stage 5: Deploy using docker-compose ----------
        stage('Deploy') {
            steps {
                echo "🚀 Deploying new version..."
                sh '''
                    # Clear out older standalone container conflicts if they exist
                    docker rm -f db web || true
                    
                    # Run the compose engine
                    docker compose down || true
                    docker compose up -d --build
                    sleep 10
                    docker compose ps
                '''
            }
        }

        // ---------- Stage 6: Verify deployment ----------
        stage('Verify') {
            steps {
                echo "✅ Verifying deployment..."
                sh '''
                    for i in {1..10}; do
                        if curl -fsS http://localhost:5000/health; then
                            echo "App is UP and Healthy!"
                            exit 0
                        fi
                        echo "Waiting for app... ($i/10)"
                        sleep 3
                    done
                    echo "App failed to pass Healthcheck verification!"
                    docker compose logs
                    exit 1
                '''
            }
        }
    }

    post {
        success {
            echo "✅ Build #${BUILD_NUMBER} SUCCEEDED!"
        }
        failure {
            echo "❌ Build #${BUILD_NUMBER} FAILED!"
            sh 'docker compose logs || true'
        }
        always {
            echo "🧹 Cleaning up old Docker images..."
            sh 'docker image prune -f || true'
        }
    }
}
