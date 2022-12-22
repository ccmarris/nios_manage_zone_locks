#!/usr/bin/env python3
#vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
'''

 Description:

    Retrieve leases for a network based on a seed IP address

 Requirements:
   Python 3.6+

 Author: Chris Marrison

 Date Last Updated: 20221222

 Todo:

 Copyright (c) 2022 Chris Marrison / Infoblox

 Redistribution and use in source and binary forms,
 with or without modification, are permitted provided
 that the following conditions are met:

 1. Redistributions of source code must retain the above copyright
 notice, this list of conditions and the following disclaimer.

 2. Redistributions in binary form must reproduce the above copyright
 notice, this list of conditions and the following disclaimer in the
 documentation and/or other materials provided with the distribution.

 THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
 "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
 LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
 FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
 COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
 INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
 BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
 LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
 CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
 LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
 ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 POSSIBILITY OF SUCH DAMAGE.

'''
__version__ = '0.1.0'
__author__ = 'Chris Marrison'
__author_email__ = 'chris@infoblox.com'
__license__ = 'BSD'

import logging
import requests
import argparse
import configparser
import time


def parseargs():
    '''
    Parse Arguments Using argparse

    Parameters:
        None

    Returns:
        Returns parsed arguments
    '''
    description = 'Manage NIOS zone locks'
    parse = argparse.ArgumentParser(description=description)
    parse.add_argument('-c', '--config', type=str, default='gm.ini',
                        help="Override ini file")
    parse.add_argument('-z', '--zone', type=str, default='',
                        help='Operate on specific zone')
    parse.add_argument('-l', '--lock', action='store_true', 
                        help="Lock zone(s)")
    parse.add_argument('-u', '--unlock', action='store_true', 
                        help="Unlock zone(s)")
    parse.add_argument('-d', '--debug', action='store_true', 
                        help="Enable debug messages")

    return parse.parse_args()


def read_ini(ini_filename):
    '''
    Open and parse ini file

    Parameters:
        ini_filename (str): name of inifile

    Returns:
        config :(dict): Dictionary of BloxOne configuration elements

    '''
    # Local Variables
    cfg = configparser.ConfigParser()
    config = {}
    ini_keys = ['gm', 'api_version', 'valid_cert', 'user', 'pass' ]

    # Attempt to read api_key from ini file
    try:
        cfg.read(ini_filename)
    except configparser.Error as err:
        logging.error(err)

    # Look for NIOS section
    if 'NIOS' in cfg:
        for key in ini_keys:
            # Check for key in BloxOne section
            if key in cfg['NIOS']:
                config[key] = cfg['NIOS'][key].strip("'\"")
                logging.debug('Key {} found in {}: {}'.format(key, ini_filename, config[key]))
            else:
                logging.warning('Key {} not found in NIOS section.'.format(key))
                config[key] = ''
    else:
        logging.warning('No BloxOne Section in config file: {}'.format(ini_filename))
        config['api_key'] = ''

    return config


def setup_logging(debug):
    '''
     Set up logging

     Parameters:
        debug (bool): True or False.

     Returns:
        None.

    '''
    # Set debug level
    if debug:
        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s %(levelname)s: %(message)s')
    else:
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s %(levelname)s: %(message)s')

    return


def create_session(user: str = '',
                   passwd: str ='',
                   validate_cert: bool =False):
    '''
    Create request session

    Parameters:
    
    Return:
        wapi_session (obj): request session object
    '''
    headers = { 'content-type': "application/json" }

    # Avoid error due to a self-signed cert.
    if not validate_cert:
        requests.packages.urllib3.disable_warnings()
    
    wapi_session = requests.session()
    wapi_session.auth = (user, passwd)
    wapi_session.verify = validate_cert
    wapi_session.headers = headers

    return wapi_session


