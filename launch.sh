#!/bin/sh

groupadd -g $CAMCOMMANDER_GROUPID camcmdr
useradd -u $CAMCOMMANDER_USERID -g camcmdr -d /tmp/camcommander/svn camcmdr
su --preserve-environment camcmdr -c "/usr/local/bin/supercronic /app/camcommander/cron-camcommander"
