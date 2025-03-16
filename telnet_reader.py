from telnetlib import Telnet 
import getpass
import time
from pathlib import Path
import re
from decode_tools import remove_double_colored, align_full_width

# Constant & Settings
ENABLE_DISPLAY = True
KEY_LEFT, KEY_UP, KEY_RIGHT, KEY_DOWN = b'\xe0K', b'\xe0H', b'\xe0M', b'\xe0P'
with open("config.txt", "r") as f:
    ADDRESS = f.readline().strip()
    USER = f.readline().strip()
    PASSWORD = f.readline().strip()
    BOARD_IDX = int(f.readline().strip())

tn = Telnet(ADDRESS)

def display_output(text):
    """Display telnet output using blessed if enabled."""
    if ENABLE_DISPLAY:
        processed_text = align_full_width(text)
        print(processed_text, end="")

def read_telnet_output(delay_before_read=1, wait_for_bytes=b"", save_path="test.bin"):
    time.sleep(delay_before_read)
    content = b""
    if wait_for_bytes:
        content = tn.read_until(wait_for_bytes) + tn.read_very_eager()
    else:
        content = tn.read_some() + tn.read_very_eager()
    
    content = remove_double_colored(content)
    if save_path:
        with open(save_path, "ab") as f:
            f.write(content)
            
    text = content.decode("big5hkscs", errors="ignore")  # Convert big5hkscs bytes to string
    display_output(text)
    return text

print("Wating for connect ......")
read_telnet_output(wait_for_bytes=b"Login")
tn.write(f"{USER}\n{PASSWORD}\n".encode())

recv = read_telnet_output()
while "精華區與重要訊息" not in recv:   # Check for the main page
    if "(Y/N)" in recv:
        print( "========================================\n", recv)
        print()
        tn.write( f"{input('Enter Y or N: ')}\n".encode() )
    else:                   # avoiding 註冊選單、十大熱門主題 ......
        tn.write( b" " )
    recv = read_telnet_output()

def extract_board_name(text, post_number):
    """Extracts the board name associated with a given post number."""
    pattern = r"^.{1,2}\s*" + str(post_number) + r"\s+(\S+)"  # Match number + capture first non-space word
    match = re.search(pattern, text, re.MULTILINE)
    board_name = match.group(1) if match else None  # Return board name if found
    return re.sub(r'[\/:*?"<>|]', "_", board_name)

# select to the target board
def select_board(board_idx, from_favrotie = False):
    tn.write( ("f" if from_favrotie else "b\n").encode() )
    read_telnet_output()
    
    tn.write( f"{board_idx}\n".encode() )
    board_name = extract_board_name(
        read_telnet_output(),
        board_idx
    )
    tn.write( b"\n" )
    read_telnet_output(wait_for_bytes="文章列表".encode("big5hkscs"))
    return board_name

def copy_post(idx, save_dir):
    """Download and save a BBS post with structured naming using pathlib."""
    save_path = save_dir / f"{idx}.bin"

    tn.write(f"{idx}\n".encode())  # Select the post
    read_telnet_output(wait_for_bytes="文章列表".encode("big5hkscs"))
    tn.write(b"\n")  # Confirm selection
    recv = ""

    while "選讀" not in recv:  # Wait for the end of the post
        recv = read_telnet_output(delay_before_read=3, save_path=save_path)
        tn.write(b" ")  # Press space to load more content

    tn.write(b"q")  # Quit post view

def taversal_board(board_name, num = 10):
    save_dir = Path("bbs_posts") / board_name
    save_dir.mkdir(parents=True, exist_ok=True)  # Ensure directory exists
    for idx in range(1, num+1):
        if num > 100:
            sub_save_dir = save_dir / str((num + 99) // 100)
            sub_save_dir.mkdir(parents=True, exist_ok=True)  # Ensure directory exists
            copy_post(idx, sub_save_dir)
        else:
            copy_post(idx, save_dir)

board_name = select_board(BOARD_IDX)
taversal_board(board_name)

tn.close()