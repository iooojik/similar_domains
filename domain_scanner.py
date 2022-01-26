import socket
import string
import threading
import time

import homoglyphs as hg


class DomainScanner:
    domain_symbols = []
    domain_zones = ['com', 'ru', 'net', 'org', 'info', 'cn', 'es', 'top', 'au', 'pl', 'it', 'uk', 'tk', 'ml', 'ga',
                    'cf', 'us', 'xyz', 'top', 'site', 'win', 'bid']
    input_word = ''
    __max_threads = 50
    __lock = threading.Lock()

    def __init__(self, input_word):
        self.get_domain_symbols()
        self.input_word = input_word

    def get_domain_symbols(self):
        self.domain_symbols = (sorted(set(string.ascii_lowercase).union(
            set('съешь же ещё этих мягких французских булок да выпей чаю'.lower().replace(" ", ""))).union('-').union(
            set('0123456789'))))

    def delete_one_symbol(self, reverse=False):
        if len(self.input_word) > 2:
            if reverse:
                for l in range(1, len(self.input_word)):
                    for zone in self.domain_zones:
                        domain = f'{self.input_word[l:len(self.input_word)]}.{zone}'
                        print(domain)
                        threading.Thread(target=self.check_domain, args=[domain]).start()
            else:
                for l in range(1, len(self.input_word)):
                    for zone in self.domain_zones:
                        domain = f'{self.input_word[0:len(self.input_word) - l]}.{zone}'
                        print(domain)
                        threading.Thread(target=self.check_domain, args=[domain]).start()

    def make_sub_domains(self):
        for l in range(1, len(self.input_word)):
            for zone in self.domain_zones:
                while threading.active_count() > self.__max_threads:
                    time.sleep(1)
                domain = f'{self.input_word[0:l]}.{self.input_word[l:len(self.input_word)]}.{zone}'
                threading.Thread(target=self.check_domain, args=[domain]).start()

    def get_domain_homoglyph(self):
        homoglyphs = hg.Homoglyphs(languages={'ru', 'en'})
        for l in range(1, len(self.input_word) + 1):
            combinations = homoglyphs.get_combinations(self.input_word[0:l])
            combinations.pop(0)
            for domain_part in combinations:
                for zone in self.domain_zones:
                    while threading.active_count() > self.__max_threads:
                        time.sleep(1)
                    domain = f'{domain_part}{self.input_word[l:len(self.input_word)]}.{zone}'
                    threading.Thread(target=self.check_domain, args=[domain]).start()

    def strategy_end_symbol(self):
        for symbol in self.domain_symbols:
            if symbol != '-':
                for zone in self.domain_zones:
                    domain = f'{self.input_word}{symbol}.{zone}'

                    while threading.active_count() > self.__max_threads:
                        time.sleep(1)
                    threading.Thread(target=self.check_domain, args=[domain]).start()

    def check_domain(self, domain):
        try:
            socket.setdefaulttimeout(2.0)
            self.__lock.acquire()
            socket.getaddrinfo(domain, 80)
            print(domain, end='\n')
        except socket.gaierror:
            pass
        self.__lock.release()

    def start_scanning(self):
        print('Scan started...')
        threads = [threading.Thread(target=self.strategy_end_symbol),
                   threading.Thread(target=self.get_domain_homoglyph), threading.Thread(target=self.make_sub_domains),
                   threading.Thread(target=self.delete_one_symbol, args=[False]),
                   threading.Thread(target=self.delete_one_symbol, args=[True])]
        for thread in threads:
            thread.start()
