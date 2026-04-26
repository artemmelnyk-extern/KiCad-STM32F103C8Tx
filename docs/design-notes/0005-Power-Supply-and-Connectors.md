# 0005 — Power Supply and Connectors (STM32F103C8T6)

**Date:** 2026-04-26
**Status:** Implemented
**References:**
- AMS1117 Datasheet — `docs/datasheets/AMS1117.pdf`
- `docs/datasheets/AMS1117-3-3 Linear-Voltage-Regulator.png`

---

## Bill of Materials (machine-readable)

| Ref | Value        | lib_id                          | Footprint                                         | Datasheet |
|-----|--------------|---------------------------------|---------------------------------------------------|-----------|
| U2  | AMS1117-3.3  | Regulator_Linear:AMS1117-3.3    | Package_TO_SOT_SMD:SOT-223-3_TabPin2              | http://www.advanced-monolithic.com/pdf/ds1117.pdf |
| C12 | 22u          | Device:C                        | Capacitor_SMD:C_0402_1005Metric                   | ~ |
| C13 | 22u          | Device:C                        | Capacitor_SMD:C_0402_1005Metric                   | ~ |
| D1  | RED          | Device:LED                      | LED_SMD:LED_0402_1005Metric                       | ~ |
| R3  | 1k5          | Device:R                        | Resistor_SMD:R_0402_1005Metric                    | ~ |
| R4  | 1k5          | Device:R                        | Resistor_SMD:R_0402_1005Metric                    | ~ |
| R5  | 1k5          | Device:R                        | Resistor_SMD:R_0402_1005Metric                    | ~ |
| J2  | Conn_01x04   | Connector:Conn_01x04_Pin        | Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical | ~ |
| J3  | Conn_01x04   | Connector:Conn_01x04_Pin        | Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical | ~ |
| J4  | Conn_01x04   | Connector:Conn_01x04_Pin        | Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical | ~ |

---

## 1 — Voltage Regulator: U2 (AMS1117-3.3)

### Context

The STM32F103C8T6 and all on-board peripherals require a regulated 3.3 V supply. The
board is powered via the USB Micro-B connector (J1, added in 0004), which provides 5 V
on the VBUS net. The AMS1117-3.3 is a 1 A, 1.117 V low-dropout linear regulator with a
fixed 3.3 V output, in SOT-223-3 (TabPin2) package.

### Pinout

| Pin | Name | Function |
|-----|------|----------|
| 3   | VI   | Input — connected to VBUS (5 V) |
| 2   | VO   | Output — connected to +3.3V rail |
| 1   | GND  | Ground |
| Tab | VO   | Exposed pad (tab), internally connected to VO — tied to +3.3V net and used for thermal dissipation |

### Circuit

```
VBUS (5 V) ──┬── C12 (22µF) ── GND     ← Input bulk cap
             │
            U2 VI (pin 3)
            U2 GND (pin 1) ── GND
            U2 VO (pin 2) ──┬── +3.3V  ← Output to MCU and peripherals
                            │
                           C13 (22µF) ── GND   ← Output bulk cap
```

### Decoupling Capacitors

| Ref | Value | Location       | Purpose                                         |
|-----|-------|----------------|-------------------------------------------------|
| C12 | 22 µF | VBUS (input)   | Input bulk cap — stabilises VBUS against cable inductance and host impedance |
| C13 | 22 µF | +3.3V (output) | Output bulk cap — LDO stability and load transient response |

The AMS1117 datasheet requires a minimum output capacitor of 10 µF for stability. 22 µF
provides margin and handles load steps from MCU peripheral startup (e.g. USB enumeration,
oscillator startup). The input capacitor C12 is recommended by the datasheet to prevent
oscillation when the input source has significant series inductance (e.g. USB cable).

### Power Budget

| Consumer         | Typical current |
|------------------|----------------|
| STM32F103C8T6    | ~25 mA at 72 MHz |
| USB D+ pull-up   | < 1 mA |
| Power LED (D1)   | ~1 mA |
| Peripherals      | < 10 mA |
| **Total**        | **< 40 mA** |

The AMS1117-3.3 is rated for 1 A output. At 40 mA load, the power dissipation in SOT-223
is well within limits:

$$P_{diss} = (V_{IN} - V_{OUT}) \times I_{LOAD} = (5 - 3.3) \times 0.04 \approx 68 \text{ mW}$$

The SOT-223 package has a typical thermal resistance of ~$170\,°C/W$ (junction-to-ambient),
giving a temperature rise of ~12 °C — no heatsinking required.

---

## 2 — Power Indicator LED: D1 + R3

### Circuit

