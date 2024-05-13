# cd ~

# sudo apt update && \
#     sudo apt upgrade -y &&\
#     sudo apt install -y wget build-essential zlib1g-dev libncurses-dev libgdbm-dev libssl-dev libsqlite3-dev libffi-dev libbz2-dev git && \
#     wget https://www.python.org/ftp/python/3.7.17/Python-3.7.17.tgz  && \
#     tar -xzf Python-3.7.17.tgz

cd ~/Python-3.7.17
# ./configure --enable-optimizations && \
#     make -j 2
    
# sudo chmod o+w /usr/local/bin
make install

cd ..

rm -rf Python-3.7.17.tgz Python-3.7.17


