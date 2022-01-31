import socket
import string
import threading
import time
import re
import homoglyphs as hg


class DomainScanner:
    domain_symbols = []
    domain_zones = ['com', 'ru', 'net', 'org', 'info', 'cn', 'es', 'top', 'au', 'pl', 'it', 'uk', 'tk', 'ml', 'ga',
                    'cf', 'us', 'xyz', 'top', 'site', 'win', 'bid']
    keyword = ''
    __max_threads = 100
    __lock = threading.Lock()

    def __init__(self, domain):
        self.get_domain_symbols()
        self.keyword = ''.join(re.findall(r"[a-zA-zа-яА-я0-9-]", domain))

    def get_domain_symbols(self):
        self.domain_symbols = (sorted(set(string.ascii_lowercase).union(
            set('съешь же ещё этих мягких французских булок да выпей чаю'.lower().replace(" ", ""))).union('-').union(
            set('0123456789'))))

    def delete_one_symbol(self):
        if len(self.keyword) > 2:
            for l in range(1, len(self.keyword)):
                for zone in self.domain_zones:
                    domain = f'{self.keyword[0:l-1]}{self.keyword[l:len(self.keyword)]}.{zone}'
                    while threading.active_count() > self.__max_threads:
                        time.sleep(1)
                    threading.Thread(target=self.check_domain, args=[domain]).start()

    def make_sub_domains(self):
        for l in range(1, len(self.keyword)):
            for zone in self.domain_zones:
                while threading.active_count() > self.__max_threads:
                    time.sleep(1)
                domain = f'{self.keyword[0:l]}.{self.keyword[l:len(self.keyword)]}.{zone}'
                threading.Thread(target=self.check_domain, args=[domain]).start()

    def get_domain_homoglyph(self):
        homoglyphs = hg.Homoglyphs(languages={'ru', 'en'})
        for l in range(1, len(self.keyword) + 1):
            combinations = homoglyphs.get_combinations(self.keyword[0:l])
            if len(combinations) > 0:
                combinations.pop(0)
            for domain_part in combinations:
                for zone in self.domain_zones:
                    while threading.active_count() > self.__max_threads:
                        time.sleep(1)
                    domain = f'{domain_part}{self.keyword[l:len(self.keyword)]}.{zone}'
                    threading.Thread(target=self.check_domain, args=[domain]).start()

    def strategy_end_symbol(self):
        for symbol in self.domain_symbols:
            for zone in self.domain_zones:
                domain = f'{self.keyword}{symbol}.{zone}'
                while threading.active_count() > self.__max_threads:
                    time.sleep(1)
                threading.Thread(target=self.check_domain, args=[domain]).start()

    def check_domain(self, domain):
        try:
            socket.setdefaulttimeout(2.0)
            socket.getaddrinfo(domain, 80)
        except Exception:
            pass
        else:
            with self.__lock:
                print(domain, end='\n')

    def start_scanning(self):
        print('Scan started...')
        threads = [
            threading.Thread(target=self.strategy_end_symbol),
            threading.Thread(target=self.get_domain_homoglyph),
            threading.Thread(target=self.make_sub_domains),
            threading.Thread(target=self.delete_one_symbol)
        ]
        for thread in threads:
            thread.start()
