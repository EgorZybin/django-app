from functools import cache


@cache
def factorial(n):
    if n < 2:
        return 1
    return n * factorial(n - 1)


def main():
    print(factorial(5))
    print(factorial(10))


if __name__ == "__main__":
    main()
