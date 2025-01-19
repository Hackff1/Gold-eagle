import requests
import time
import uuid
import random
import base64
import hmac
import hashlib
import re
import binascii

def get_secret(url):
    try:
        # Fetch the content from the provided URL
        response = requests.get(url)
        response.raise_for_status()
        content = response.text

        # Search for the TAP_SECRET variable in the content
        match = re.search(r'TAP_SECRET\s*=\s*["\']([^"\']+)["\']', content)
        if not match:
            raise ValueError('TAP_SECRET variable not found.')

        # Extract the TAP_SECRET value
        tap_secret = match.group(1)

        # Decode the TAP_SECRET value
        secret_bytes = base64.b32decode(tap_secret, casefold=True)
        secret_hex = binascii.hexlify(secret_bytes).decode()
        return secret_hex
    except Exception as e:
        raise ValueError(f'Error fetching or decoding TAP_SECRET: {e}')


def generate_totp_in_base64(secret_hex, step=2, digits=6, algorithm=hashlib.sha1):
    secret_bytes = bytes.fromhex(secret_hex)
    time_counter = int(time.time() // step)
    time_counter_bytes = time_counter.to_bytes(8, byteorder="big")
    hmac_hash = hmac.new(secret_bytes, time_counter_bytes, algorithm).digest()
    offset = hmac_hash[-1] & 0x0F
    code_int = int.from_bytes(hmac_hash[offset:offset+4], byteorder="big") & 0x7FFFFFFF
    otp = code_int % (10 ** digits)
    otp_str = str(otp).zfill(digits)
    otp_base64 = base64.b64encode(otp_str.encode()).decode()
    return otp_base64


# URL containing the TAP_SECRET variable
SECRET_URL = 'https://telegram.geagle.online/assets/index-DI7KSCOy.js'

# Fetch the secret
try:
    secret_hex = get_secret(SECRET_URL)
except Exception as e:
    print(f"Error fetching secret: {e}")
    exit(1)

# Banner and styling
PURPLE = "\033[35m"
CYAN = "\033[36m"
YELLOW = "\033[33m"
GREEN = "\033[32m"
RED = "\033[31m"
BLUE = "\033[34m"
BOLD = "\033[1m"
UNDERLINE = "\033[4m"
RESET = "\033[0m"

ascii_banner = f"""
{PURPLE}    ______      __        __  ______                 __
   / ____/___  / /_____  / /_/ ____/______  ______  / /_____
  / /_  / __ \/ //_/ _ \/ __/ /   / ___/ / / / __ \/ __/ __ \\
 / __/ / /_/ / ,< /  __/ /_/ /___/ /  / /_/ / /_/ / /_/ /_/ /
/_/    \____/_/|_|\___/\__/\____/_/   \__, / .___/\__/\____/
                                     /____/_/               {RESET}
"""

tagline = f"""
{YELLOW} +-+-+-+-+-+-+ +-+-+-+-+ +-+-+ +-+-+-+-+ +-+-+-+-+-+-+-+-+
 |A|n|y|o|n|e| |w|a|n|t| |d|o| |s|o|m|e| |d|o|n|a|t|i|o|n|
 +-+-+-+-+-+-+ +-+-+-+-+ +-+-+ +-+-+-+-+ +-+-+-+-+-+-+-+-+ {RESET}
"""

print(f"{GREEN}{'=' * 70}{RESET}")
print(f"{ascii_banner}")
print(f"{tagline}")
print(f"{GREEN}{'=' * 70}{RESET}")
print(f"{YELLOW}{BOLD}{UNDERLINE}Telegram: https://t.me/foketcrypto{RESET}")
print(f"{RED}{BOLD}{UNDERLINE}YouTube: https://youtube.com/@foketcrypto{RESET}")
print(f"{GREEN}{'=' * 70}{RESET}")

def send_request(available_taps, count, token, secret_hex, max_retries=3):
    url = 'https://gold-eagle-api.fly.dev/tap'
    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-US,en;q=0.9',
        'authorization': f'Bearer {token}',
        'content-type': 'application/json',
        'origin': 'https://telegram.geagle.online',
        'priority': 'u=1, i',
        'referer': 'https://telegram.geagle.online/',
        'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
    }

    attempt = 0
    while attempt < max_retries:
        try:
            nonce = generate_totp_in_base64(secret_hex=secret_hex)
            data = {
                "available_taps": available_taps,
                "count": count,
                "timestamp": int(time.time()),
                "salt": str(uuid.uuid4()),
                "nonce": nonce,
            }
            response = requests.post(url, headers=headers, json=data, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            attempt += 1
            print(f"{RED}Request timed out. Retrying... Attempt {attempt}/{max_retries}{RESET}")
            time.sleep(2)
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

    return {"error": f"Request failed after {max_retries} attempts."}

# Read tokens from file
try:
    with open('data.txt', 'r') as file:
        tokens = [line.strip() for line in file.readlines()]
except Exception as e:
    print(f"{RED}Error reading tokens from file: {e}{RESET}")
    exit(1)

available_taps = 1000

# Main loop
while True:
    for token in tokens:
        print(f"\n{BLUE}Processing token: {token}{RESET}")
        for i in range(1):
            count = random.randint(510, 520)
            response = send_request(available_taps, count, token, secret_hex)
            
            if "error" in response:
                print(f"{RED}Error on request {i + 1}/4: {response['error']}{RESET}")
            else:
                print(f"{GREEN}Success on request {i + 1}/4: {response}{RESET}")

            delay = random.uniform(2, 5)
            print(f"{YELLOW}Calculated delay: {delay:.2f} seconds{RESET}")
            time.sleep(delay)
        
        print(f"{BLUE}Completed 4 requests for token {token}.{RESET}")

    sleep_time = random.uniform(8 * 60, 8.3* 60)
    print(f"{RED}Sleeping for {sleep_time:.2f} seconds before processing next batch of tokens...{RESET}")
    time.sleep(sleep_time)
