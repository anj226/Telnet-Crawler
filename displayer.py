from decode_tools import align_full_width, remove_double_colored, POST_BREAK, PAGE_BREAK
import re

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
    # Initialize the displayer
    displayer = Displayer()
    board_name = "kuku"

    with open(f"bbs_posts/{board_name}/index.txt", "r") as index_file:
        posts = index_file.read().strip().split("\n")
        total_posts = len(posts)
        current_index = 0

        while True:
            print(b"\x1b[2J".decode())    # Clear terminal screen
            print(b"\x1b[1;1H".decode())  # Move to top
            for post in posts[current_index:current_index + 24]:
                print(post)

            user_input = input(
                "[Press Enter to continue, input a post index number to view a post, or 'q' to quit]\n"
            )

            if user_input == "":
                current_index += 24
                if current_index >= total_posts:
                    current_index = 0
            elif user_input.isdigit():
                post_index = int(user_input)
                if 0 <= post_index < total_posts:
                    file_path = f"bbs_posts/{board_name}/{board_name}-{post_index // 100}.bin"
                    with open(file_path, "rb") as file:
                        post = file.read().split(POST_BREAK)[post_index % 100]
                        pages = post.split(PAGE_BREAK)
                        for page in pages:
                            if page.strip(b"\r\n") == b"" : break
                            else:
                                displayer.display_bbs_data(page)
                                input("\n[Press Enter to continue to next page]\n")
                    print(b"\x1b[24;1H".decode())  # Move to bottom
                    input("\n[End of post. Press Enter to return]\n")
                else:
                    print("Invalid post index.")
            elif user_input.lower() == "q":
                break
            else:
                print("Invalid input.")