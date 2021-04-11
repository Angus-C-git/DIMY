import BloomFilter
import EphID
import Network

import time

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

    if test_selection == 2 or test_selection == 5:
        print("=" * 10, "Shamir Test", "=" * 10)

        print(f"[**] Spinning up threads")

        receiver_thread_1 = Network.ReceiverRunner("RECEIVER_THREAD", 1)
        receiver_thread_1.start()

        broadcast_thread = Network.BroadcastRunner("BROADCAST_THREAD", ["share_1", "share_2", "share_3", "share_4"], 1)
        broadcast_thread.start()

        receiver_thread_1.join()
        broadcast_thread.join()
        print("=" * (20 + len(" Shamir Test ")), "\n")
        run_tests() if test_selection != 5 else None  # test done

    if test_selection == 4 or test_selection == 5:
        print("=" * 11, "DBF Tests", "=" * 11)
        print("[**] Creating DBF")
        dbf_1 = BloomFilter.DailyBloomFilter("DBF1")
        print(f"[**] Created {dbf_1.name}")
        print(f"[**] Updating {dbf_1.name}'s age")
        dbf_1.update_age()
        print(f"[**] {dbf_1.name} AGE: {dbf_1.age}")

        print(f"[**] Sending CBF with garbage data")
        Network.send_cbf("VGhlIHF1aWNrIGJyb3duIGZveCBqdW1wcyBvdmVyIHRoZSBsYXp5IGRvZy4=")

        print(f"[**] Sending QBF with garbage data")
        Network.send_qbf("VGhlIHF1aWNrIGJyb3duIGZveCBqdW1wcyBvdmVyIHRoZSBsYXp5IGRvZy4=")

        print("=" * (22 + len(" DBF Tests ")), "\n")
        run_tests() if test_selection != 5 else None  # test done

    print("[>>] Finished tests!")


def main():
    print("[>>] Running DIMY\n")
    # ========== TESTS ============ #
    run_tests()
    #################################


if __name__ == '__main__':
    main()
