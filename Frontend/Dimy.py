import BloomFilter
import EphID

'''
TEST CODE ONLY
'''


def run_tests():
    print("=" * 10, " Select a test suite ", "=" * 10, "\n")
    print("[1] EphID Test")
    print("[2] Broadcast / Receive shares test")
    print("[3] EncID Exchange test")
    print("[4] Bloom Filter tests")
    print("[5] Full Operations Test (Requires secondary client)")
    print("[6] Quit")
    test_selection = int(input("[>>] "))

    None if test_selection != 6 else exit(0)

    print("\n[>>] Running tests, pray ...\n")

    if test_selection == 1 or test_selection == 5:
        print("=" * 10, "EphID Tests", "=" * 10)
        print("[**] Generating new EphID")
        eph_id_runner = EphID.EphIDRunner("EphIDRunner")
        eph_id_runner.start()
        # TODO: Thread never returns
        eph_id_runner.join()
        print("=" * (20 + len(" EphID Tests ")), "\n")
        run_tests() if test_selection != 5 else None  # test done

    if test_selection == 4 or test_selection == 5:
        print("=" * 11, "DBF Tests", "=" * 11)
        print("[**] Creating DBF")
        dbf_1 = BloomFilter.DailyBloomFilter("DBF1")
        print(f"[**] Created {dbf_1.name}")
        print(f"[**] Updating {dbf_1.name}'s age")
        dbf_1.update_age()
        print(f"[**] {dbf_1.name} AGE: {dbf_1.age}")
        print("=" * (22 + len(" DBF Tests ")), "\n")
        run_tests() if test_selection != 5 else None  # test done


def main():
    print("[>>] Running DIMY\n")

    # ========== TESTS ============ #
    run_tests()
    #################################


if __name__ == '__main__':
    main()
