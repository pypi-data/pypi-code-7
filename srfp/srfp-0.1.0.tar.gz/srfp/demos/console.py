from srfp import comms, protocol

mio = comms.MessageIO('unix:/tmp/virtualbox-sock')
path = []
ls_cache = {}

def check_file(name, isfile):
    if dst not in ls_cache.get(tuple(path), tuple()):
        mio.send_msg(protocol.DirectoryListRequest(path))
        listing_resp = mio.recv_msg()
        ls_cache[tuple(path)] = listing_resp.listing
        if dst not in listing_resp.listing:
            return False

    # check it's a directory
    mio.send_msg(protocol.NodeInfoRequest(path + [dst]))
    if mio.recv_msg().isfile != isfile:
        return False

    return True

while True:
    cmd = input("{} > ".format(b'\\'.join(path).decode('utf8'))).split()
    if cmd[0] == 'cd':
        if len(cmd) != 2:
            print("Usage: cd <dir>")
            continue
        dst = cmd[1].encode('utf8')
        if dst == b'..':
            path.pop()
        else:
            if check_file(dst, False):
                path.append(dst)
            else:
                print("No such directory")

    if cmd[0] == 'ls':
        mio.send_msg(protocol.DirectoryListRequest(path))
        listing_resp = mio.recv_msg()
        ls_cache[tuple(path)] = listing_resp.listing
        for i in listing_resp.listing:
            print(i.decode('utf8'))

    if cmd[0] == 'cat':
        if len(cmd) != 2:
            print("Usage: cat <file>")
            continue

        dst = cmd[1].encode('utf8')

        if not check_file(dst, True):
            print("No such file")

        offset = 0
        try:
            while True:
                mio.send_msg(protocol.FileContentsRequest(offset, 0xFF, path + [dst]))
                rv = mio.recv_msg()
                print(rv.data.decode('utf8'), end="")
                if len(rv.data) != 0xFF:
                    break
        except UnicodeDecodeError:
            print("Came across something that wasn't valid UTF8. Quitting.")

    if cmd[0] == 'exit':
        exit(0)

