def print_pyramid(layers):
    for i in range(layers):
        # 計算空格數量 (隨層數遞減) 與 當前層要顯示的數字 (由大到小)
        padding = " " * (layers - i - 1)
        digit = str(layers - 1 - i)
        row = " ".join([digit] * (i + 1))
        print(f"{padding}{row}")

if __name__ == "__main__":
    print_pyramid(5)
