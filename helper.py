from Crypto.Cipher import AES
import secrets
import hashlib
import socket
import time as t

HANDSHAKE_INSTRUCTION = "0" * 48
OPEN_INSTRUCTION = "a" + "0" * 47
CLOSE_INSTRUCTION = "c" + "0" * 47
CONFIRMATION_INSTRUCTION = "aa" + "0" * 46

class Demo_Romote:
    def __init__(self, KEY, seed):
        self.hasher = Hasher(KEY, seed)
        self.key = KEY

    def attachReciver(self, reciver):
        self.reciver = reciver

    def send(self, msg):
        print("")
        print("This progam uses a rolling hash. Each hash is generated using the previous hash value and the digital key, a random 256 bit number.")
        print("The next 196 bits or 48 hexidicimal characters is the instrution set. This can tell the reciver to do a certain action.")
        print("The last 64 bits is used to discribe important info such as time, hash iteration, and speicial instructions.")
        print("")
        print("First the remote sends a handshake. This handshake is used such that the reciver confirms that it is legitiment, and that the comuncation was not intercepted")
        print("This handshake contains one hash value.")
        print("")
        input()

        self.hasher.hashBuffer()

        handshake = self.handshake()

        expectedHash = self.hasher.hashbuffer[2]
        handshake = msgDecrypter(handshake, expectedHash)

        if handshake[:64] == expectedHash:
            print("")
            print("When the remote recives the proper handshake response, it encypts and sends out its message along with a hash that again mantains that the data is valid")
            print("In this case, the message is the one that you typed out in the start. However, this message can contain any confidental information or instruction.")
            print("")

            input()

            expectedHash = self.hasher.hashbuffer[4]

            confirmation = self.sendMsg(msg)
            confirmation = msgDecrypter(confirmation, expectedHash)

            if confirmation[:64] == expectedHash:
                print(f"Success: {confirmation}")

                self.hasher.updateHash(4)

                return (0)

            else:
                print("REMOTE: Reciver hash not expected value.", end ="")
                print(f"Expected {expectedHash} but recived {confirmation[:64]}")

        else:
            print("REMOTE: Reciver hash not expected value.", end ="")
            print(f"Expected {expectedHash} but recived {handshake[:64]}")

    def handshake(self):
        handshake = self.hasher.hashbuffer[1] + HANDSHAKE_INSTRUCTION + self.hasher.getIterationHex(1)
        print(f"REMOTE handshake sent: {handshake}")

        handshake = msgEncrypter(handshake, self.hasher.hashbuffer[1])
        print(f"REMOTE handshake encrypted: {handshake.hex()}")

        print("")
        print("Messages are encypted using their expected hash such that only the intended recipiant can decrypt them")
        print("")

        input()

        return self.reciver.handshakeHandler(handshake)

    def sendMsg(self, msg):
        print(f"REMOTE sending msg: {bytes.fromhex(msg).decode('utf-8')}")

        msg = self.hasher.hashbuffer[3] + msg + self.hasher.getIterationHex(3)
        print(f"REMOTE msg sent: {msg}")

        msg = msgEncrypter(msg, self.hasher.hashbuffer[3])
        print(f"REMOTE msg encrypted: {msg.hex()}")

        return self.reciver.msgHandler(msg)


