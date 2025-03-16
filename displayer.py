from decode_tools import align_full_width
def display_output(text):
    """Display telnet output using blessed if enabled."""
    processed_text = align_full_width(text)
    print(processed_text, end="")

def display_bbs_page(filename, lines_per_page=24):
    with open(filename, "rb") as file:
        while True:
            lines = []
            for _ in range(lines_per_page):
                line = file.readline()
                if not line:  # End of file
                    break
                line = line.decode("big5hkscs", "ignore") 
                lines.append(line)

            if not lines:  # No more content to display
                break

            display_output("".join(lines))  # Print the 24-line page
            input("\n[Press Enter to continue...]")  # Wait for user input before next page


# Run the displayer
for i in range(1, 11):
    display_bbs_page(f"bbs_posts/Jolie/{i}.bin")