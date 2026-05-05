# STM32F103C8T6 vs STM32L432KB — Comparison

| Parameter | **STM32F103C8T6** (current) | **STM32L432KB** |
|---|---|---|
| **Series** | STM32F1 (Mainstream) | STM32L4 (Ultra-low-power) |
| **Core** | Arm Cortex-M3 | Arm Cortex-M4 + FPU + DSP |
| **Max clock** | 72 MHz | 80 MHz |
| **Flash** | 64 KB | 128 KB (up to 256 KB) |
| **SRAM** | 20 KB | 64 KB (16 KB with parity) |
| **Supply voltage** | 2.0 – 3.6 V | 1.71 – 3.6 V |
| **Package** | LQFP-48 (7×7 mm) | UFQFPN-32 (5×5 mm) — 32 pins only |
| **GPIO** | up to 37 (LQFP-48) | up to 26 |
| **ADC** | 2× 12-bit, 1 µs | 1× 12-bit, 5 Msps (oversampling to 16-bit) |
| **DAC** | — | 2× 12-bit |
| **Op-Amp / Comparators** | — | 1× OPAMP, 2× ultra-low-power comparators |
| **UART/USART** | 3× USART | 3× USART + 1× LPUART |
| **SPI** | 2× SPI | 2× SPI + 1× QSPI |
| **I2C** | 2× | 2× FM+ (up to 1 Mbit/s) |
| **CAN** | Yes | Yes |
| **USB** | Full-speed (needs crystal) | Full-speed **crystal-less** |
| **DMA** | 7-channel | 14-channel |
| **Timers** | 7 (3× GP 16-bit, 1× motor PWM, 2× WDG, SysTick) | 11 (1× 32-bit GP, motor control, 2× LP timers, …) |
| **Security** | Basic | MPU, Firewall, TRNG, readout/proprietary code protection |
| **Power modes** | Sleep, Stop, Standby | 8 nA shutdown, 28 nA standby, 1 µA Stop 2 |
| **Run current** | ~36 mA @ 72 MHz | ~6.7 mA @ 80 MHz (84 µA/MHz) |
| **Debug** | SWD + JTAG | SWD + JTAG + ETM |

---

## Key Takeaways

- **L432KB is much more capable and power-efficient**, but only comes in a 32-pin package — you lose ~11 GPIO pins vs. the LQFP-48.
- The **crystal-less USB** is a significant advantage (removes Y1 + C12/C13 and simplifies layout).
- The **FPU + DSP** make it far better for signal processing tasks.
- The smaller package (5×5 mm vs. 7×7 mm) shrinks board area but requires finer routing (0.5 mm pitch on both).
- `AMS1117-3.3` LDO still works since the L432KB accepts 1.71–3.6 V, but a more efficient LDO would complement its low-power features.
