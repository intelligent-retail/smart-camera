machine=$(uname -m)

wget https://www.piwheels.org/simple/numpy/numpy-1.16.1-cp35-cp35m-linux_${machine}.whl
pip install numpy-1.16.1-cp35-cp35m-linux_${machine}.whl
rm numpy-1.16.1-cp35-cp35m-linux_${machine}.whl

wget https://www.piwheels.org/simple/opencv-contrib-python/opencv_contrib_python-3.4.4.19-cp35-cp35m-linux_${machine}.whl
pip install opencv_contrib_python-3.4.4.19-cp35-cp35m-linux_${machine}.whl
rm opencv_contrib_python-3.4.4.19-cp35-cp35m-linux_${machine}.whl

wget https://www.piwheels.org/simple/scipy/scipy-1.3.0rc1-cp35-cp35m-linux_${machine}.whl
pip install scipy-1.3.0rc1-cp35-cp35m-linux_${machine}.whl
rm scipy-1.3.0rc1-cp35-cp35m-linux_${machine}.whl

wget https://www.piwheels.org/simple/pyzmq/pyzmq-17.0.0-cp35-cp35m-linux_${machine}.whl
python3 -m pip install pyzmq-17.0.0-cp35-cp35m-linux_${machine}.whl
rm pyzmq-17.0.0-cp35-cp35m-linux_${machine}.whl