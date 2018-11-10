# Do webcam stuff
#

# can't use onbuild due to SSL visibility
FROM python:3.7

RUN apt-get update && apt-get install -y rsync

WORKDIR /usr/share/ca-certificates/extra
ADD support/DOIRootCA2.cer DOIRootCA2.crt
RUN echo "extra/DOIRootCA2.crt" >> /etc/ca-certificates.conf && update-ca-certificates

ENV SUPERCRONIC_URL=https://github.com/aptible/supercronic/releases/download/v0.1.6/supercronic-linux-amd64 \
    SUPERCRONIC=supercronic-linux-amd64 \
    SUPERCRONIC_SHA1SUM=c3b78d342e5413ad39092fd3cfc083a85f5e2b75

RUN curl -fsSLO "$SUPERCRONIC_URL" \
 && echo "${SUPERCRONIC_SHA1SUM}  ${SUPERCRONIC}" | sha1sum -c - \
 && chmod +x "$SUPERCRONIC" \
 && mv "$SUPERCRONIC" "/usr/local/bin/${SUPERCRONIC}" \
 && ln -s "/usr/local/bin/${SUPERCRONIC}" /usr/local/bin/supercronic

ENV CONFIGUPDATER_CONFIG=/tmp/configupdater.yaml

WORKDIR /app/camcommander
ADD requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

ADD VERSION .
ADD support/launch.sh .
ADD support/cron-camcommander .
RUN chmod 755 *.sh

WORKDIR /app/build
ADD . .
RUN ls
RUN python setup.py install

#CMD ["supervisord /app/camcommander/supervisord.conf"]
CMD ["ping -i 1 localhost"]
