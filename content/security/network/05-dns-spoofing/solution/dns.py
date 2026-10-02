import struct


def parse_header(data):
    # Six big-endian 16-bit fields. The QR bit (top bit of flags) says whether
    # this is a query or a response.
    ident, flags, qd, an, ns, ar = struct.unpack("!HHHHHH", data[:12])
    return {"id": ident, "is_response": bool(flags >> 15 & 1),
            "questions": qd, "answers": an}


def accept_response(pending, response):
    # The whole defence: only believe an answer to a question you actually
    # asked. A forged reply carries an id/name pair you never sent.
    ident, name, is_response, answer_ip = response
    if is_response and (ident, name) in pending:
        return answer_ip
    return None


if __name__ == "__main__":
    hdr = struct.pack("!HHHHHH", 0x1234, 0x8180, 1, 1, 0, 0)
    print(parse_header(hdr))
    pending = {(0x1234, "example.com")}
    print(accept_response(pending, (0x1234, "example.com", True, "93.184.216.34")))
    print(accept_response(pending, (0x9999, "example.com", True, "6.6.6.6")))
