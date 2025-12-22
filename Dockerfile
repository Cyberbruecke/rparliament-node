FROM ubuntu:latest
#upgrade & python
RUN apt update && apt upgrade -y && apt autoremove -y && apt install -y curl python3 python3-pip

#vars
ARG D_DATA=/data
ARG D_OUT=$D_DATA/out
ENV D_RP_CACHE=$D_OUT/rpki-cache
ENV D_RP_OUT=$D_OUT/rpki-out
ENV D_SHARE=$D_OUT/share
ENV D_METRICS=$D_SHARE/metrics
ENV D_RP_TALS=$D_DATA/in/rpki-tals
ENV F_PEER_IP_LOG=/tmp/peer_ip_log

ENV RTR_REFRESH=30

#init
RUN mkdir -p $D_RP_OUT $D_RP_CACHE $D_RP_TALS $D_METRICS
RUN chmod 777 $D_RP_OUT
RUN ln -sf $D_RP_OUT/metrics $D_METRICS/rpki-client.metrics
RUN echo '{}' > $D_SHARE/master-vrp.json &&  \
    echo '{}' > $D_SHARE/vrp.json &&  \
    echo '{}' > /tmp/conn_state.json &&  \
    echo '{}' > /tmp/dnsbook.json &&  \
    echo '{}' > /tmp/skiplist_state.json &&  \
    touch $D_SHARE/skiplist.lst &&  \
    touch $D_SHARE/master-skiplist.lst

#stayrtr
COPY --from=rpki/stayrtr /stayrtr /bin/stayrtr

#rpki-client
RUN apt install -y curl rsync build-essential libssl-dev libtls-dev
RUN touch /etc/rsyncd.conf
RUN curl https://ftp.openbsd.org/pub/OpenBSD/rpki-client/$(curl https://ftp.openbsd.org/pub/OpenBSD/rpki-client/ | egrep -o "rpki-client-[0-9.]+.tar.gz" | tail -n 1) -o /root/rpki-client.tar.gz
RUN cd /root/ && tar -xzvf rpki-client.tar.gz && cd /root/rpki-client-* && ./configure --with-output-dir=$D_RP_OUT && make && rm /root/rpki-client.tar.gz
RUN useradd _rpki-client && passwd -d _rpki-client
RUN ln -s /root/rpki-client-*/src/rpki-client /bin/rpki-client
RUN cp /root/rpki-client-*/*.tal $D_RP_TALS
RUN chown -R _rpki-client:_rpki-client $D_RP_OUT $D_RP_TALS $D_RP_CACHE
RUN curl https://www.arin.net/resources/manage/rpki/arin.tal -o $D_RP_TALS/arin.tal
RUN touch $D_RP_OUT/metrics && chmod 644 $D_RP_OUT/*

#nginx
RUN apt install -y nginx
COPY /config/stayrtr-proxy.conf /etc/nginx/sites-enabled/stayrtr-proxy.conf
COPY /config/peering.conf /etc/nginx/sites-enabled/peering.conf
RUN ln -sf /dev/stdout /var/log/nginx/access.log && ln -sf /dev/stderr /var/log/nginx/error.log
RUN sed -i 's/user www-data;/user root;/' /etc/nginx/nginx.conf
RUN sed -i 's/http {/http {\n\tlog_format peer_ip_log '\$remote_addr';\n\taccess_log \/tmp\/peer_ip_log peer_ip_log;/' /etc/nginx/nginx.conf
RUN mkfifo $F_PEER_IP_LOG


#app
RUN apt install -y libpcap-dev lsof
COPY src/ /app/
RUN pip3 install --break-system-packages -r /app/requirements.txt

EXPOSE 8282
EXPOSE 4242

CMD ln -sf /proc/1/fd/1 /dev/stdout && \
    ln -sf /proc/1/fd/2 /dev/stderr && \
    cd /app/ && \
    python3 vars.py && \
    (python3 ip_reader.py &) && \
    nginx -t && \
    service nginx start && \
    (stayrtr -bind '' -tls.bind 0.0.0.0:8282 -tls.key /etc/ssl/private/rtr.key -tls.cert /etc/ssl/certs/rtr.crt -cache http://localhost/master-vrp.json -refresh $RTR_REFRESH &) && \
    (python3 -u monitored_rp.py &) && \
    python3 -u peering.py