class Demo_Reciver:
    def __init__(self, KEY, seed):
        self.hasher = Hasher(KEY, seed)
        self.key = KEY

    def attachRemote(self, remote):
        self.remote = remote

    def msgHandler(self, msg):
        expectedHash = self.hasher.hashbuffer[3]
        msg = msgDecrypter(msg, expectedHash)

        if msg[:64] == expectedHash:
            print("")
            print("The reciver checks the message by decrypting it and matching the hash.")
            print("If this step suceeds, the reciver approves the message and replies with a confirmation")
            print("")

            input()

            msgDecoded = msg[64:112]
            msgDecoded = bytes.fromhex(msgDecoded).decode("utf-8")

            print(f"RECIVER: Message Recived: {msgDecoded}")

            msgHash = self.hasher.hashbuffer[4]
            msg = msgHash + CONFIRMATION_INSTRUCTION + self.hasher.getIterationHex(4)

            encryptmsg = msgEncrypter(msg, msgHash)

            print(f"RECIVER confirmation: {msg}")
            print(f"RECIVER encrypted response: {encryptmsg.hex()}")

            self.hasher.updateHash(4)

            return encryptmsg
        else:
            print(f"RECIVER: Remote hash not expected value. Expected {expectedHash} but recived {handshake[:64]}")
            return (0)

    def handshakeHandler(self, handshake):
        print("The handshake is matched by the reciver, and then the reciver responds with the next code in the sequence.")
        print("")

        self.hasher.hashBuffer()

        expectedHash = self.hasher.hashbuffer[1]

        handshake = msgDecrypter(handshake, expectedHash)

        if handshake[:64] == expectedHash and handshake[64:128]:
            print(f"RECIVER: Handshake Accpeted {handshake}")

            reply = self.hasher.hashbuffer[2] + HANDSHAKE_INSTRUCTION + self.hasher.getIterationHex(2)
            print(f"RECIVER handshake response: {reply}")

            encryptmsg = msgEncrypter(reply, self.hasher.hashbuffer[2])
            print(f"RECIVER encrypted response: {encryptmsg.hex()}")

            return encryptmsg
        else:
            print(f"RECIVER: Remote hash not expected value. Expected {expectedHash} but recived {handshake[:64]}")
            return (0)


class Client:
    def __init__(self, KEY, port, serverIp):
        self.key = KEY
        self.port = port
        self.serverIp = serverIp

        # Send the hash of the key to the server
        keyHash = hashlib.sha512(bytes.fromhex(self.key))
        keyHash = keyHash.digest()

        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((self.serverIp, self.port))

        self.s.sendall(keyHash)

        # Timer
        start = t.time()

        # Recive a peice of data containing a unique 512 bit key
        proofhash = self.s.recv(512)

        end = t.time()
        timeDiff = end - start

        if timeDiff - 0.05 > 0.2:
            print(f"Server took too long to respond! {timeDiff}s")

            self.close()
            return 0

        proofhash = msgDecrypter(proofhash, self.key)

        if proofhash[64:128] != self.key:
            print(f"Server sent wrong key!")

            self.close()
            return 0

        self.hasher = Hasher(self.key, proofhash[:64])

    def send(self, msg, special):
        hash = self.hasher.updateHash(1)

        msg = self.msgConstructor(msg, special)
        msg = msgEncrypter(msg, hash)

        self.s.sendall(msg)

        hash = self.hasher.updateHash(1)

        data = self.s.recv(1024)

        if not data:
            return 0

        data = msgDecrypter(data, hash)
        print(data)

        if data[192:256] != hash:
            return 0

        return data

    def msgConstructor(self, msg, special):
        msg = msg.ljust(176, '0')

        iteration = str(hex(self.hasher.iteration)).lstrip('0x')
        iteration = iteration.rjust(8, '0')

        time = round(t.time() * 10) % (2 ** 24)
        time = str(hex(time)).lstrip('0x')
        time = time.rjust(6, '0')

        return (msg + special + time + iteration + self.hasher.currentHash)

    def close(self):
        self.s.close()


class Server:
    def __init__(self, KEY, port):
        self.key = KEY
        self.port = port

        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind(("0.0.0.0", self.port))
        self.s.listen()

        self.conn, self.addr = self.s.accept()
        data = self.conn.recv(512)

        start = t.time()

        keyHash = hashlib.sha512(bytes.fromhex(self.key))
        keyHash = keyHash.digest()

        if data == keyHash:
            proofhash = secrets.token_hex(32)
            msg = proofhash + self.key
            msg = msgEncrypter(msg, self.key)

            end = t.time()

            t.sleep(0.05 - (start - end))

            self.conn.sendall(msg)

            self.hasher = Hasher(self.key, proofhash[:64])

        else:
            print("Key hash not expected value")
            raise ValueError

    def receive(self, msg, special):
        hash = self.hasher.updateHash(1)

        data = self.conn.recv(1024)

        if not data:
            self.close()
            return 0

        data = msgDecrypter(data, hash)
        print(data)

        if data[192:256] != hash:
            self.close()
            return 0

        hash = self.hasher.updateHash(1)

        msg = self.msgConstructor(msg, special)
        msg = msgEncrypter(msg, hash)

        self.conn.sendall(msg)

        return data

    def msgConstructor(self, msg, special):
        msg = msg.ljust(176, '0')

        iteration = str(hex(self.hasher.iteration)).lstrip('0x')
        iteration = iteration.rjust(8, '0')

        time = round(t.time() * 10) % (2 ** 24)
        time = str(hex(time)).lstrip('0x')
        time = time.rjust(6, '0')

        return (msg + special + time + iteration + self.hasher.currentHash)

    def close(self):
        self.s.close()


