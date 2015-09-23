echo "Starting clipboard archiver damon"
echo "Putting clipboard-archiver-d in $HOME/bin"
cp ./src/clipboard_archiver_d.py $HOME/bin/clipboard-archiver-d
echo "Setting 774 permissions to clipboard-archiver-d"
chmod 774 $HOME/bin/clipboard-archiver-d
