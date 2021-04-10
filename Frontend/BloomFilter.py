# Static helper function to generate bf entries
def generate_bloom_hash(entry):
    return "hash" + entry


class BloomFilter:
    bit_array = []

    def __init__(self, name):
        self.name = name

    def push(self, entry):
        self.bit_array.append(generate_bloom_hash(entry))


class DailyBloomFilter(BloomFilter):
    age = 0

    def __init__(self, name):
        super().__init__(name)

    # Called once a day for expiry management
    def update_age(self):
        self.age += 1


class QueryBloomFilter(BloomFilter):
    def __init__(self, name):
        super().__init__(name)


# Combine DBFs into a CBF
class ContactBloomFilter(BloomFilter):
    def __init__(self, name, dbfs):
        super().__init__(name)
        self.bit_array.append(dbfs)  # TODO: will need more logic to handle this
