from bitarray.util import rindex

import BloomFilter
import EphID
import Network  # TODO: Import necessary only

import time

PROD = 0
TEST = 1
# SECTION_HEAD = 30

'''
Print Banner Art



_|_|_|    _|_|_|  _|      _|  _|      _|  
_|    _|    _|    _|_|  _|_|    _|  _|    
_|    _|    _|    _|  _|  _|      _|      
_|    _|    _|    _|      _|      _|      
_|_|_|    _|_|_|  _|      _|      _|      
'''


def print_banner():
    space = 10
    print(' ' * space, '_|_|_|    _|_|_|  _|      _|  _|      _|  ')
    print(' ' * space, '_|    _|    _|    _|_|  _|_|    _|  _|    ')
    print(' ' * space, '_|    _|    _|    _|  _|  _|      _|  ')
    print(' ' * space, '_|    _|    _|    _|      _|      _|  ')
    print(' ' * space, '_|_|_|    _|_|_|  _|      _|      _| ')


'''
Test Driver for DIMY functions.
'''


def run_tests():
    print("=" * 10, " Select a test suite ", "=" * 10, "\n")
    print("[0] Rebind Port")
    print("[1] EphID Test")
    print("[2] Broadcast / Receive shares test")
    print("[3] EncID Exchange test")
    print("[4] Bloom Filter tests")
    print("[5] Full Operations Test (Requires secondary client)")
    print("[6] EphID Core Exchange Test")
    print("[7] Run Assignment Line")
    print("[8] QBF & CBF Upload Test")
    print("[9] Quit")
    test_selection = int(input("[>>] "))

    if test_selection == 7:
        return

    None if test_selection != 9 else exit(0)

    print("\n[>>] Running tests, pray ...\n")

    if test_selection == 1 or test_selection == 5:
        print("=" * 10, "EphID Tests", "=" * 10)
        print("[**] Generating new EphID")
        eph_id = EphID.EphID("EPH_ID")
        eph_id_runner = EphID.EphIDRunner("EphIDRunner", eph_id)
        eph_id_runner.start()
        # TODO: Thread never returns
        eph_id_runner.join()
        print("=" * (20 + len(" EphID Tests ")), "\n")
        run_tests() if test_selection != 5 else None  # test done

    if test_selection == 0:
        Network.PORT = int(input("New Client Port: "))
        run_tests()

    if test_selection == 2 or test_selection == 5:
        print("=" * 10, "Shamir Test", "=" * 10)

        print(f"[**] Spinning up threads")
        # eph_id_runner = EphID.EphIDRunner("EPH_ID_THREAD")
        # time.sleep(1)

        receiver_thread_1 = Network.ReceiverRunner("RECEIVER_THREAD", 1)
        receiver_thread_1.start()

        broadcast_thread = Network.BroadcastRunner("BROADCAST_THREAD", ["share_1", "share_2", "share_3", "share_4"],
                                                   "HASH", 1)
        broadcast_thread.start()

        receiver_thread_1.join()
        broadcast_thread.join()
        print("=" * (20 + len(" Shamir Test ")), "\n")
        run_tests() if test_selection != 5 else None  # test done

    if test_selection == 4 or test_selection == 5:
        print("=" * 12, "BF Tests", "=" * 12)

        # - DBF TESTS - #
        TEST_ENC_ID = '0e2fac609122f7f241ed1a969b5e02af'
        print("[**] Starting DBF manager")
        dbfRunner = BloomFilter.DBFManager("DBF_RUNNER_THREAD", 120)  # generate a new dbf every 60 sec
        dbfRunner.start()
        print("[**] Creating DBF")
        dbf_1 = BloomFilter.DailyBloomFilter("DBF1")
        print(f"[**] Created {dbf_1.name}")
        # TODO:::: This is fairly redundant test code
        print(f"[**] Updating {dbf_1.name}'s age")
        print(f"[**] {dbf_1.name} AGE: {dbf_1.age}")

        print(f"[**] Encoding test EncID: {TEST_ENC_ID}  into: {dbf_1.name}, with: {BloomFilter.HASH_ROUNDS} murmur "
              f"hashes")

        dbf_1.push(TEST_ENC_ID)

        # TODO: Find out how to print the set indexes
        print(f"[**] Current DBF State Post Insert: {[i[0] for i in enumerate(dbf_1.bit_array.tolist()) if i[1]]}")

        print("\n[**] Starting CBF/DBF Upload Tests")
        print(f"[**] Sending CBF with garbage data")
        Network.send_cbf("VGhlIHF1aWNrIGJyb3duIGZveCBqdW1wcyBvdmVyIHRoZSBsYXp5IGRvZy4=")

        print(f"[**] Sending QBF with garbage data")
        # Network.send_qbf("VGhlIHF1aWNrIGJyb3duIGZveCBqdW1wcyBvdmVyIHRoZSBsYXp5IGRvZy4=")

        print("=" * (22 + len(" DBF Tests ")), "\n")
        run_tests() if test_selection != 5 else None  # test done

    if test_selection == 6 or test_selection == 5:
        print("[**] Starting receiver ...")
        receiver_thread_1 = Network.ReceiverRunner("RECEIVER_THREAD", 0)
        receiver_thread_1.start()
        print("[**] Starting EphID Runner ...")

        eph_id = EphID.EphID("EPH_ID")
        # print("[**]")
        eph_id_runner = EphID.EphIDRunner("EPH_ID_THREAD", eph_id)
        print(f"[**] Regenerating EphIDs every {eph_id_runner.eph_clock} seconds")

        broadcast_thread = Network.BroadcastRunner("BROADCAST_THREAD", eph_id.n_shares, eph_id.current_eph_id_hash, 0)
        broadcast_thread.start()

        receiver_thread_1.join()
        broadcast_thread.join()

    if test_selection == 8:
        print("[**] Generating a 5 DBFs to upload ..")
        from copy import deepcopy
        for x in range(0, 5):
            curr_dbf = BloomFilter.DailyBloomFilter(f"DBF_{x}")
            BloomFilter.DEVICE_DBFS.append(curr_dbf)

        TEST_ENC_ID = '0e2fac609122f7f241ed1a969b5e02af'
        for dbf in BloomFilter.DEVICE_DBFS:
            dbf.push(TEST_ENC_ID)
            # print(f"DBF BIT ARRAY: {dbf.bit_array}")

        # for dbf in BloomFilter.DEVICE_DBFS:
        #     print(f"NAME: {dbf.name} BA: {dbf.bit_array}")

        # print("[**] Combining into QBF")
        BloomFilter.upload_qbf(1)

        # upload = str(input("Upload Close Contacts Y/n ? "))
        # if upload == "yes":
        cbf = BloomFilter.ContactBloomFilter("TEST_CBF")
        if cbf.decision == 'n':
            print("[>>] Contacts not uploaded")
        else:  # Send 2X
            BloomFilter.send_cbf(cbf.bit_array)
            # BloomFilter.send_cbf(cbf.bit_array)

        print("[**] Combining into QBF")
        BloomFilter.upload_qbf(1)

        run_tests()

    print("[>>] Finished tests!")


