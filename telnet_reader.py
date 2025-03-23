from telnetlib import Telnet 
import time
from pathlib import Path
import re
from decode_tools import remove_double_colored
from displayer import Displayer

class Telnet_Reader():
    def __init__(self):
        # Constant & Settings
        self.config_path = "config.txt"
        self.enable_display = True
        self.page_break = b"\xff\xff\xff"
        self.delay_before_read = 1

        self.read_config()
        self.displayer = Displayer()
        self.tn = None

    def read_config(self):
        with open(self.config_path, "r") as f:
            self.ADDRESS = f.readline().strip()
            self.USER = f.readline().strip()
            self.PASSWORD = f.readline().strip()
    
    def read_telnet_output(self, wait_for_bytes=b"", save_path = "", fixed = True):
        time.sleep(self.delay_before_read)
        content = b""
        if wait_for_bytes:
            content = self.tn.read_until(wait_for_bytes) + self.tn.read_very_eager()
        else:
            content = self.tn.read_some() + self.tn.read_very_eager()
        
        if save_path:
            with open(save_path, "ab") as f:
                f.write(content)
                f.write(self.page_break) # self-defined page break symbol

        if self.enable_display:
            self.displayer.display_bbs_data(content, fixed)
        
        # Convert big5hkscs bytes to string
        content = remove_double_colored(content)
        text = content.decode("big5hkscs", errors="ignore")
        return text
    
    def login(self):
        self.tn = Telnet(self.ADDRESS)
        print("Wating for connect ......")
        self.read_telnet_output(wait_for_bytes=b"Login")
        # TODO: getpass
        self.tn.write(f"{self.USER}\n{self.PASSWORD}\n".encode())


    def nevigate(self):
        recv = self.read_telnet_output()
        while "精華區與重要訊息" not in recv:   # Check for the main page
            if "(Y/N)" in recv:
                if not self.enable_display:
                    print( "========================================\n", recv)
                self.tn.write( (input('\n[Enter Y or N]') + "\n").encode() )
            else:                   # avoiding 註冊選單、十大熱門主題 ......
                self.tn.write( b" " )
            recv = self.read_telnet_output()
    
    @staticmethod
    def extract_board_name(text, board_idx):
        """Extracts the board name associated with a given board index."""
        pattern = r"^.{1,2}\s*" + str(board_idx) + r"\s+(\S+)" # Match number + capture first non-space word
        match = re.search(pattern, text, re.MULTILINE)
        board_name = match.group(1) if match else None  # Return board name if found
        return re.sub(r'[\/:*?"<>|]', "_", board_name)

    # select to the target board
    def select_board(self, board_idx, from_favrotie = False):
        self.tn.write( ("f" if from_favrotie else "b\n").encode() )
        
        recv = self.read_telnet_output()
        self.tn.write( f"{board_idx}\n".encode() )
        
        board_name = self.extract_board_name(
            recv + self.read_telnet_output(),
            board_idx
        )
        self.tn.write( b"\n" )
        self.read_telnet_output(
            wait_for_bytes="文章列表".encode("big5hkscs")
        )
        return board_name

    def copy_post(self, idx, save_path):
        """Download and save a BBS post with structured naming using pathlib."""
        self.tn.write(f"{idx}\n".encode())  # Select the post
        self.read_telnet_output(
            wait_for_bytes="文章列表".encode("big5hkscs")
        )
        self.tn.write(b"\n")  # Confirm selection
        recv = ""

        while "選讀" not in recv:  # Wait for the end of the post
            recv = self.read_telnet_output(save_path=save_path)
            self.tn.write(b" ")  # Press space to load more content

        self.tn.write(b"q")  # Quit post view

    # def taversal_board(self, board_name, max_num = 10):
    #     Path("bbs_posts").mkdir(parents=True, exist_ok=True)  # Ensure directory exists
    #     for idx in range(1, max_num+1):
    #         save_path = Path("bbs_posts") / (f"{board_name}-{str((max_num + 99) // 100)}.bin")
    #         # self.copy_post(idx, save_path)
    
    def taversal_board(self, board_name, max_post_num = 10):
        """Download and save a BBS post with structured naming using pathlib."""
        self.tn.write(b"1\n")  # To the top
        self.read_telnet_output(
            wait_for_bytes="文章列表".encode("big5hkscs")
        )
        self.tn.write(b"\n")  # Confirm selection
        
        i, recv = 0, ""
        while i < max_post_num:
            save_path = Path("bbs_posts") / (f"{board_name}-{i // 100}.bin")
            recv = self.read_telnet_output(save_path=save_path, fixed=False)
            self.tn.write(b" ")  # Press space to load more content
            if "選讀" in recv:  i += 1

            
    def download_board(self, board_idx):
        Path("bbs_posts").mkdir(parents=True, exist_ok=True)  # Ensure directory exists
        self.login()
        self.nevigate()
        board_name = self.select_board(board_idx)
        self.taversal_board(board_name)
        self.tn.close()

if __name__ == "__main__":
    reader = Telnet_Reader()
    reader.download_board(3) # The index of the board