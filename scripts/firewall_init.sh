# # cd ~

# # sudo apt update && \
# #     sudo apt upgrade -y &&\
# #     sudo apt install -y wget build-essential zlib1g-dev libncurses-dev libgdbm-dev libssl-dev libsqlite3-dev libffi-dev libbz2-dev git && \
# #     wget https://www.python.org/ftp/python/3.7.17/Python-3.7.17.tgz  && \
# #     tar -xzf Python-3.7.17.tgz

# # cd ~/Python-3.7.17
# # ./configure --enable-optimizations && \
# #     make -j 2
    
# # sudo make install

# # cd ..

# # rm -rf Python-3.7.17.tgz Python-3.7.17

# # sudo apt-get install -y openjdk-8-jdk
# # sudo apt-get install -y git zip unzip autoconf automake libtool curl zlib1g-dev swig build-essential

# sudo apt-get install -y python3-dev python3-pip python3-wheel
# # sudo python3.7 -m pip install --upgrade pip
# # sudo python3.7 -m pip install --user keras

# cd ~
# wget https://github.com/bazelbuild/bazel/releases/download/0.19.2/bazel-0.19.2-dist.zip
# mkdir Bazel-0-19.2
# cd Bazel-0-19.2
# unzip ../bazel-0.19.2-dist.zip

# sed -i  's/#error This code for 64 bit Unix.//g' ./src/tools/singlejar/mapped_file_posix.inc

# export BAZEL_JAVAC_OPTS="-J-Xmx1g"
# ./compile.sh

# sudo cp output/bazel /usr/local/bin

# cd $HOME
# git clone -b v1.13.2 --depth=1 https://github.com/tensorflow/tensorflow Tensorflow-1.13.2
cd ~/Tensorflow-1.13.2

# grep -Rl "lib64"| xargs sed -i 's/lib64/lib/g'

# export TF_NEED_CUDA=0
# export TF_NEED_AWS=0
# ./configure

# cd third_party/icu &&
# sed -i 's/e15ffd84606323cbad5515bf9ecdf8061cc3bf80fb883b9e6aa162e485aa9761/86b85fbf1b251d7a658de86ce5a0c8f34151027cc60b01e1b76f167379acf181/g' ./workspace.bzl

# cd ../..

# bazel build --config=noaws --config=nohdfs --config=nokafka --config=noignite --config=nonccl -c opt --verbose_failures //tensorflow/tools/pip_package:build_pip_package

# sudo python3.7 -m pip install wheel

# bazel-bin/tensorflow/tools/pip_package/build_pip_package /tmp/tensorflow_pkg

sudo python3.7 -m pip install --user /tmp/tensorflow_pkg/tensorflow-1.13.2-cp37-cp37m-linux_i686.whl
