from domain_scanner import DomainScanner

try:
    print('Enter keyword:')
    keyword = input()
    if len(keyword.replace(' ', '')) > 0:
        domain_scanner = DomainScanner(input_word=keyword[:0 + keyword.find(".")])
        domain_scanner.start_scanning()
except KeyboardInterrupt:
    pass
