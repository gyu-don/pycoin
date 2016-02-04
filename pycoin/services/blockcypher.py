import json
import io

try:
    from urllib2 import urlopen
except ImportError:
    from urllib.request import urlopen

from pycoin.tx import Tx, Spendable
from pycoin.serialize import h2b, h2b_rev


class BlockCypherProvider(object):
    def __init__(self, api_key = "", netcode="BTC"):
        NETWORK_PATHS = {
            "BTC" : "main",
            "XTN" : "test3"
        }

        self.network_path = NETWORK_PATHS.get(netcode)
        self.api_key = api_key

    def base_url(self, args):
        return "https://api.blockcypher.com/v1/btc/%s/%s" % (self.network_path, args)

    def spendables_for_address(self, address):
        """
        Return a list of Spendable objects for the
        given bitcoin address.
        """
        spendables = []
        url_append = "?unspentOnly=true&token=%s&includeScript=true" % self.api_key
        url = self.base_url("addrs/%s%s" % (address, url_append))
        result = json.loads(urlopen(url).read().decode("utf8"))
        for txn in result.get("txrefs", []):
            coin_value = txn.get("value")
            script = h2b(txn.get("script"))
            previous_hash = h2b_rev(txn.get("tx_hash"))
            previous_index = txn.get("tx_output_n")
            spendables.append(Spendable(coin_value, script, previous_hash, previous_index))
        return spendables

    def tx_for_tx_hash(self, tx_hash):
        '''
        returns the pycoin.tx object for tx_hash
        '''
        try:
            url_append = "?token=%s&includeHex=true" % self.api_key
            url = self.base_url("txs/%s" % (tx_hash + url_append))
            result = json.loads(urlopen(url).read().decode("utf8"))
            tx = Tx.parse(io.BytesIO(h2b(result.get("hex"))))
            return tx
        except:
            raise Exception


    def get_balance(self, address):
        '''
        returns the balance object from blockcypher for address
        '''
        url_append = "/balance?token=%s" % self.api_key
        url = self.base_url("addrs/%s" % (address + url_append))
        result = json.loads(urlopen(url).read().decode("utf8"))
        return result