class ZONELOCKS:
    '''
    Control NIOS Zone Locking
    '''

    def __init__(self, cfg: str = 'gm.ini') -> None:
        '''
        Handle Zone Locks

        Parameters:
            cfg_file (str): Override default ini filename
        '''
        self.config = {}
        self.config = read_ini(cfg)

        self.gm = self.config.get('gm')
        self.wapi_version = self.config.get('api_version')
        self.username = self.config.get('user')
        self.password = self.config.get('pass')
        self.base_url = f'https://{self.gm}/wapi/{self.wapi_version}'

        if self.config.get('valid_cert') == 'true':
            self.validate_cert = True
        else:
            self.validate_cert = False

        self.session = create_session( user=self.username,
                                      passwd=self.password,
                                      validate_cert=self.validate_cert)

        return
 

    def _add_params(self, url, first_param=True, **params):
        # Add params to API call URL
        if len(params):
            for param in params.keys():
               if first_param:
                   url = url + '?'
                   first_param = False
               else:
                   url = url + '&'
               url = url + param + '=' + params[param]
        
        return url


    def wapi_get(self, **params):
        '''
        Make wapi call

        Parameters:
            **params: parameters for request.get
        
        Returns:
            data: JSON response as object (list/dict) or None
        '''
        status_codes_ok = [ 200, 201 ]

        response = self.session.get(**params)
        if response.status_code in status_codes_ok:
            data = response.json()
        else:
            logging.debug(f'HTTP response: {response.status_code}')
            logging.debug(f'Body: {response.content}')
            data = None

        return data


    def wapi_post(self, **params):
        '''
        Make wapi call

        Parameters:
            **params: parameters for request.get
        
        Returns:
            data: JSON response as object (list/dict) or None
        '''
        status_codes_ok = [ 200, 201 ]

        response = self.session.post(**params)
        if response.status_code in status_codes_ok:
            data = response.text
        else:
            logging.debug(f'HTTP response: {response.status_code}')
            logging.debug(f'Body: {response.content}')
            data = None

        return data


    def get_zones(self, **params):
        '''
        Get list of zones with lock status

        Parameters:

        Returns:
            List of zones with lock status
        '''
        zones = []
        return_fields = '_return_fields=fqdn,locked,locked_by'

        # Get Zones
        url = f'{self.base_url}/zone_auth?{return_fields}'
        if params:
            url = self._add_params(url, first_param=False, **params)

        # Use base session
        logging.info(f'Retrieving zone data')
        response = self.wapi_get(url=url)
        if response:
            logging.info('Zone data retrieved successfully')
            logging.debug(f'Response: {response}')
            zones = response
        else:
            logging.error('Failed to retrieve zone data')
            zones = []
        
        return zones


    def lock_zone(self, fqdn: str = '', zone_ref: str  = ''):
        '''
        Lock specified zone using either fqdn or object _ref

        Parameters:
            fqdn (str): Zone name (optional)
            zone_ref (str): Object Reference (_ref of zone)
        
        Returns:
            bool
        '''
        status = False
    
        if not zone_ref:
            zone_data = self.get_zones(fqdn=fqdn)
            if len(zone_data) == 1:
                zone_ref = zone_data[0].get('_ref')
            else:
                logging.error(f'Cannot proceed: {len(zone_data)} zone matches')
                zone_ref = ''
        
        if zone_ref:
            url = f'{self.base_url}/{zone_ref}'
            url += '?_function=lock_unlock_zone&operation=LOCK' 
            response = self.wapi_post(url=url)
            if response == '{}':
                logging.info('Zone locked') 
                status = True
            else:
                logging.error(f'Error locking zone: {response}')

        return status


    def unlock_zone(self, fqdn: str = '', zone_ref: str  = ''):
        '''
        Unlock specified zone using either fqdn or object _ref

        Parameters:
            fqdn (str): Zone name (optional)
            zone_ref (str): Object Reference (_ref of zone)
        
        Returns:
            bool
        '''
        status = False
    
        if not zone_ref:
            zone_data = self.get_zones(fqdn=fqdn)
            if len(zone_data) == 1:
                zone_ref = zone_data[0].get('_ref')
            else:
                logging.error(f'Cannot proceed: {len(zone_data)} zone matches')
                zone_ref = ''
        
        if zone_ref:
            url = f'{self.base_url}/{zone_ref}'
            url += '?_function=lock_unlock_zone&operation=UNLOCK' 
            response = self.wapi_post(url=url)
            if response == '{}':
                logging.info('Zone unlocked') 
                status = True
            else:
                logging.error(f'Error unlocking zone: {response}')

        return status


