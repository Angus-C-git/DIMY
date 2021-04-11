import BloomFilter
import EphID


def test_threads():
    receiver_thread = Thread(target=Network.receive_shares(), args=())
    receiver_thread.daemon = True
    receiver_thread.start()


'''
Test Driver for DIMY functions.
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
        eph_id = EphID.EphID()
        print(f"[**] Created EphID: {eph_id.eph_id}")
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
