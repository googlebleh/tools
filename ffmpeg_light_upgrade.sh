#!/bin/bash

set -e

SWSETUP_ROOT="$HOME/Downloads/sw_setup"
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
# sudo apt update
# sudo apt -y install --only-upgrade autoconf automake build-essential \
#   libass-dev libfreetype6-dev libsdl1.2-dev libtheora-dev libtool libva-dev \
#   libvdpau-dev libvorbis-dev libxcb1-dev libxcb-shm0-dev libxcb-xfixes0-dev \
#   pkg-config texinfo zlib1g-dev yasm libx264-dev libx265-dev libfdk-aac-dev \
#   libmp3lame-dev libopus-dev libvpx-dev

# FFmpeg
cd "$FF_SOURCES/FFmpeg"
git pull
# PATH="$HOME/bin:$PATH" PKG_CONFIG_PATH="$FF_BUILD/lib/pkgconfig" ./configure \
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
  --enable-nonfree
  # --enable-libx265 \
PATH="$HOME/bin:$PATH" make -j
make install
#make distclean
hash -r

# Delete unneeded backups
rm -r $BIN_BACKUP

echo "FFmpeg updated"