```
+3.3V ── R3 (1.5 kΩ) ──[A D1 K]── PWR_LED_K net ── GND
```

D1 is a red LED used as a power-on indicator. R3 limits the LED current. The net label
`PWR_LED_K` connects D1's cathode to GND.

### Current Calculation

Using a typical red LED forward voltage of $V_F \approx 1.8\,V$:

$$I_{LED} = \frac{V_{CC} - V_F}{R3} = \frac{3.3 - 1.8}{1500} = 1\,\text{mA}$$

1 mA provides a clearly visible indication at low power consumption. The 1.5 kΩ value
was chosen to match other resistors already on the board (USB D+ pull-up R2). For a
brighter LED, R3 can be reduced to 470 Ω (~3.2 mA) without exceeding the typical
20 mA maximum rating of a 0402 LED.

---

## 3 — Peripheral Breakout Connectors: J2, J3, J4

Three 4-pin 2.54 mm pitch pin headers are added to expose MCU peripheral signals
for external connections (sensors, debug adapters, etc.).

### J2 — Debug / Peripheral Header

J2 exposes signals in the USB and SWD area of the MCU, including:

| J2 pin | Signal   | MCU pin | Description                        |
|--------|----------|---------|------------------------------------|
| 1      | USB_D−   | PA11 (21)| USB differential data minus        |
| 2      | USB_D+   | PA12 (22)| USB differential data plus         |
| 3      | SDIO     | PA13 (34)| SWDIO — SWD data line              |
| 4      | SWCLK    | PA14 (37)| SWDCLK — SWD clock line            |

> "SDIO" is used on the schematic as the net label for SWDIO (PA13). This is a labelling
> choice — the signal is SWD Data I/O, not the SDIO peripheral.

### J3 — USART1 Connector

J3 provides access to the USART1 interface and power rails:

| J3 pin | Signal      | MCU pin | Description          |
|--------|-------------|---------|----------------------|
| 1      | +3.3V       | —       | 3.3 V power output   |
| 2      | USART1_TX   | PA9 (30)| USART1 transmit      |
| 3      | USART1_RX   | PA10 (31)| USART1 receive      |
| 4      | GND         | —       | Ground               |

### J4 — I2C2 Connector

J4 provides access to the I2C2 interface with on-board pull-up resistors R4 and R5:

| J4 pin | Signal      | MCU pin  | Description          |
|--------|-------------|----------|----------------------|
| 1      | +3.3V       | —        | 3.3 V power output   |
| 2      | I2C2_SCL    | PB10 (21)| I2C2 clock line      |
| 3      | I2C2_SDA    | PB11 (22)| I2C2 data line       |
| 4      | GND         | —        | Ground               |

---

## 4 — I2C Pull-up Resistors: R4, R5

R4 and R5 are 1.5 kΩ pull-up resistors for I2C2_SCL and I2C2_SDA respectively,
connected between each signal line and +3.3V.

I2C requires open-drain lines pulled to VCC. The pull-up resistor value determines
the maximum bus speed and rise time:

$$t_r \approx 0.8473 \times R_p \times C_{bus}$$

For 1.5 kΩ and an estimated bus capacitance of 50 pF (short PCB traces + device inputs):

$$t_r \approx 0.8473 \times 1500 \times 50 \times 10^{-12} \approx 63\,\text{ns}$$

| Mode         | Max rise time | 1.5 kΩ result | Compatible? |
|--------------|--------------|---------------|-------------|
| Standard (100 kHz) | 1000 ns | 63 ns       | Yes |
| Fast (400 kHz)     | 300 ns  | 63 ns       | Yes |
| Fast Plus (1 MHz)  | 120 ns  | 63 ns       | Yes |

1.5 kΩ is suitable for Fast Mode (400 kHz) operation on a compact PCB. It also matches
the other 1.5 kΩ resistors on the board (R2 — USB D+ pull-up), simplifying the BOM.

---

## Placement Notes

- **U2**: Place close to J1 (USB connector) to minimise the VBUS trace length. C12 goes
  between J1 VBUS pin and U2 VI, as close to U2 as possible. C13 goes on the +3.3V side
  of U2 VO as close as possible to the output pin.
- **D1 + R3**: Place near the edge of the board for visibility. Route the anode of D1 to
  the +3.3V rail via R3.
- **J2, J3, J4**: Pin headers should be accessible on the board edge or perimeter, oriented
  consistently (pin 1 marked with a square pad). J3 and J4 are placed near each other to
  allow stacked cables or a ribbon connection to external peripherals.
- **R4, R5**: Place directly between the +3.3V rail via and the I2C2 signal traces leading
  to J4, as close to J4 as possible to minimise stub length on the pull-up path.
