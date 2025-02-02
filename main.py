import base64
import datetime
import concurrent.futures
from passlib.utils.pbkdf2 import pbkdf2


EMAIL: str = "test@example.com"
SALT: str = "D1868F784E3353B3ABB003A1E2A36F56AF6C9D917DFF9C9CCBA3731014C7619D"
HASH: str = "d17780c96b5452d220164a321f240ee49b236d57b7a38744c7ddc47980265542"
ROUNDS = 100000

PASS_VARIANTS = [
    ["T","t"],
    ["e","E","3"],
    ["S","s","5"],
    ["T","t"],
]

blDryRun = False
blThreaded = True


def GenHash(MasterPassword: str) -> bytes:
    MasterPasswordBytes = str.encode(MasterPassword)
    MasterKey = pbkdf2(MasterPasswordBytes, str.encode(EMAIL), ROUNDS, None, "hmac-sha256")
    MasterPasswordHash = pbkdf2(MasterKey, MasterPasswordBytes, 1, None, "hmac-sha256")
    MasterPasswordHashb64 = base64.b64encode(MasterPasswordHash).decode()
    PasswordHash = pbkdf2(MasterPasswordHashb64.encode(), bytes.fromhex(SALT), ROUNDS, None, "hmac-sha256")
    return PasswordHash


def CheckGuess(strGuess: str):
    PasswordHash = GenHash(strGuess)
    if PasswordHash == bytes.fromhex(HASH):
        print ("\nMatch:", PasswordHash.hex())
        with open(("Match_" + PasswordHash.hex() + ".txt"), "w") as f:
            f.write(strGuess)
        print("\n * DONE * ")
        exit()


intPassGuessLength = len(PASS_VARIANTS)
strIndex = [None] * intPassGuessLength
intIndex = [None] * intPassGuessLength
for intPosition in range(0, intPassGuessLength):
    intIndex[intPosition] = 0
    strIndex[intPosition] = ""

print("\n * Calculating Guesses * ")

strGuesses = []
blDone = False
while not blDone:
    strGuess = "" # Reset
    for intPosition in range(0, intPassGuessLength): 
        if intIndex[intPosition] >= len(PASS_VARIANTS[intPosition]):
            if ((intPosition + 1) >= len(intIndex)):
                blDone = True
                break;
            intIndex[intPosition + 1] = intIndex[intPosition + 1] + 1 # step next position
            intIndex[intPosition] = 0 # reset this position

        strIndex[intPosition] = str(PASS_VARIANTS[intPosition][(intIndex[intPosition])])
        strGuess = strGuess + strIndex[intPosition]
    if not blDone:
        strGuesses.append(strGuess)
        intIndex[0] = intIndex[0] + 1 # Step

intGuess = 0;
intGuesses = len(strGuesses)
print(intGuesses, "Guesses")

intGuessSecs = round(intGuesses / 130)
if (intGuessSecs > 60):
    print(round(intGuessSecs / 60, 2), "minutes estimated to complete")
else: 
    print(intGuessSecs, "seconds estimated to complete")

input("\nPress Enter to continue...")

if (blDryRun):
    print(strGuesses)
    exit()
dteStart = datetime.datetime.now()

intMod = int(intGuesses / 100) # show 100 entries or every 100 if less than 10000
if (intMod < 100):
    intMod = 100

print("\n * BEGIN * ")
if (blThreaded):
    with concurrent.futures.ThreadPoolExecutor(8) as executor: # 8 works, increase for speed, decrease for reliability
        futures = [executor.submit(CheckGuess, str(strGuess)) for strGuess in strGuesses]
        for future in concurrent.futures.as_completed(futures):
            result = future.result(timeout=2)
            intGuess += 1
            if ((intGuess % intMod == 0) and intGuess > 0):
                dteDiff = datetime.datetime.now() - dteStart
                if (dteDiff.seconds > 0):
                    intEstimatedTime = round(((intGuesses - intGuess) / (intGuess / (dteDiff.seconds))), 2)
                    if (intEstimatedTime > 60):
                        print(intGuess, "/", intGuesses, "(", round(intGuess / intGuesses * 100, 2),"% done )", dteDiff.seconds, "seconds elapsed,", round(intEstimatedTime / 60, 2), "minutes estimated remaining...")
                    else:
                        print(intGuess, "/", intGuesses, "(", round(intGuess / intGuesses * 100, 2),"% done )", dteDiff.seconds, "seconds elapsed,", intEstimatedTime, "seconds estimated remaining...")

else:
    for strGuess in strGuesses:
        CheckGuess(strGuess)
        intGuess += 1
        if ((intGuess % intMod == 0) and intGuess > 0): 
            dteDiff = datetime.datetime.now() - dteStart
            if (dteDiff.seconds > 0):
                intEstimatedTime = round(((intGuesses - intGuess) / (intGuess / (dteDiff.seconds))), 2)
                print(intGuess, "/", intGuesses, "(", round(intGuess / intGuesses * 100, 2),"% done )", dteDiff.seconds, "seconds elapsed,", intEstimatedTime, "seconds estimated remaining...")

print("\n * DONE * ")
