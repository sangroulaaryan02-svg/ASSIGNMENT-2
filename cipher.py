def shift_within_range(char, start, end, amount):
  
    size = ord(end) - ord(start) + 1
    return chr((ord(char) - ord(start) + amount) % size + ord(start))


def transform_char(char, shift1, shift2, decrypt=False):
    
    direction = -1 if decrypt else 1

    if 'a' <= char <= 'n':
        amount = direction * (shift1 * shift2)
        return shift_within_range(char, 'a', 'n', amount)

    if 'o' <= char <= 'z':
        amount = direction * (-(shift1 + shift2))
        return shift_within_range(char, 'o', 'z', amount)

    if 'A' <= char <= 'M':
        amount = direction * (-shift1)
        return shift_within_range(char, 'A', 'M', amount)

    if 'N' <= char <= 'Z':
        amount = direction * (shift2 ** 2)
        return shift_within_range(char, 'N', 'Z', amount)

    if '0' <= char <= '9':
        amount = direction * (shift1 - shift2)
        return shift_within_range(char, '0', '9', amount)

    return char


def encrypt_file(shift1: int, shift2: int, input_path: str, output_path: str) -> None:
    with open(input_path, 'r', encoding='utf-8') as input_file:
        text = input_file.read()

    encrypted_text = ''.join(
        transform_char(char, shift1, shift2) for char in text
    )

    with open(output_path, 'w', encoding='utf-8') as output_file:
        output_file.write(encrypted_text)


def decrypt_file(shift1: int, shift2: int, input_path: str, output_path: str) -> None:
    with open(input_path, 'r', encoding='utf-8') as input_file:
        text = input_file.read()

    decrypted_text = ''.join(
        transform_char(char, shift1, shift2, decrypt=True) for char in text
    )

    with open(output_path, 'w', encoding='utf-8') as output_file:
        output_file.write(decrypted_text)


def verify_files(original_path: str, decrypted_path: str) -> bool:
    with open(original_path, 'r', encoding='utf-8') as original_file:
        original_text = original_file.read()

    with open(decrypted_path, 'r', encoding='utf-8') as decrypted_file:
        decrypted_text = decrypted_file.read()

    successful = original_text == decrypted_text

    if successful:
        print("Decryption successful.")
    else:
        print("Decryption unsuccessful.")

    return successful


def read_nonnegative_integer(prompt: str) -> int:
    while True:
        try:
            value = int(input(prompt))

            if value < 0:
                print("Please enter a non-negative integer.")
            else:
                return value

        except ValueError:
            print("Please enter a valid non-negative integer.")


def main():
    shift1 = read_nonnegative_integer("Enter shift1: ")
    shift2 = read_nonnegative_integer("Enter shift2: ")

    encrypt_file(shift1, shift2, "raw_text.txt", "encrypted_text.txt")
    decrypt_file(shift1, shift2, "encrypted_text.txt", "decrypted_text.txt")
    verify_files("raw_text.txt", "decrypted_text.txt")


if __name__ == "__main__":
    main()