class Hasher:
    def __init__(self, KEY, seed):
        self.key = KEY
        self.previousHash = "0" * 64
        self.currentHash = seed
        self.iteration = 0
        self.hashbuffer = ["0", "0", "0", "0", "0"]

    def getIteration(self, iterationNum):
        if iterationNum > self.iteration:
            temp = self.currentHash

            for i in range(iterationNum - self.iteration):
                temp = getNextHash(temp, self.key)

            return temp

        elif iterationNum == self.iteration:
            return self.currentHash

        elif iterationNum - 1 == self.iteration:
            return self.previousHash

        else:
            print("Out of Bounds")
            raise ValueError

    def getNextHash(self):
        hash = hashlib.sha256(bytes.fromhex(self.currentHash + self.key))
        hash = hash.hexdigest()

        return hash

    def updateHash(self, n):
        for i in range(n):
            hash = self.getNextHash()

            self.previousHash = self.currentHash
            self.currentHash = hash
            self.iteration += 1

        return self.currentHash

    def getIterationHex(self, n):
        hexValue = str(hex(self.iteration + n))

        hexValue = hexValue.replace("0x", "")
        hexValue = hexValue.rjust(16, '0')

        return hexValue

    def hashBuffer(self):
        temp = self.currentHash

        for i in range(5):
            temp = getNextHash(temp, self.key)

            self.hashbuffer[i] = temp


# Custom message encrypter which using the current hash scrambles and mutates the values
def msgEncrypter(msg, key):
    key = bytes.fromhex(key)
    msg = bytes.fromhex(msg)

    iv = hashlib.md5(key)
    iv = iv.digest()

    cipher = AES.new(key, AES.MODE_CBC, iv)

    msg = cipher.encrypt(msg)

    return msg

def msgDecrypter(msg, key):
    key = bytes.fromhex(key)

    iv = hashlib.md5(key)
    iv = iv.digest()

    cipher = AES.new(key, AES.MODE_CBC, iv)

    msg = cipher.decrypt(msg)

    return msg.hex()


# Gets the next hash from a hash value and a key
def getNextHash(currentHash, key):
    hash = hashlib.sha256(bytes.fromhex(currentHash + key))
    hash = hash.hexdigest()

    return hash


# Converts a byte into a list of binary numbers
def byteToBin(num):
    bin = []

    for i in range(8):
        bin.append(int(num / 2 ** (7 - i)))

        num %= 2 ** (7 - i)

    return bin


# Adds two bytes together based on thier binary vaules
def byteBinAdd(msg, key):
    msg = byteToBin(msg)
    key = byteToBin(key)

    msgValue = 0

    for i in range(8):
        msg[i] += key[i] + 1
        msg[i] %= 2

    return binToInt(msg)


# Coverts a binary number into a base 10 number
def binToInt(num):
    msgValue = 0

    for i in range(len(num)):
        if num[i] == 1:
            msgValue += 2 ** (len(num) - 1 - i)

    return msgValue


# Converts a hexidecimal character into a binary number
def hexcharToBin(num):
    bin = []

    num = hexcharToInt(num)

    for i in range(4):
        bin.append(int(num / 2 ** (3 - i)))

        num %= 2 ** (3 - i)

    return bin


# Converts a hexidecimal character into a base 10 number
def hexcharToInt(hexchar):
    temp = 0

    try:
        temp = int(hexchar)

    except:
        if hexchar == "a" or hexchar == "A":
            temp = 10
        elif hexchar == "b" or hexchar == "B":
            temp = 11
        elif hexchar == "c" or hexchar == "C":
            temp = 12
        elif hexchar == "d" or hexchar == "D":
            temp = 13
        elif hexchar == "e" or hexchar == "E":
            temp = 14
        elif hexchar == "f" or hexchar == "F":
            temp = 15
        else:
            raise ValueError

    finally:
        return temp
