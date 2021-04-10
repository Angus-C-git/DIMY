import BloomFilter

'''
TEST CODE ONLY
'''


def run_tests():
    print("[>>] Running tests in debug mode, pray ...\n")

    print("=" * 10, "DBF Tests", "=" * 10)
    print("[**] Creating DBF")
    dbf_1 = BloomFilter.DailyBloomFilter("DBF1")
    print(f"[**] Created {dbf_1.name}")
    print(f"[**] Updating {dbf_1.name}'s age")
    dbf_1.update_age()
    print(f"[**] {dbf_1.name} AGE: {dbf_1.age}")


def main():
    print("[>>] Running DIMY\n")

    ############# TESTS #############
    run_tests()
    ################################


if __name__ == '__main__':
    main()
