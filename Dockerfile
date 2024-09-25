# Base Image
FROM nvidia/cuda:12.1.0-cudnn8-devel-ubuntu20.04
# FROM nvidia/cuda:12.6.0-cudnn-devel-ubuntu20.04

# Latch environment building
COPY --from=812206152185.dkr.ecr.us-west-2.amazonaws.com/latch-base-cuda:fe0b-main /bin/flytectl /bin/flytectl
WORKDIR /root

ENV VENV /opt/venv
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV PYTHONPATH /root
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y libsm6 libxext6 libxrender-dev build-essential procps rsync openssh-server

RUN apt-get install -y software-properties-common &&\
    add-apt-repository -y ppa:deadsnakes/ppa &&\
    apt-get install -y python3.9 python3-pip python3.9-distutils curl

RUN python3.9 -m pip install --upgrade pip && python3.9 -m pip install awscli

RUN curl -L https://github.com/peak/s5cmd/releases/download/v2.0.0/s5cmd_2.0.0_Linux-64bit.tar.gz -o s5cmd_2.0.0_Linux-64bit.tar.gz &&\
    tar -xzvf s5cmd_2.0.0_Linux-64bit.tar.gz &&\
    mv s5cmd /bin/ &&\
    rm CHANGELOG.md LICENSE README.md

COPY --from=812206152185.dkr.ecr.us-west-2.amazonaws.com/latch-base-cuda:fe0b-main /root/Makefile /root/Makefile
COPY --from=812206152185.dkr.ecr.us-west-2.amazonaws.com/latch-base-cuda:fe0b-main /root/flytekit.config /root/flytekit.config

WORKDIR /tmp/docker-build/work/

SHELL [ \
    "/usr/bin/env", "bash", \
    "-o", "errexit", \
    "-o", "pipefail", \
    "-o", "nounset", \
    "-o", "verbose", \
    "-o", "errtrace", \
    "-O", "inherit_errexit", \
    "-O", "shift_verbose", \
    "-c" \
]

ENV TZ='Etc/UTC'

ENV LANG='en_US.UTF-8'
ARG DEBIAN_FRONTEND=noninteractive

# Install system requirements
RUN apt-get update --yes && \
    xargs apt-get install --yes aria2 git wget unzip

# Install Miniconda
RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh && \
    bash miniconda.sh -b -p /root/miniconda && \
    rm miniconda.sh

# Install RFdiffusion
RUN git clone https://github.com/RosettaCommons/RFdiffusion.git

RUN cd RFdiffusion && \
    mkdir models && cd models && \
    aria2c -q -x 16 http://files.ipd.uw.edu/pub/RFdiffusion/6f5902ac237024bdd0c176cb93063dc4/Base_ckpt.pt && \
    aria2c -q -x 16 http://files.ipd.uw.edu/pub/RFdiffusion/e29311f6f1bf1af907f9ef9f44b8328b/Complex_base_ckpt.pt && \
    aria2c -q -x 16 http://files.ipd.uw.edu/pub/RFdiffusion/60f09a193fb5e5ccdc4980417708dbab/Complex_Fold_base_ckpt.pt && \
    aria2c -q -x 16 http://files.ipd.uw.edu/pub/RFdiffusion/74f51cfb8b440f50d70878e05361d8f0/InpaintSeq_ckpt.pt && \
    aria2c -q -x 16 http://files.ipd.uw.edu/pub/RFdiffusion/76d00716416567174cdb7ca96e208296/InpaintSeq_Fold_ckpt.pt && \
    aria2c -q -x 16 http://files.ipd.uw.edu/pub/RFdiffusion/5532d2e1f3a4738decd58b19d633b3c3/ActiveSite_ckpt.pt && \
    aria2c -q -x 16 http://files.ipd.uw.edu/pub/RFdiffusion/12fc204edeae5b57713c5ad7dcb97d39/Base_epoch8_ckpt.pt && \
    aria2c -q -x 16 http://files.ipd.uw.edu/pub/RFdiffusion/f572d396fae9206628714fb2ce00f72e/Complex_beta_ckpt.pt && \
    aria2c -q -x 16 http://files.ipd.uw.edu/pub/RFdiffusion/1befcb9b28e2f778f53d47f18b7597fa/RF_structure_prediction_weights.pt

RUN /root/miniconda/bin/conda create --name SE3nv python=3.9 -y && \
    /root/miniconda/bin/conda run --name SE3nv conda install pytorch torchvision torchaudio pytorch-cuda=12.1 -c pytorch -c nvidia -y && \
    /root/miniconda/bin/conda run --name SE3nv pip install hydra-core pyrsistent && \
    /root/miniconda/bin/conda run -n SE3nv conda install -c dglteam/label/th24_cu121 dgl

RUN cd RFdiffusion/env/SE3Transformer && \
    /root/miniconda/bin/conda run -n SE3nv pip install --no-cache-dir -r requirements.txt && \
    /root/miniconda/bin/conda run -n SE3nv python setup.py install && \
    cd ../.. && \
    /root/miniconda/bin/conda run -n SE3nv pip install -e . && \
    /root/miniconda/bin/conda run -n SE3nv pip install pandas

ENV DGLBACKEND=pytorch

# Latch SDK
# DO NOT REMOVE
RUN pip install latch==2.52.2
RUN mkdir /opt/latch

# Copy workflow data (use .dockerignore to skip files)
COPY . /root/

# Latch workflow registration metadata
# DO NOT CHANGE
ARG tag
# DO NOT CHANGE
ENV FLYTE_INTERNAL_IMAGE $tag

WORKDIR /root
