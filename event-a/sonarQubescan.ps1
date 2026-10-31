docker run --rm `
  -e SONAR_HOST_URL="http://host.docker.internal:9000" `
  -e SONAR_TOKEN="$env:SONAR_TOKEN" `
  -v "${PWD}:/usr/src" `
  sonarsource/sonar-scanner-cli `
  "-Dsonar.projectKey=PROJECT-TICKET-LTD-BASE" `
  "-Dsonar.sources=." `
  "-Dsonar.java.binaries=out" `
  "-Dsonar.exclusions=out/**,.scannerwork/**"