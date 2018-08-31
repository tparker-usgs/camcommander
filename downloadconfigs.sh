#!/bin/sh

WGET="wget -O /tmp/wrp.yaml"
if [ "x$HTTP_USER" != x ]; then
    WGET="${WGET} --http-user=$HTTP_USER --http-passwd=$HTTP_PASSWD --auth-no-challenge"
fi

$WGET $WRP_CONFIG_URL
