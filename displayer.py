from decode_tools import align_full_width, remove_double_colored
import re

PAGE_BREAK = b"\xff\xff\xff"
CURSOR_MOVE_PATTERN_PREFIX = re.compile(rb'^\x1B\[(\d*);(\d*)H')
CURSOR_MOVE_PATTERN = re.compile(rb'\x1B\[(\d*);(\d*)H')

class Displayer:
    def __init__(self):
        self.buffer = b""
        self.cursor_position = (1, 1)
        self.bytes_to_int = lambda x : int(x) if x != b"" else 1
    
    def display_output(self):
        content = remove_double_colored(self.buffer)
        plain_text = "".join(content.decode("big5hkscs", errors="ignore"))
        processed_text = align_full_width(plain_text)
        print(b"\x1b[2J".decode())  # Clear last page
        print(processed_text, end="")

    def display_bbs_data(self, data, fixed = False):
        data = data.strip(b"\r\n")
        if len(data) == 0 :
            print("End.")
            return
        self.detect_cursor_position(data)
        if not fixed:
            self.scroll()
        self.buffer += data
        self.display_output()
    
    def detect_cursor_position(self, data):
        match = CURSOR_MOVE_PATTERN_PREFIX.match(data)
        if match:
            self.cursor_position = list(map(self.bytes_to_int, match.groups()))

    def scroll(self):
        """Adjust `ESC[<number>;<number>H` row numbers to account for scrolling effects."""
        segments = CURSOR_MOVE_PATTERN.split(b"\x1B[1;1H" + self.buffer)  # Split on ESC[x;yH
        adjusted_segments = [segments.pop(0)]
        for i in range(0, len(segments), 3):
            row, col = map(self.bytes_to_int, segments[i:i+2])
            text_splitted = segments[i+2]
            new_row = row + self.cursor_position[0] - 24
            if new_row < 1:
                lines = text_splitted.split(b"\n")
                text_splitted = b"\n".join(lines[abs(new_row)+1:])
                new_row, col = 1, 1
            
            adjusted_segments.append(f"\x1B[{new_row};{col}H".encode()) # Scrolled position
            adjusted_segments.append(text_splitted)

        self.buffer = b"".join(adjusted_segments)

if __name__ == "__main__":
    # Run the displayer
    displayer = Displayer()
    filename = f"bbs_posts/kuku-0.bin"
    with open(filename, "rb") as file:
        post = file.read() 
        pages = post.split(b"\xff\xff\xff")
        for page in pages:
            displayer.display_bbs_data(page)
            input("\n[Enter Anything to Continue]")