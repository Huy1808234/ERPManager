"""
Utility module for VLXD Thống Nhất
Converts numerical amounts to Vietnamese words (Số thành Chữ).
Example: 5000000 -> "Năm triệu đồng"
"""

def num2vietnamese_words(n):
    try:
        n = int(round(float(n)))
    except (ValueError, TypeError):
        return ""

    if n == 0:
        return "Không đồng"
    if n < 0:
        return "Âm " + num2vietnamese_words(-n).lower()

    units = ["", "ngàn", "triệu", "tỷ", "ngàn tỷ", "triệu tỷ"]
    digits = ["không", "một", "hai", "ba", "bốn", "năm", "sáu", "bảy", "tám", "chín"]

    def read_block(b, is_highest):
        hundreds = b // 100
        tens = (b % 100) // 10
        ones = b % 10
        res = []

        if hundreds > 0 or not is_highest:
            res.append(digits[hundreds] + " trăm")

        if tens == 0:
            if ones > 0 and (hundreds > 0 or not is_highest):
                res.append("lẻ")
        elif tens == 1:
            res.append("mười")
        else:
            res.append(digits[tens] + " mươi")

        if ones == 1:
            if tens > 1:
                res.append("mốt")
            else:
                res.append("một")
        elif ones == 5:
            if tens > 0:
                res.append("lăm")
            else:
                res.append("năm")
        elif ones > 0:
            res.append(digits[ones])

        return " ".join(res)

    blocks = []
    temp = n
    while temp > 0:
        blocks.append(temp % 1000)
        temp //= 1000

    read_parts = []
    for i in range(len(blocks) - 1, -1, -1):
        b = blocks[i]
        if b > 0:
            part = read_block(b, i == len(blocks) - 1)
            if units[i]:
                part += " " + units[i]
            read_parts.append(part)

    result = " ".join(read_parts).strip()
    if not result:
        return "Không đồng"
    
    result = result[0].upper() + result[1:] + " đồng"
    return result

if __name__ == "__main__":
    print("5000000 ->", num2vietnamese_words(5000000))
    print("5078000 ->", num2vietnamese_words(5078000))
