#!/bin/sh

groupadd -g $CAMCOMMANDER_GROUPID camcmdr
useradd -u $CAMCOMMANDER_USERID -g camcmdr -d /app/camcommander camcmdr
su - camcmdr -c /usr/local/bin/supercronic /app/camcommander/cron-camcommander
