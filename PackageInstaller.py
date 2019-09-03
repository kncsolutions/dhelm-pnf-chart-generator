# -*- coding: utf-8 -*-
"""
    **PackageInstaller.py**
    - Copyright (c) 2019, KNC Solutions Private Limited.
    - License: 'Apache License, Version 2.0'.
    - version: 1.0.0
"""
import subprocess
import sys
try:
    import pandas as pd
except ImportError:
    print('Pandas is not installed, installing it now')
    subprocess.call(['pip', 'install', 'pandas'])


class install_packages:
    @staticmethod
    def install():
        df = pd.read_csv('package_status.csv')
        print(df.at[df.first_valid_index(), 'a'])
        if df.at[df.first_valid_index(), 'a'] == 1:
            return
        reqs = subprocess.check_output([sys.executable, '-m', 'pip', 'freeze'])
        installed_packages = [r.decode().split('==')[0] for r in reqs.split()]
        print(installed_packages)
        package_list = ['pandas',
                        'XlsxWriter',
                        'pytz',
                        'tzlocal',
                        'DhelmGfeedClient',
                        'Quandl',
                        'kiteconnect'
                        ]
        for item in package_list:
            if item not in installed_packages:
                print(item)
                subprocess.call(['pip', 'install', 'DateTime'])
        success = True
        reqs = subprocess.check_output([sys.executable, '-m', 'pip', 'freeze'])
        installed_packages = [r.decode().split('==')[0] for r in reqs.split()]
        for item in package_list:
            if item not in installed_packages:
                success = False
        if success:
            df.loc[df.first_valid_index(), 'a'] = 1
            print(df)
            df.to_csv('package_status.csv', encoding='utf-8', index=False)