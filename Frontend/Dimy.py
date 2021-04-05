import BloomFilter


def main():
    print("[>>] Running")
    dbf_1 = BloomFilter.DailyBloomFilter("DBF1")
    dbf_1.update_age()
    print(dbf_1.age)


if __name__ == '__main__':
    main()
