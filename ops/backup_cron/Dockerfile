FROM postgres:16-alpine

RUN apk add --no-cache bash ca-certificates coreutils aws-cli && update-ca-certificates

COPY backup.sh /backup.sh

ENTRYPOINT ["bash", "/backup.sh"]

