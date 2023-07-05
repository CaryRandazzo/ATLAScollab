FROM rootproject/root:6.26.06-conda

# RUN pip3 uninstall werkzeug && \
#     pip3 install -v https://github.com/pallets/werkzeug/archive/refs/tags/2.0.1.tar.gz
    # pip3 install werkzeug==2.0.1

RUN pip3 install \
    pandas \
    scipy \
    plotly \
    dash \
    dash-bootstrap-components

CMD ["python3", "/app/src/app.py"]
