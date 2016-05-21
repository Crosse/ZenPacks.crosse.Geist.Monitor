from Products.DataCollector.plugins.CollectorPlugin import (
        SnmpPlugin, GetTableMap, GetMap,
        )


class Monitor(SnmpPlugin):
    relname = 'geistClimateSensors'
    modname = 'ZenPacks.crosse.Geist.Monitor.GeistClimateSensor'

    snmpGetMap = (
            GetMap({
                '.1.3.6.1.4.1.21239.1.1.8.1.2.0': 'climateCount',
                '.1.3.6.1.4.1.21239.1.1.8.1.3.0': 'powerMonitorCount',
                '.1.3.6.1.4.1.21239.1.1.8.1.4.0': 'tempSensorCount',
                '.1.3.6.1.4.1.21239.1.1.8.1.5.0': 'airflowSensorCount',
                '.1.3.6.1.4.1.21239.1.1.8.1.6.0': 'powerOnlyCount',
                '.1.3.6.1.4.1.21239.1.1.8.1.7.0': 'doorSensorCount',
                '.1.3.6.1.4.1.21239.1.1.8.1.8.0': 'waterSensorCount',
                '.1.3.6.1.4.1.21239.1.1.8.1.9.0': 'currentSensorCount',
                '.1.3.6.1.4.1.21239.1.1.8.1.10.0': 'millivoltSensorCount',
                '.1.3.6.1.4.1.21239.1.1.8.1.11.0': 'power3ChSensorCount',
                '.1.3.6.1.4.1.21239.1.1.8.1.12.0': 'outletCount',
                '.1.3.6.1.4.1.21239.1.1.8.1.13.0': 'vsfcCount',
                '.1.3.6.1.4.1.21239.1.1.8.1.14.0': 'ctrl3ChCount',
                '.1.3.6.1.4.1.21239.1.1.8.1.15.0': 'ctrlGrpAmpsCount',
                '.1.3.6.1.4.1.21239.1.1.8.1.16.0': 'ctrlOutputCount',
                '.1.3.6.1.4.1.21239.1.1.8.1.17.0': 'dewpointSensorCount',
                '.1.3.6.1.4.1.21239.1.1.8.1.18.0': 'digitalSensorCount',
                '.1.3.6.1.4.1.21239.1.1.8.1.19.0': 'dstsSensorCount',
                '.1.3.6.1.4.1.21239.1.1.8.1.20.0': 'cpmSensorCount',
                '.1.3.6.1.4.1.21239.1.1.8.1.21.0': 'smokeAlarmSensorCount',
                '.1.3.6.1.4.1.21239.1.1.8.1.22.0': 'neg48VdcSensorCount',
                '.1.3.6.1.4.1.21239.1.1.8.1.23.0': 'pos30VdcSensorCount',
                '.1.3.6.1.4.1.21239.1.1.8.1.24.0': 'analogSensorCount',
                '.1.3.6.1.4.1.21239.1.1.8.1.25.0': 'ctrl3ChIECCount',
                '.1.3.6.1.4.1.21239.1.1.8.1.26.0': 'airSpeedSwitchSensorCount',
                })
            )

    snmpGetTableMaps = (
            GetTableMap(
                'climateTable', '1.3.6.1.4.1.21239.1.2.1', {
                    '.1':  'climateIndex',
                    '.2':  'climateSerial',
                    '.3':  'climateName',
                    '.4':  'climateAvail',
                    '.5':  'climateTempC',
                    '.10': 'climateIO1',
                    '.11': 'climateIO2',
                    '.12': 'climateIO3',
                    }
                ),
            )

    def process(self, device, results, log):
        sensor_count = sum([x for x in results[0].values()])
        climate_sensors = results[1].get('climateTable', {})

        rm = self.relMap()
        for snmpindex, row in climate_sensors.items():
            serial = row.get('climateSerial')
            if not serial:
                log.warn('Skipping climate sensor with no serial')
                continue
            
            rm.append(self.objectMap({
                'id': self.prepId(serial),
                'title': row.get('climateName'),
                'snmpindex': snmpindex.strip('.'),
                'serial': serial,
                'temperature': row.get('climateTempC'),
                'ioPort1': row.get('climateIO1'),
                'ioPort2': row.get('climateIO2'),
                'ioPort3': row.get('climateIO3'),
                }))

        om = self.objectMap({
            'sensor_count': sensor_count,
            })
        return [om, rm]
