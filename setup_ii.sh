echo "Setting ip ii"
echo "Putting obesstions.txt at $HOME"
cp ./data/obessions.txt $HOME/obessions.txt
echo "Putting ii in $HOME/bin"
cp ./src/ii.pl $HOME/bin/ii
echo "Setting 774 permissions to ii"
chmod 774 $HOME/bin/ii 
