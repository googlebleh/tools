FROM archlinux

ARG uname=user
ARG gname=host_users
ARG uhome=/home/$uname

RUN pacman -Sy --noconfirm --needed \
	base-devel git wget bash-completion \
	vim ripgrep ctags
RUN groupadd -g 100 $gname
RUN useradd -m -u 23055 -g $gname $uname
RUN echo "$uname ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

USER "$uname"

RUN mkdir -p $HOME/setup_sw/aur
RUN git clone \
	--depth 1 \
	https://aur.archlinux.org/paru.git \
	$HOME/setup_sw/aur/paru
WORKDIR $uhome/setup_sw/aur/paru
RUN makepkg -sir --noconfirm

RUN mkdir -p $HOME/repos
RUN git clone \
	--depth 1 \
	https://github.com/googlebleh/configs.git \
	$HOME/repos/configs
WORKDIR $uhome/repos/configs
RUN ./install.sh $HOME/repos/configs
# RUN vim +PlugInstall +qall
RUN sed -i 's/^colorscheme jellybeans/colorscheme desert/' ~/.vimrc
RUN echo "source ~/repos/configs/bash_ps1.sh" >> ~/.bashrc
RUN echo "PROMPT_COMMAND=bash_ps1_color" >> ~/.bashrc
ENV TERM=xterm-256color

# drop passwordless sudo
# RUN sudo sed -i '$ d' /etc/sudoers

WORKDIR $uhome
