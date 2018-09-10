#!/bin/sh

git push \
&& git tag `cat VERSION` \
&& git push --tags
