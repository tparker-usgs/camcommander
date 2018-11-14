#!/bin/sh

VERSION=`python -c "import camcommander; print(camcommander.__version__)"`
echo $VERSION
git add camcommander/__init__.py
git commit -m 'version bump'
git push \
&& git tag $VERSION \
&& git push --tags
