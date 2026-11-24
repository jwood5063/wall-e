# Pololu 5421 KiCad libraries

The Pololu 5421 is an isolated, normally open SPST solid-state relay
module with a bidirectional load path.

## Add to a KiCad project

1. Extract this folder into your project.
2. In the Schematic Editor, open **Preferences → Manage Symbol Libraries**
   and add `Pololu.kicad_sym` to **Project Specific Libraries**.
3. In the PCB Editor, open **Preferences → Manage Footprint Libraries**
   and add the `Pololu.pretty` folder to **Project Specific Libraries**.
   Use the nickname `Pololu` so that the symbol's footprint assignment resolves.
4. Place `Pololu:Pololu_5421` and update the PCB from the schematic.

## Mounting and pin map

View the motherboard from its component side with the module above it,
component side up. Pad 1 is the footprint origin and has a square pad
and a silkscreen mark. X increases to the right and Y increases down.

| Pad | Signal | X (mm) | Y (mm) |
| --- | --- | ---: | ---: |
| 1 | GND | 0.00 | 0.00 |
| 2 | VIN | 2.54 | 0.00 |
| 3 | EN | 5.08 | 0.00 |
| 4 | LOAD1 | 0.00 | 17.78 |
| 5 | LOAD2 | 5.08 | 17.78 |

The module outline is 8.128 × 20.32 mm, based on the drawing's
320 × 800 mil dimensions. Use a straight 1×3 header for the control
pins and a straight 1×3 header with its center pin removed for the
load pins. The motherboard uses five Ø1.00 mm plated holes sized for
nominal 0.64 mm square posts. Check fit and current capacity for your
chosen headers, solder joints, and motherboard copper before fabrication.
The library was checked in KiCad 10.0.8. Physical fit and current capacity
were not tested.

[Pololu 5421 product documentation](https://www.pololu.com/product/5421)
