# Telnet-Crawler  
A tool to download and read posts from a BBS server via Telnet.  

## Setup
1. Ensure Python 3 is installed.
2. If using Python 3.13+, install `telnetlib-313-and-up`:
   ```
   pip install pip install telnetlib-313-and-up
   ```
   (This is not needed for earlier Python 3 versions, as telnetlib is built-in.)

## Downloading from the BBS Server  
1. Edit `example-config.txt` and rename it to `config.txt`.  
2. In `telnet_reader.py` (line 160), update the board index to specify which board you want to download from.  
3. Run:  
   ```sh
   python3 telnet_reader.py
   ```
4. The downloaded content will be saved in:  
   ```
   ./bbs_posts/<board_name>
   ├── index.txt
   ├── <board_name>-0.bin
   ├── <board_name>-1.bin
   └── ...
   ```

## Reading Downloaded Content  
1. In `display.py` (line 53), update the `board_name` to match the content you just downloaded.  
2. Run:  
   ```sh
   python3 display.py
   ```