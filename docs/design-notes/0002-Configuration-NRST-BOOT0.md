# 0002 — Configuration Pins: NRST & BOOT0

## Bill of Materials (machine-readable)
| Ref | Value | lib_id | Footprint | Datasheet |
|-----|-------|--------|-----------|-----------|
| C9  | 100n | Device:C | Capacitor_SMD:C_0402_1005Metric | ~ |
| R1  | 10k  | Device:R | Resistor_SMD:R_0402_1005Metric | ~ |
| SW1 | SW_SPDT | Switch:SW_SPDT | Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical | ~ |

---

## Context

The STM32F103C8T6 has two dedicated configuration pins that control the boot mode and
the external reset behaviour. Both must be handled correctly to ensure reliable startup
and a usable programming/debugging workflow.

---

## NRST — External Reset Filter

### Pin

| MCU pin | Name | Type |
|---------|------|------|
| 7 | NRST | I/O, active-low reset |

### Circuit

```
NRST (net) ─────┬──── to MCU pin 7
                │
               C9 100n
                │
               GND
```

### Component

| Ref | Value | Footprint |
|-----|-------|-----------|
| C9  | 100n  | Capacitor_SMD:C_0402_1005Metric |

### Rationale

The STM32 datasheet recommends a 100 nF filter capacitor on NRST. It serves two purposes:

1. **Noise immunity** — absorbs fast voltage transients on the reset line that could cause
   a spurious reset during normal operation.
2. **Reset pulse shaping** — ensures the reset pulse width meets the minimum requirement
   (typ. 300 µs for the internal reset circuit to latch).

The NRST net is also routed as a named label so that it can be wired to a debug connector
(e.g. SWD 10-pin header pin 10) without a long wire crossing the sheet.

### Reference

- STM32F103C8 datasheet §5.3.13: NRST — external reset pin with internal pull-up (~40 kΩ).

---

## BOOT0 — Boot Mode Selection

### Pins

| MCU pin | Name  | Boot mode control |
|---------|-------|-------------------|
| 44      | BOOT0 | Selects boot source together with BOOT1 (PB2) |

### Boot Mode Truth Table

| BOOT1 (PB2) | BOOT0 | Boot source |
|-------------|-------|-------------|
| x           | 0     | Main Flash (normal operation) |
| 0           | 1     | System memory — ST factory bootloader (UART/SPI/I2C/USB DFU) |
| 1           | 1     | Embedded SRAM |

### Circuit

```
+3.3V ──┐
        │ (SW1 position A)
        SW1 (SPDT)
        │ (SW1 position B)
GND ────┘
        │
        │ SW_BOOT0 (net)
        │
       R1 10k (series)
        │
        │ BOOT0 (net)
        │
       ─┴─ to MCU pin 44
```

### Components

| Ref | Value   | Footprint | Notes |
|-----|---------|-----------|-------|
| SW1 | SW_SPDT | Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical | 3-pin header + jumper for prototype |
| R1  | 10k     | Resistor_SMD:R_0402_1005Metric | Series protection + override resistor |

### Rationale

**SW1 — SPDT boot mode switch**

A single-pole double-throw switch (implemented here as a 3-pin header with a jumper)
ties BOOT0 to either GND or +3.3V:

- **GND position (normal)** — BOOT0 = 0, MCU boots from main Flash. This is the default
  position for production and normal development use.
- **+3.3V position (bootloader)** — BOOT0 = 1, MCU enters the ST factory bootloader stored
  in system memory. This allows programming via UART (PA9/PA10) without a dedicated
  SWD programmer.

A header + jumper was chosen over a DIP switch for prototype convenience. On a production
board this may be replaced with a SMD slide switch or a pull-down resistor only (if
SWD programming is the sole programming path and no UART DFU is needed).

**R1 — 10 kΩ series resistor**

The series resistor between the switch and the BOOT0 pin serves two purposes:

1. **Short-circuit protection** — if the switch momentarily shorts +3.3V to GND during
   switching (break-before-make gap), R1 limits the transient current.
2. **ST-Link / external override** — when the MCU is already running and an external tool
   drives BOOT0 (e.g. some programmers can assert BOOT0 before reset), R1 allows the
   tool to override the switch position without fighting it. At 10 kΩ, the switch is
   a weak driver that any pushed output can easily overcome.

### Notes

- BOOT1 (PB2) is not broken out in this design. It defaults to GND via the MCU internal
  state after reset (input with internal weak pull, floats low if unconnected — verify
  on board bring-up).
- The BOOT0 footprint for SW1 is a 3-pin vertical 2.54 mm pin header. A 2-pin jumper
  placed between pins 1–2 selects GND; between pins 2–3 selects +3.3V. Mark the header
  silkscreen accordingly.

### Reference

- STM32F103C8 datasheet §3.4: Boot configuration.
- AN2606 §33: STM32F10xxx system memory boot mode (UART bootloader).
