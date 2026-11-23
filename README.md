# Qt Instrument Cluster

Qt 6 / QML **test instrument-cluster application** for the [Car Dashboard](https://github.com/NordDemonNord/car-panel-os) learning project. It runs on a **Raspberry Pi 4 with Yocto Linux** (and can also run on desktop Linux) to verify the Qt graphics stack, display configuration and end-to-end vehicle telemetry path.

**This is not the final instrument cluster of the Car Dashboard project.** The actual instrument cluster is planned for a **separate display driven directly by STM32H743 bare-metal firmware** (LTDC). The Raspberry Pi display is intended for **infotainment**, for which a new, separate Qt application will be developed from scratch.

This repository will remain available as a reusable Qt/QML experiment and reference for possible future projects, even after the dedicated infotainment application replaces it on the Raspberry Pi.

## Features

- Qt Quick interface with speedometer, tachometer, tell-tales and vehicle readouts.
- C++ `VehicleDataReceiver` exposes vehicle properties to QML.
- Selectable telemetry backends: **demo**, **HTTP** and **SocketCAN**.
- CAN speed decoding: standard 11-bit ID `0x1A0`, DLC 2, unsigned big-endian 16-bit value at 0.01 km/h/bit.
- CAN disconnect timeout and reconnect handling in the current receiver implementation.

Only the speed frame `0x1A0` is implemented in the current CAN data path. Other displayed values and tell-tales are supported by the UI or alternate data sources; **do not interpret them as verified live CAN signals**.

## System integration

```text
ESP32 or PC/CANable → CAN 500 kbit/s → STM32H743
    → SLCAN over UART (CP2102) → Raspberry Pi (slcand, can0)
    → Qt SerialBus / SocketCAN → VehicleDataReceiver → QML gauges
```

Related repositories:

- [car-panel-firmware](https://github.com/NordDemonNord/car-panel-firmware) — STM32 and ESP32 firmware, CAN frame specification
- [car-panel-os](https://github.com/NordDemonNord/car-panel-os) — Yocto image, Qt recipe and boot-time systemd service

## Build on Linux

Requires **Qt 6.8+** with **Quick, Svg, Core5Compat, Network and SerialBus**, CMake, a C++ compiler, and the Qt Quick runtime modules. Using Qt Creator with the matching Qt kit is also supported.

```bash
git clone https://github.com/NordDemonNord/qt-instrument-cluster.git
cd qt-instrument-cluster
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build -j"$(nproc)"
```

The executable target is `appDashBoard`. Qt module installation paths and runtime plugin availability depend on the Linux distribution. Yocto builds the application using the recipe in `car-panel-os`.

## Select telemetry source

Set the `VEHICLE_DATA_SOURCE` environment variable when launching:

| Value | Data source | Requirements |
| --- | --- | --- |
| `demo` | Local animated test data | No CAN hardware |
| `http` | HTTP polling of `http://192.168.4.1/data` | Compatible ESP32 HTTP endpoint; this is the current code's **default** |
| `can` | Qt SerialBus SocketCAN | An available `can0` or another selected CAN interface |

```bash
VEHICLE_DATA_SOURCE=demo ./build/appDashBoard
VEHICLE_DATA_SOURCE=can VEHICLE_CAN_INTERFACE=can0 ./build/appDashBoard
```

Run `appDashBoard` from the location produced by your CMake generator; it may differ from the example. For a hardware-free SocketCAN test, a Linux `vcan0` interface may be used if the kernel provides `vcan`:

```bash
sudo modprobe vcan
sudo ip link add dev vcan0 type vcan
sudo ip link set vcan0 up
VEHICLE_DATA_SOURCE=can VEHICLE_CAN_INTERFACE=vcan0 ./build/appDashBoard
# In a second terminal:
cansend vcan0 1A0#2EE0
```

`cansend` is provided by `can-utils`. For a real Pi deployment the Yocto service already selects `VEHICLE_DATA_SOURCE=can`.

## Implementation

- `main.cpp` — application setup, QML engine and receiver context property.
- `VehicleDataReceiver.cpp/.h` — telemetry backends and QML-facing state.
- `Main.qml` and individual `*.qml` components — dashboard interface.
- `assets/` — gauges, icons and fonts.
- `CMakeLists.txt` — build and installation definitions.

## Development and AI disclosure

**The Qt application in this repository was created entirely with AI assistance.** It is used as a test application to validate the embedded Linux graphics stack and CAN-to-Qt integration; it is **not presented as independently authored Qt application code**. The broader Car Dashboard project includes separately developed STM32/ESP32 firmware and Yocto integration in the linked repositories.

## Status and next steps

- [x] Qt 6/QML dashboard with a hardware-accelerated Raspberry Pi deployment
- [x] Demo and HTTP data sources
- [x] Qt SerialBus/SocketCAN speed data source
- [x] Speed shown from STM32-forwarded CAN data (reported hardware test)
- [ ] Expand and centralize the CAN message definitions across the project
- [ ] Optional: extend live CAN decoding for testing additional instruments and indicators
- [ ] Add a short demo video/screenshot and automated tests
- [ ] Develop a separate infotainment Qt application for Raspberry Pi (outside this repository)

## License and third-party assets

Source code is licensed under [MIT](LICENSE). Fonts in `assets/fonts/` carry their own OFL notices; see the included license files. Other third-party assets, if any, retain their respective rights and must be checked before redistribution. This repository is a learning prototype and is not intended for road use.
