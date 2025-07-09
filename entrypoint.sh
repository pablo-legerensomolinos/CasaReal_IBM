if [[ -z "${DB_SSL_BASE64}" ]]; then
  # No defined
  echo "No DB_SSL_BASE64"
else
  export DB_SSL_SERVER_CERTIFICATE=/tmp/db2.cert
  echo -n "${DB_SSL_BASE64}" | base64 -d > ${DB_SSL_SERVER_CERTIFICATE}
fi

poetry run pro