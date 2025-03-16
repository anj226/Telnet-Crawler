import unicodedata
def remove_double_colored(text_bytes):
    """Decode byte sequence, handling 'double-colored' characters."""
    result = bytearray()  # We'll accumulate the decoded result here
    i = 0   # Pointer for reading the byte sequence

    while i < len(text_bytes):
        if 0x00 <= text_bytes[i] <= 0x7F:  # Valid single byte (ASCII range)
            result.append(text_bytes[i])
            i += 1
        elif i + 1 < len(text_bytes) and text_bytes[i+1] != 0x1B:  # Double bytes
            result.append(text_bytes[i])
            result.append(text_bytes[i+1])
            i += 2
        else: # Double bytes with control code in between
            result.append(text_bytes[i])
            i += 1
            
            # Match control code
            # CONTROL_CODE_PATTERN = re.compile(rb'\x1B\[[0-9;?]*[A-Za-z]')
            control_code = bytearray()
            while i < len(text_bytes) and (text_bytes[i] < 65 or 90 < text_bytes[i] < 97 or 122 < text_bytes[i]): # Check [A-Za-z]
                control_code.append(text_bytes[i])
                i += 1
            
            if i + 1 < len(text_bytes):
                control_code.append(text_bytes[i])
                result.append(text_bytes[i + 1])
                result.extend(control_code)
                i += 2

            else:
                # Error! Maybe just ignore this.
                pass

    return bytes(result)

def align_full_width(text_str):
    """Align full-width characters by adding a space after them."""
    aligned_text = []
    for char in text_str:
        aligned_text.append(char)
        if unicodedata.east_asian_width(char) in {"A"}:
            aligned_text.append(" ")  # Add a space after full-width characters
    return "".join(aligned_text)

if __name__ == "__main__":
    # Example usage
    raw_bytes = b'\xa3k\xa3\x1b[37mk\xa3k'
    text = remove_double_colored(raw_bytes).decode("big5hkscs")
    text = align_full_width(text)
    print(text)
