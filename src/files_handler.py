from os import stat
import re
from mongodb import MongoDb


class FilesHandler:

    @staticmethod
    def get_ips_from_file():
        persist = MongoDb()
        ipv4_address = re.compile(
            '^(?:(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\\.){3}(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]).?$'
        )
        ip_collection = persist.db.ips
        with open('list_of_ips.txt', 'r') as reader:
            for line in reader:
                for word in line.replace(',', '').split(' '):
                    ip_address = ipv4_address.findall(word)
                    if ip_address:
                        ip_address = ip_address[0][:-1] if ip_address[0][-1] == '.' else ip_address[0]
                        ip_collection.insert_one({
                            'ip': ip_address,
                            'status': "waiting"
                        })
