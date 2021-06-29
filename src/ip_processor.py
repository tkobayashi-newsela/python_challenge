import requests
import logging
from concurrent.futures import ThreadPoolExecutor
from mongodb import MongoDb


class Fail_Processing(Exception):
    pass


class IP_Processor:

    def __init__(self) -> None:
        self.rdap_url = [
            'http://rdap.arin.net/registry/ip/',
            'http://rdap.db.ripe.net/ip/',
            'http://rdap.apnic.net/ip/',
            'http://rdap.lacnic.net/rdap/ip/',
            'http://rdap.afrinic.net/rdap/ip/'
        ]
        self.geoip_url = 'http://ipwhois.app/json/'
        persist = MongoDb()
        self.ip_collection = persist.db.ips

    def get_geoip_info(self, ip):
        """"
        Gets the geoip information.
        Raises Fail_Processing in case status_code != 200
        """
        response = requests.get(f'{self.geoip_url}/{ip}/')
        if response.status_code == 200:
            return response.json()
        raise Fail_Processing(response.json())

    def get_rdap_info(self, ip):
        """"
        Gets the rdap information.
        Raises Fail_Processing in case status_code != 200
        """
        for url in self.rdap_url:
            response = requests.get(f'{url}{ip}/')
            if response.status_code == 200:
                return response.json()
            if url == self.rdap_url[-1]:
                raise Fail_Processing(response.json())

    def start_process(self):
        """"
        Starts the process of ip reading.
        Uses 10 threads to maximize performance
        """
        ip_list = self.ip_collection.find({
            "status": "waiting"
        })
        with ThreadPoolExecutor(max_workers=10) as executor:
            executor.map(self.process_ip, list(ip_list))

    def check_ip_cache(self, ip):
        """"
        Checks in the database if there already is information about the ip.
        """
        processed_ip = self.ip_collection.find_one(
            {
                "ip": ip,
                "status": "processed"
            }
        )
        if processed_ip:
            self.ip_collection.delete_many(
                {
                    "ip": ip['ip'],
                    "status": {"$ne": "processed"}
                }
            )
            return True
        return False

    def process_ip(self, ip):
        """"
        Process the ip. Gets the rdap and geoip information and saves
        it in the database
        """
        is_cached = self.check_ip_cache(ip['ip'])
        if not is_cached:
            self.ip_collection.find_one_and_update(
                {
                    "ip": ip['ip']
                },
                {
                    '$set': {
                        'status': 'processing'
                    }
                }
            )
            try:
                rdap = self.get_rdap_info(ip['ip'])
                geoip = self.get_geoip_info(ip['ip'])
                self.ip_collection.find_one_and_update(
                    {
                        "ip": ip["ip"]
                    },
                    {
                        '$set': {
                            'rdap': rdap,
                            'geoip': geoip,
                            'status': "processed"
                        }
                    }
                )
            except Fail_Processing as e:
                self.ip_collection.find_one_and_update(
                    {
                        "ip": ip["ip"]
                    },
                    {
                        '$set': {
                            'status': "failed"
                        }
                    }
                )
                ip = ip['ip']
                logging.error(f"Fail processing ip {ip}")
                from file_handler import FilesHandler
                FilesHandler.write_failed_ip(ip, e)
