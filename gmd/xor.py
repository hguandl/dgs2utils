class XOR(object):
    key1 = b"e43bcc7fcab+a6c4ed22fcd433/9d2e6cb053fa462-463f3a446b19"
    key2 = b"861f1dca05a0;9ddd5261e5dcc@6b438e6c.8ba7d71c*4fd11f3af1"

    @staticmethod
    def dexor(text: bytes) -> bytes:
        last_byte = text[-1]
        if last_byte == 0:
            return text

        check = (
            last_byte
            ^ XOR.key1[(len(text) - 1) % len(XOR.key1)]
            ^ XOR.key2[(len(text) - 1) % len(XOR.key2)]
        )
        if check != 0:
            raise ValueError("Cannot dexor")

        ret = list()
        for i in range(len(text)):
            b = text[i]
            b = (
                b
                ^ XOR.key1[i % len(XOR.key1)]
                ^ XOR.key2[i % len(XOR.key2)]
            )
            ret.append(b)
        return bytes(ret)

    @staticmethod
    def rexor(text: bytes) -> bytes:
        ret = list()
        for i in range(len(text)):
            b = text[i]
            b = (
                b
                ^ XOR.key1[i % len(XOR.key1)]
                ^ XOR.key2[i % len(XOR.key2)]
            )
            ret.append(b)
        return bytes(ret)
