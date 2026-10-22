#!/bin/bash
# recovery helper: rebuilds build/raster.sh after a sandbox restart wipes build/.
# build/raster.sh is an ignored artifact; its content lives here so recovery never
# depends on something that only existed in a dead process's shell history.
cd "$(dirname "$0")/.."
mkdir -p build
cat > build/raster.sh <<'INNER'
#!/bin/bash
cd "$(dirname "$0")/.."
fails=0; n=0
raster(){ rsvg-convert -w "$2" -h "$3" "$1" -o "drawings/png/$(basename "${1%.svg}").png" || { echo "FAIL $1"; fails=$((fails+1)); }; n=$((n+1)); }
while IFS= read -r f; do raster "$f" 2560 1440; done < <(ls drawings/svg/CS-*.svg 2>/dev/null)
while IFS= read -r f; do raster "$f" 3840 2160; done < <(ls drawings/svg/HM-*.svg 2>/dev/null)
while IFS= read -r f; do raster "$f" 1920 1080; done < <(ls drawings/svg/LP-*.svg 2>/dev/null)
echo "rasterised $n sheets, $fails failures"
[ $fails -eq 0 ] || exit 1
INNER
echo "build/raster.sh written"