def run_asst_cycle():
    section_head = 30

    print_banner()
    print(f"\n\n[>>] Client Starting On Port {Network.PORT}, output is in 0xHex\n")

    print('\n<', ':' * section_head, '[TASK-1 :: SEGMENT-1 :: A]', ':' * section_head, '>\n')

    EPH_ID = EphID.EphID("EPH_ID")
    print(f"[>>] Generated New EphID: {EPH_ID.current_eph_id.hex()}")
    print(f"[>>] EphID Hash {hex(EPH_ID.current_eph_id_hash)}")

    print('\n<', ':' * section_head, '[TASK-2 :: SEGMENT-2 :: A]', ':' * section_head, '>\n')

    print(f"[>>] EphID Shares:\n")

    for share in EPH_ID.n_shares:
        print(f"    ‣ {share}")

    print('\n<', ':' * section_head, '[TASK-3 :: SEGMENT-3 :: A:B:C]', ':' * section_head, '>\n')

    EPH_RUNNER = EphID.EphIDRunner("EPH_ID_THREAD", EPH_ID)
    DBF_MANAGER = BloomFilter.DBFManager("DBF_MANGER_THREAD")  # Override default for testing
    QBF_MANAGER = BloomFilter.QBFManager("QBF_MANAGER_THREAD", 300)  # Every 300 seconds send query
    RECEIVER_SVR = Network.ReceiverRunner("RECEIVER_THREAD", PROD)
    BROADCAST_SVR = Network.BroadcastRunner("BROADCAST_THREAD", EPH_ID.n_shares, EPH_ID.current_eph_id_hash, PROD)

    EPH_RUNNER.start()
    DBF_MANAGER.start()
    QBF_MANAGER.start()
    RECEIVER_SVR.start()
    BROADCAST_SVR.start()

    # print("[>>] continued ...")

    # CREATE GENESIS DBF
    BloomFilter.DEVICE_DBFS.append(BloomFilter.DailyBloomFilter("genesis_from_cold_start"))

    # print(f"[**] Current DBF State Post Insert: {[i[0] for i in enumerate(dbf_1.bit_array.tolist()) if i[1]]}")


def main():
    print("[>>] Running ...\n")
    # ========== TESTS ============ #
    run_tests()
    #################################
    run_asst_cycle()


if __name__ == '__main__':
    main()
