FROM rootproject/root:6.22.00-conda

RUN pip3 uninstall werkzeug && \
    pip3 install -v https://github.com/pallets/werkzeug/archive/refs/tags/2.0.1.tar.gz

RUN pip3 install \
    pandas \
    scipy \
    plotly \
    dash==1.19.0 \
    dash-core-components==1.15.0 \
    dash-html-components==1.1.2 \
    dash-bootstrap-components==0.11.1

CMD ["python3", "/app/src/app.py"]
