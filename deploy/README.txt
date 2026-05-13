Optional Aiven CA certificate for TLS verification:

  Save the CA file from Aiven Console (Overview → download CA) as:

    aiven-ca.pem

  in this folder, then on Render set:

    MYSQL_SSL_CA=/app/deploy/aiven-ca.pem
    MYSQL_USE_SSL=true

  Do not commit secrets. Committing only the Aiven project CA is a team choice;
  prefer MYSQL_SSL_CA_PEM on Render for private repos.
