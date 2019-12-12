FROM raspbian:openvino
LABEL maintainer="AWL"
LABEL email="awl@co.jp"

USER root

COPY requirements.txt ./

COPY lib_install_default.sh .
COPY lib_install_wget.sh .

RUN if ! sh ./lib_install_default.sh ; then sh ./lib_install_wget.sh ; fi

USER ${USER}
WORKDIR ${AWL_DIR}

COPY . .
RUN chmod +x entrypoint.sh
RUN sudo ln -f entrypoint.sh /bin/entrypoint.sh

EXPOSE 5559

CMD tail -f /dev/null