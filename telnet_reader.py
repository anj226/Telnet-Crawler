from telnetlib import Telnet 
import getpass
import time

# Constant & Settings
ENABLE_DISPLAY = True
KEY_LEFT, KEY_UP, KEY_RIGHT, KEY_DOWN = b'\xe0K', b'\xe0H', b'\xe0M', b'\xe0P'
with open("config.txt", "r") as f:
    ADDRESS = f.readline().strip()
    USER = f.readline().strip()
    PASSWORD = f.readline().strip()
    BOARD_IDX = int(f.readline().strip())


tn = Telnet(ADDRESS)

def display_output(content):
    """Display telnet output using blessed if enabled."""
    if ENABLE_DISPLAY:
        processed_text = content.expandtabs(4)
        print(processed_text, end="")

def read_telnet_output(delay_before_read=1, wait_for_bytes=b"", save_path="test.bin"):
    time.sleep(delay_before_read)
    content = b""
    if wait_for_bytes:
        content = tn.read_until(wait_for_bytes) + tn.read_very_eager()
    else:
        content = tn.read_some() + tn.read_very_eager()
    
    if save_path:
        with open(save_path, "w") as f:
            f.write(content.decode("Big5", "ignore"))
    
    # Decode and display output
    if content:
        decoded_text = content.decode("big5", errors="ignore")  # Convert Big5 bytes to string
        display_output(decoded_text)  # Display with Blessed

    return content

print("Wating for connect ......")
read_telnet_output(wait_for_bytes=b"Login").decode("Big5", "ignore")

tn.write(f"{USER}\n{PASSWORD}\n".encode())
recv = read_telnet_output().decode("Big5", "ignore")
while "精華區與重要訊息" not in recv:   # Check for the main page
    if "(Y/N)" in recv:
        print( "========", recv)
        tn.write( f"{input('Enter Y or N: ')}\n".encode() )
    else:                   # avoiding 註冊選單、十大熱門主題 ......
        tn.write( b" " )
    recv = read_telnet_output().decode("Big5", "ignore")

# select to the target board
def select_board(board_idx, from_favrotie = False):
    tn.write( ("f" if from_favrotie else "b\n").encode() )
    read_telnet_output()
    
    tn.write( f"{board_idx}\n".encode() )
    read_telnet_output()

    tn.write( b"\n" )
    read_telnet_output()

def copy_post(idx):
    tn.write( f"{idx}\n\n".encode() )
    recv = ""
    # "瀏覽 P.x (x%)" or "文章選讀"
    while "選讀" not in recv:   # Check for the page end
        recv = read_telnet_output(save_path=f"./board_1/{idx}.bin").decode("Big5", "ignore")
        tn.write( b" " )
    tn.write( KEY_LEFT )

def taversal_board(num = 10):
    for idx in range(1, num+1):
        copy_post(idx)
    
select_board(BOARD_IDX)
taversal_board()

tn.close()