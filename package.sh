rm -f trap.opk
rm -f src/*.pyc
chmod +x src/main.py
mksquashfs . trap.opk -all-root -noappend -no-exports -no-xattrs
