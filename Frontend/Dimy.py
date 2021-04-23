import BloomFilter
import EphID
import random

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
        print("=" * 12, "BF Tests", "=" * 12)

        # - DBF TESTS - #
        print("[**] Starting DBF manager")
        dbfRunner = BloomFilter.DBFManager("DBF_RUNNER_THREAD", 15)  # generate a new dbf every 15 sec
        dbfRunner.start()
        print("[**] Creating DBF")
        dbf = BloomFilter.DailyBloomFilter("DBF")
        print(f"[**] Created {dbf.name}")
        test_enc_id = '5122ccacfe'
        print(f"[**] Encoding Encounter ID {test_enc_id}")
        dbf.push(test_enc_id)
        # TODO: DBF age is deprecated
        print(f"[**] Updating {dbf.name}'s age")
        dbf.update_age()
        print(f"[**] {dbf.name} AGE: {dbf.age}")
        # ---

        # - CBF TESTS - #
        print("[**] Creating 6 DBFs To Encode")

        for dbf in range(0, 6):
            # Create Objs
            BloomFilter.DEVICE_DBFS.append(BloomFilter.DailyBloomFilter(f"DBF_{dbf}"))
            print(f"[**] Adding DBF_{dbf}")
            # Insert random encIds
            BloomFilter.DEVICE_DBFS[dbf].push(str(hex(random.randint(10000, 400000)))[2:])

        cbf = BloomFilter.ContactBloomFilter("CBF")
        print("[**] Waiting ~15 seconds for DBF expiry test\n")

        dbfRunner.join()  # TODO: this will never rejoin

        print("=" * (22 + len(" bf Tests ")), "\n")
        run_tests() if test_selection != 5 else None  # test done


def main():
    print("[>>] Running DIMY\n")

    # ========== TESTS ============ #
    run_tests()
    #################################


if __name__ == '__main__':
    main()
