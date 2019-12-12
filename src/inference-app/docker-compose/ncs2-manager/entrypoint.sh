#!/bin/bash
sed "s|<INSTALLDIR>|${INTEL_OPENVINO_DIR}|" ${INTEL_OPENVINO_DIR}/bin/setupvars.sh > ${AWL_DIR}/setupvars.sh

chmod +x ${AWL_DIR}/setupvars.sh
source ${AWL_DIR}/setupvars.sh

python3 -u ${AWL_DIR}/run.py