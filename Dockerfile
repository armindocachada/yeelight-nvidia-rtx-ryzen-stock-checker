FROM python:3.9-rc-slim-buster

RUN TZ=Europe/London && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN apt-get -y update && apt-get -y install cron
RUN pip3 install yeelight
RUN pip3 install requests
RUN pip3 install bs4
RUN pip3 install pandas
COPY files/* /home/

#RUN chmod 755 /script.sh /entry.sh
RUN /usr/bin/crontab /home/crontab.txt

# Run the command on container startup
RUN touch /var/log/cron.log

CMD cron && tail -f /var/log/cron.log