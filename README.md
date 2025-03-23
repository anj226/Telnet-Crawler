# Telnet-Crawler
## Download from BBS server
1. Edit `example-config.txt` and readname it into `config.txt` 
2. In `telnet_reader.py` line 138, edit the index of the board you want to download.  
2. Run `python3 telnet_reader.py`.
The content will be downloaded at `./bbs_posts/<boardname>-0.bin`.

## Read from downloaded content
1. In `display.py` line 58, edit the filename as the content you just downloaded.
2. Run `python3 displayer.py`.