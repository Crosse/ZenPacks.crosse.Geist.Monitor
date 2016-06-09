from Products.DataCollector.plugins.DataMaps import MultiArgs, RelationshipMap, ObjectMap
from Products.DataCollector.plugins.CollectorPlugin import (
        SnmpPlugin, GetTableMap, GetMap,
        )


class Monitor(SnmpPlugin):
    snmpGetMap = (
            GetMap({
                '.1.3.6.1.4.1.21239.1.1.1.0': 'productTitle',
                '.1.3.6.1.4.1.21239.1.1.2.0': 'productVersion',
                '.1.3.6.1.4.1.21239.1.1.3.0': 'productFriendlyName',
                '.1.3.6.1.4.1.21239.1.1.5.0': 'productUrl',
                '.1.3.6.1.4.1.21239.1.1.7.0': 'productHardware',
                # The rest are solely used to get the total sensor count.
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
                    '.2': 'climateSerial',
                    '.3': 'climateName',
                    '.4': 'climateAvail',
                    }
                ),
            )

    def process(self, device, results, log):
        log.info('Modeler %s processing data for device %s',
                self.name(), device.id)

        getdata, tabledata = results
        sensor_count = sum([getdata[x] for x in getdata if 'Count' in x])

        maps = []

        # device-specific data
        manufacturer = 'Geist Manufacturing, Inc.'
        os_name = '%s %s' % (getdata['productTitle'], getdata['productVersion'])
        maps.append(ObjectMap(data={
            'sensor_count': sensor_count,
            'title': getdata['productFriendlyName'],
            'setHWProductKey': MultiArgs(getdata['productHardware'], manufacturer),
            'setOSProductKey': MultiArgs(os_name, manufacturer),
            }))

        # Components: climate sensors
        rm = RelationshipMap(
                relname='geistClimateSensors',
                modname='ZenPacks.crosse.Geist.Monitor.GeistClimateSensor',
                )
        for snmpindex, row in tabledata.get('climateTable', {}).items():
            serial = row.get('climateSerial')
            if not serial:
                log.warn('Skipping climate sensor with no serial')
                continue
            log.debug('Modeling climate sensor %s', serial)
            
            values = {k: row[k] for k in row}
            values['id'] = self.prepId(serial)
            values['title'] = values['climateName']
            values['snmpindex'] = snmpindex.strip('.')

            rm.append(ObjectMap(
                modname='ZenPacks.crosse.Geist.Monitor.GeistClimateSensor',
                data=values
                ))
        maps.append(rm)

        return maps
