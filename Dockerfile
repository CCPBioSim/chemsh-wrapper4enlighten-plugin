FROM ubuntu:21.04

RUN apt-get update; \
    DEBIAN_FRONTEND=noninteractive; \
    apt-get install -y --no-install-recommends \
            make=4.3-4ubuntu1 gcc-7=7.5.0-6ubuntu4 gfortran-7=7.5.0-6ubuntu4 \
            cmake=3.18.4-2ubuntu1 python3-dev=3.9.4-1 \
            python3-numpy=1:1.19.5-1ubuntu2 libblas-dev=3.9.0-3ubuntu2 \
            liblapack-dev=3.9.0-3ubuntu2 xz-utils=5.2.5-1.0build2

RUN update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-7 10
RUN update-alternatives --install /usr/bin/gfortran gfortran /usr/bin/gfortran-7 10

COPY dl_poly_4.09.tar.gz /bin
WORKDIR /bin
RUN tar -xzvf dl_poly_4.09.tar.gz
WORKDIR dl_poly_4.09/source
RUN ln -s ../build/Makefile_SRL2 Makefile; make FCFLAGS=-DSERIAL gnu

COPY dftbplus-21.1.x86_64-linux.tar.xz /bin
WORKDIR /bin
RUN tar -xvf dftbplus-21.1.x86_64-linux.tar.xz
RUN mkdir /bin/dftbplus-21.1.x86_64-linux/data
WORKDIR /bin/dftbplus-21.1.x86_64-linux/data
COPY mio-1-1.tar.xz ./
RUN tar -xvf mio-1-1.tar.xz

COPY chemsh-py.tar.gz /bin
WORKDIR /bin
RUN tar -xzvf chemsh-py.tar.gz
WORKDIR chemsh-py
RUN ./setup --fc gfortran --cc gcc --dl_poly /bin/dl_poly_4.09
RUN ln -s /bin/chemsh-py/bin/gnu/chemsh /bin/

# Ugly fix to make py-chemshell happy without user (no $HOME etc.)
RUN sed -i "s|path.expanduser('~')|'/tmp'|g" /bin/chemsh
RUN sed -i "s/getuser()/' '/g" /bin/chemsh

COPY qmmm.py /bin
RUN chmod +x /bin/qmmm.py
WORKDIR /tmp