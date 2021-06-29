import re
from mongodb import MongoDb
from ip_processor import IP_Processor


class FilesHandler:

    @staticmethod
    def get_ips_from_file():
        """
        Reads the file and populates the mongo database with
        the ips to be processed
        """
        persist = MongoDb()
        ip_processor = IP_Processor()
        ipv4_address = re.compile(
            '^(?:(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\\.){3}(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5]).?$'
        )
        ip_collection = persist.db.ips
        with open('./files/list_of_ips.txt', 'r') as reader:
            for line in reader:
                for word in line.replace(',', '').split(' '):
                    ip_address = ipv4_address.findall(word)
                    if ip_address:
                        ip_address = ip_address[0][:-1] if ip_address[0][-1] == '.' else ip_address[0]
                        ip_collection.delete_many(
                            {
                                'ip': ip_address,
                                'status': {"$in": ["failed", "waiting"]}
                            }
                        )
                        cached_ip = ip_processor.check_ip_cache(ip_address)
                        if not cached_ip:
                            ip_collection.insert_one({
                                'ip': ip_address,
                                'status': "waiting"
                            })

    @staticmethod
    def write_failed_ip(ip, reason):
        """"
        Writes the failed ip in the file
        """
        with open('./files/failed_ip_list.txt', 'a') as writer:
            writer.write(f"{ip} {reason}\n")