def report_lock_status(cfg: str ='', zone:str =''):
    '''
    Get zone and report log status

    Parameters:
        cfg(str): Configuration file (will use gm.ini by default)
        zone(str): Zone name, if specified only this zone will be reported
    
    Returns:
        JSON zone data
    '''
    gm = ZONELOCKS(cfg)

    if zone:
        zone_data = gm.get_zones(fqdn=zone)
    else:
        zone_data = gm.get_zones()
    
    if zone_data:
        for z in zone_data:
            report = f'Zone: {z.get("fqdn")}, Locked: {z.get("locked")}'
            if z.get('locked'):
                report += f', Locked by: {z.get("locked_by")}'
            logging.info(report)
    else:
        logging.info('No matching zones found.')
    
    return zone_data


def control_zone_lock(cfg: str = '',
                      zone: str = '',
                      zone_ref: str = '',
                      lock: bool = False,
                      unlock: bool = False) -> bool:
    '''
    Wrapper to lock/unlock zones

    Parameters:
        cfg (str): Configuration file - defaults to gm.ini
        zone (str): Zone Name (optional)
        zone_ref (str): Object ref of zone _ref
        lock (bool): Lock zone
        unlock (bool): Unlock zone
    
    Note: 
        If lock and unlock are set to True unlock wins.
    
    Returns:
        bool
    '''
    status = False
    gm = ZONELOCKS(cfg)

    if lock and unlock:
        # Unlock overrides
        lock = False
    
    if lock:
        status = gm.lock_zone(fqdn=zone, zone_ref=zone_ref)
    
    if unlock:
        status = gm.unlock_zone(fqdn=zone, zone_ref=zone_ref)

    return status


def process_all_zones(cfg: str = '', 
                      lock: bool = False, 
                      unlock: bool = False):
    '''
    Run against all zones

	Parameters:
        cfg (str): Configuration file - defaults to gm.ini
        lock (bool): Lock zone
        unlock (bool): Unlock zone
    Note: 
        If lock and unlock are set to True unlock wins.
    '''
    gm = ZONELOCKS(cfg)

    if lock and unlock:
        # Unlock overrides
        lock = False

    zone_data = gm.get_zones()
    for z in zone_data:
        if lock and not z.get('locked'):
            ref = z.get('_ref')
            s = gm.lock_zone(zone_ref=ref)
        if unlock and z.get('locked'):
            ref = z.get('_ref')
            s = gm.unlock_zone(zone_ref=ref)
        report_lock_status(cfg=cfg, zone=z.get('fqdn'))
    
    return


def main():
    '''
    Code logic
    '''
    exitcode = 0
    run_time = 0

    # Parse CLI arguments
    args = parseargs()
    setup_logging(args.debug)

    t1 = time.perf_counter()
    
    if not (args.lock or args.unlock):
        report_lock_status(cfg=args.config, zone=args.zone)
    else:
        if args.zone:
            s = control_zone_lock(cfg=args.config,
                                  zone=args.zone,
                                  lock=args.lock,
                                  unlock=args.unlock)
        else:
            s = process_all_zones(cfg=args.config,
                                  lock=args.lock,
                                  unlock=args.unlock)

    run_time = time.perf_counter() - t1
    
    logging.info('Run time: {}'.format(run_time))

    return exitcode


### Main ###
if __name__ == '__main__':
    exitcode = main()
    exit(exitcode)
## End Main ###
