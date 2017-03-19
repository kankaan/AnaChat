FROM python:3-onbuild
MAINTAINER Antti K
EXPOSE 5000
CMD [ "python", "./run.py" ]
