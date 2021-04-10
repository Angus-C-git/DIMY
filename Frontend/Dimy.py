import BloomFilter
import Network
# import threading
from threading import Thread


def test_threads():
    receiver_thread = Thread(target=Network.receive_shares(), args=())
    receiver_thread.daemon = True
    receiver_thread.start()


'''
TEST CODE ONLY
'''


def run_tests():
    print("[>>] Running tests in debug mode, pray ...\n")

    print("=" * 10, "Networking Tests", "=" * 10)
    print(f"[**] Spinning up receiver threads")

    receiver_thread_1 = Network.NetworkRunner("receiver_thread_1")
    # receiver_thread_2 = Network.NetworkRunner("receiver_thread_2")
    receiver_thread_1.start()
    # receiver_thread_2.start()

    print("[**] Spinning up broadcast threads")

    receiver_thread_1.join()
    # receiver_thread_2.join()

    print("=" * 10, "DBF Tests", "=" * 10)
    print("[**] Creating DBF")
    dbf_1 = BloomFilter.DailyBloomFilter("DBF1")
    print(f"[**] Created {dbf_1.name}")
    print(f"[**] Updating {dbf_1.name}'s age")
    dbf_1.update_age()
    print(f"[**] {dbf_1.name} AGE: {dbf_1.age}")


def main():
    print("[>>] Running DIMY\n")
    # ============ TESTS ===========
    run_tests()
    ################################


if __name__ == '__main__':
    main()
