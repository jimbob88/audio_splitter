ls family_1.2_deu*.mp3 | \
    sed -e "s/\(.*\)/file '\1'/" | \
    ffmpeg -protocol_whitelist 'file,pipe' -f concat -i - -c copy output.mp3