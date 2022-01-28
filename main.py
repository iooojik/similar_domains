from domain_scanner import DomainScanner

try:
    keyword = input('Enter keyword:\n')
    if len(keyword.replace(' ', '')) > 0:
        domain_scanner = DomainScanner(domain=keyword)
        domain_scanner.start_scanning()
except KeyboardInterrupt:
    pass
