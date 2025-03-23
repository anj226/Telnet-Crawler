# Telnet-Crawler  
A tool to download and read posts from a BBS server via Telnet.  

## Downloading from the BBS Server  
1. Edit `example-config.txt` and rename it to `config.txt`.  
2. In `telnet_reader.py` (line 138), update the board index to specify which board you want to download from.  
3. Run:  
   ```sh
   python3 telnet_reader.py
   ```
4. The downloaded content will be saved in:  
   ```
   ./bbs_posts/<boardname>-0.bin
   ```

## Reading Downloaded Content  
1. In `display.py` (line 58), update the filename to match the content you just downloaded.  
2. Run:  
   ```sh
   python3 display.py
   ```