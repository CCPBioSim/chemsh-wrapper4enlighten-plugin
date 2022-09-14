FROM ubuntu:22.04 AS ubuntu-pychemsh-base

RUN apt-get update; \
    DEBIAN_FRONTEND=noninteractive; \
    apt-get install -y --no-install-recommends \
            make=4.3-4.1build1 gcc-9=9.4.0-5ubuntu1 gfortran-9=9.4.0-5ubuntu1 \
            cmake=3.22.1-1ubuntu1 python3-dev=3.10.4-0ubuntu2 \
            python3-numpy=1:1.21.5-1build2 libblas-dev=3.10.0-2ubuntu1 \
            liblapack-dev=3.10.0-2ubuntu1 xz-utils=5.2.5-2ubuntu1; \
    apt-get clean; \
    rm -rf /var/lib/apt/lists/*

RUN update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-9 10
RUN update-alternatives --install /usr/bin/gfortran gfortran /usr/bin/gfortran-9 10


FROM ubuntu-pychemsh-base AS ubuntu-pychemsh-build

COPY dftbplus-21.2.x86_64-linux.tar.xz /bin
WORKDIR /bin
RUN tar -xvf dftbplus-21.2.x86_64-linux.tar.xz
WORKDIR dftbplus-21.2.x86_64-linux/bin
RUN rm setupgeom waveplot modes phonons

RUN mkdir /bin/dftbplus-21.2.x86_64-linux/data
WORKDIR /bin/dftbplus-21.2.x86_64-linux/data
COPY mio-1-1.tar.xz ./
RUN tar -xvf mio-1-1.tar.xz; rm mio-1-1.tar.xz

COPY chemsh-py-master-20220913.tar.gz /bin
COPY dl-poly-devel-20220712.tar.gz /bin
WORKDIR /bin
RUN tar -xzvf chemsh-py-master-20220913.tar.gz
WORKDIR chemsh-py
RUN ./setup --fc gfortran --cc gcc --dl_poly /bin/dl-poly-devel-20220712.tar.gz
RUN rm -rf tests dev docs


FROM ubuntu-pychemsh-base

COPY --from=ubuntu-pychemsh-build /bin/dftbplus-21.2.x86_64-linux \
                                  /bin/dftbplus-21.2.x86_64-linux
COPY --from=ubuntu-pychemsh-build /bin/chemsh-py /bin/chemsh-py

RUN ln -s /bin/chemsh-py/bin/gnu/chemsh /bin/

# Ugly fix to make py-chemshell happy without user (no $HOME etc.)
RUN sed -i "s|path.expanduser('~')|'/tmp'|g" /bin/chemsh
RUN sed -i "s/getuser()/' '/g" /bin/chemsh

COPY qmmm.py /bin
RUN chmod +x /bin/qmmm.py
WORKDIR /tmp
