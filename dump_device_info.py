try:
    import simplepyble
except ImportError:
    print("Unable to import simplepyble -- try `pip install simplepyble`")
    exit(1)

if __name__ == "__main__":
    adapters = simplepyble.Adapter.get_adapters()

    if len(adapters) == 0:
        print("No adapters found")

    # Query the user to pick an adapter
    print("Please select an adapter:")
    for i, adapter in enumerate(adapters):
        print(f"{i}: {adapter.identifier()} [{adapter.address()}]")

    choice = 0 #int(input("Enter choice: "))
    adapter = adapters[choice]

    print(f"Selected adapter: {adapter.identifier()} [{adapter.address()}]")

    adapter.set_callback_on_scan_start(lambda: print("Scan started."))
    adapter.set_callback_on_scan_stop(lambda: print("Scan complete."))
    adapter.set_callback_on_scan_found(lambda peripheral: print(f"Found {peripheral.identifier()} [{peripheral.address()}]") if "BLE" in peripheral.identifier() or "Ble" in peripheral.identifier() else None)

    # Scan for a bit
    adapter.scan_for(2000)
    peripherals = adapter.scan_get_results()

    # Query the user to pick a peripheral
    print("Please select a peripheral:")
    for i, peripheral in enumerate(peripherals):
        print(f"{i}: {peripheral.identifier()} [{peripheral.address()}]")

    choice = int(input("Enter choice: "))
    peripheral = peripherals[choice]

    print(f"Connecting to: {peripheral.identifier()} [{peripheral.address()}]")
    peripheral_info = {"identifier": peripheral.identifier(), "address": peripheral.address(), "services": None}
    peripheral.connect()

    print("Successfully connected, listing services...")
    services = peripheral.services()
    service_list = []
    for service in services:
        print("--------------------")
        print(f"Service UUID: {service.uuid()}")
        service_entry = {"uuid": service.uuid(), "characteristics": []}
        characteristics = service.characteristics()
        for characteristic in characteristics:
            print(f"\tCharacteristic UUID: {characteristic.uuid()}")
            characteristic_entry = {"uuid": characteristic.uuid(), "descriptors": [], "capabilities": None}
            descriptors = characteristic.descriptors()
            for descriptor in descriptors:
                print(f"\t\tDescriptor UUID: {descriptor.uuid()}")
                characteristic_entry["descriptors"].append({"uuid": descriptor.uuid()})
                dir(descriptor)
                #print(f"Descriptor Value: {descriptor.read_value()}")
            
            capabilities = characteristic.capabilities()
            print(f"\t\tCapabilities: {capabilities}")
            capabilities_entry = {"capabilities": capabilities, "value": None}
            dir(capabilities)
            if "read" in capabilities:
                value = peripheral.read(service.uuid(), characteristic.uuid())
                capabilities_entry["value"] = value.hex()
                print(f"\t\tValue: {value}")
            characteristic_entry["capabilities"] = capabilities_entry
            service_entry["characteristics"].append(characteristic_entry)
            # if "notify" in capabilities:
            #     contents = peripheral.notify(service.uuid(), characteristic.uuid(), lambda data: print(f"Notification: {data}"))#print(f"Properties: {characteristic.properties()}")
            #     print(f"\t\tContents: {contents}")
        service_list.append(service_entry)
    peripheral_info["services"] = service_list
    
    print("--------------------")
    import json
    print(json.dumps(peripheral_info, indent=2))
    # write a list of all services and characteristics with capabilities and values to a json file
    with open("peripheral_info.json", "w") as f:
        json.dump(peripheral_info, f, indent=2)


    import time
    for t in range(10):
        # Iterate through all services and characteristics and read their values, printing ones that have changed
        for service in peripheral_info["services"]:
            for characteristic in service["characteristics"]:
                capabilities = characteristic["capabilities"]
                if "read" in capabilities:
                    value = peripheral.read(service["uuid"], characteristic["uuid"])
                    if value.hex() != capabilities["value"]:
                        print(f"Value changed for {service['uuid']} {characteristic['uuid']}: {value}")
                        capabilities["value"] = value.hex()
        time.sleep(1)

    # while(True):
    #     # Ask the user to pick a service/characteristic pair
    #     print("Please select a service/characteristic pair:")
    #     for i, (service_uuid, characteristic) in enumerate(service_characteristic_pair):
    #         print(f"{i}: {service_uuid} {characteristic}")

    #     choice = int(input("Enter choice: "))
    #     service_uuid, characteristic_uuid = service_characteristic_pair[choice]

    #     contents = peripheral.read(service_uuid, characteristic_uuid)
    #     print(f"Contents: {contents}")

    peripheral.disconnect()
