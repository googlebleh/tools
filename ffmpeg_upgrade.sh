#!/bin/bash

set -e

FF_ROOT="$HOME/Downloads/sw_setup/ff"
FF_BUILD="$FF_ROOT/build"
FF_SOURCES="$FF_ROOT/sources"
FF_INSTALL_PATH="$HOME/.local/bin"
BIN_BACKUP="$FF_INSTALL_PATH/ffbak"

# Backup old version
mkdir -p $BIN_BACKUP
for f in $FF_INSTALL_PATH/{ffmpeg,ffplay,ffprobe,ffserver}; do
    if [ -f $f ]; then
        mv $f $BIN_BACKUP
    fi
done
echo "Backed up ff binaries to" $BIN_BACKUP

# H.264 video encoder
cd $FF_SOURCES

exit

SWSETUP_ROOT=
FF_ROOT="$SWSETUP_ROOT/ff"
FF_BUILD="$FF_ROOT/ffmpeg_build"
FF_SOURCES="$FF_ROOT/ffmpeg_sources"
BIN_BACKUP="$HOME/bin/ffbak"

# Backup old version
mkdir -p $BIN_BACKUP
for f in ~/bin/{ffmpeg,ffplay,ffprobe,ffserver}
do
    if [ -f $f ]; then
        mv $f $BIN_BACKUP
    fi
done
echo "Backed up ff binaries to" $BIN_BACKUP

# Precompiled dependencies
sudo apt update
sudo apt -y install --only-upgrade autoconf automake build-essential \
  libass-dev libfreetype6-dev libsdl2-dev libtheora-dev libtool libva-dev \
  libvdpau-dev libvorbis-dev libxcb1-dev libxcb-shm0-dev libxcb-xfixes0-dev \
  pkg-config texinfo zlib1g-dev yasm libx264-dev libmp3lame-dev libopus-dev

# H.265/HEVC video encoder
cd "$FF_SOURCES/x265"
hg pull -u
cd "$FF_SOURCES/x265/build/linux"
PATH="$HOME/bin:$PATH" cmake -G "Unix Makefiles" -DCMAKE_INSTALL_PREFIX="$FF_BUILD" -DENABLE_SHARED:bool=off ../../source
make
make install

# AAC audio encoder
cd "$FF_SOURCES/fdk-aac"
git pull
autoreconf -fi
./configure --prefix="$FF_BUILD" --disable-shared
make
make install

# VP8/VP9 video encoder and decoder
cd "$FF_SOURCES/libvpx"
# git pull
PATH="$HOME/bin:$PATH" ./configure --prefix="$FF_BUILD" --enable-pic --disable-examples --disable-unit-tests --enable-vp9-highbitdepth
PATH="$HOME/bin:$PATH" make
make install

# FFmpeg
cd "$FF_SOURCES/FFmpeg"
git pull
PATH="$HOME/bin:$PATH" PKG_CONFIG_PATH="$FF_BUILD/lib/pkgconfig" ./configure \
  --prefix="$FF_BUILD" \
  --pkg-config-flags="--static" \
  --extra-cflags="-I$FF_BUILD/include" \
  --extra-ldflags="-L$FF_BUILD/lib" \
  --bindir="$HOME/bin" \
  --enable-gpl \
  --enable-libass \
  --enable-libfdk-aac \
  --enable-libfreetype \
  --enable-libmp3lame \
  --enable-libopus \
  --enable-libtheora \
  --enable-libvorbis \
  --enable-libvpx \
  --enable-libx264 \
  --enable-libx265 \
  --enable-nonfree \
  --enable-static
PATH="$HOME/bin:$PATH" make
make install
hash -r

# Delete unneeded backups
rm -r $BIN_BACKUP

echo "FFmpeg updated"
