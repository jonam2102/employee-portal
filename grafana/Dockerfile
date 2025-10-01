FROM grafana/grafana:latest

COPY dashboards.yaml /etc/grafana/provisioning/dashboards/
COPY datasources.yaml /etc/grafana/provisioning/datasources/
COPY redis-dashboard.json /var/lib/grafana/dashboards/
COPY fastapi-dashboard.json /var/lib/grafana/dashboards/


# Expose Grafana's default port
EXPOSE 3000

# Start Grafana
CMD ["/run.sh"]