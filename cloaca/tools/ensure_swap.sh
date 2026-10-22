#!/bin/bash
# Recovery step (C-022): the station gives no swap; big scenes (FIGURES.blend with scan
# textures) peak above available RAM during Cycles texture sync. A 4 GB swapfile absorbs
# the bursts. Recreate after every sandbox restart - it never survives.
if ! swapon --show | grep -q swapfile; then
  sudo fallocate -l 4G /swapfile && sudo chmod 600 /swapfile && sudo mkswap /swapfile >/dev/null && sudo swapon /swapfile
  echo "swapfile created"
else
  echo "swap already present"
fi
free -m | tail -1
