import requests
from concurrent.futures import ThreadPoolExecutor
from mongodb import MongoDb


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
        response = requests.get(f'{self.geoip_url}/{ip}/')
        if response.status_code == 200:
            return response.json()

    def get_rdap_info(self, ip):
        for url in self.rdap_url:
            response = requests.get(f'{url}{ip}/')
            if response.status_code == 200:
                return response.json()
            # if url == self.rdap_url[-1]:

    def start_process(self):
        ip_list = self.ip_collection.find({
            "status": "waiting"
        })
        with ThreadPoolExecutor(max_workers=5) as executor:
            executor.map(self.process_ip, list(ip_list))

    def check_ip_cache(self, ip):
        processed_ip = self.ip_collection.find(
            {
                "ip": ip['ip'],
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
        is_cached = self.check_ip_cache(ip)
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
