from collections import Counter
import math
import os

def ip_entropy(subscriber_ips):
    if not subscriber_ips:
        return 0
    counts = Counter(subscriber_ips)
    total = sum(counts.values())
    entropy = -sum((c/total) * math.log2(c/total) for c in counts.values())
    return entropy