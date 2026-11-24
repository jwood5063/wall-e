# Pololu 2815 Big MOSFET Slide Switch HP

## KiCad setup

1. Extract this folder next to your project's `.kicad_pro` file.
2. In **Schematic Editor → Preferences → Manage Symbol Libraries**,
   add `Pololu_2815.kicad_sym` to **Project Specific Libraries**.
3. In **PCB Editor → Preferences → Manage Footprint Libraries**,
   add the `Pololu_2815.pretty` folder to **Project Specific Libraries**.
   Use the nickname `Pololu_2815` to resolve the preassigned footprint.
4. Place `Pololu_2815:Pololu_2815` in the schematic and update the PCB.

## Assembly and pinout

Mount the module component-side up on two straight 1×6 soldered headers.
The footprint uses Ø1.00 mm plated holes for nominal 0.64 mm square posts.
The pitch within each row is 2.54 mm and the rows are 17.78 mm apart.
The 20.32 × 22.86 mm PCB outline is on F.Fab. The courtyard includes
the slide lever overhang. Leave access to move the lever.

Viewed from above with the lever at the bottom, the square VIN pad
at the top of the left row is the footprint origin.

| Y (mm) | Left row, X = 0 mm | Right row, X = 17.78 mm |
| ---: | --- | --- |
| 0.00 | 1 VIN | 2 VOUT |
| 2.54 | 1 VIN | 2 VOUT |
| 5.08 | 3 GND | 3 GND |
| 7.62 | 3 GND | 3 GND |
| 10.16 | 4 ON | 3 GND |
| 12.70 | 3 GND | 5 SW |

The footprint uses the two side headers. Leave the four large terminal
holes and the three center switch holes on the module empty for this assembly.
Each repeated pad number is assigned to the same schematic net.
For loads above 5 A, Pololu calls for both small holes per power connection
when using the side headers. Route both VIN pads and both VOUT pads,
and provide adequate ground return copper and header current capacity.

With the onboard slide switch off, drive ON high for logic control or
connect an external switch between SW and GND. Leave ON and SW open
for onboard slide switch operation.

KiCad 10.0.8 parsed both library files. Physical fit and current capacity
have not been tested.

- [Pololu product documentation](https://www.pololu.com/product/2815)
- [Pololu top-view pinout](https://a.pololu-files.com/picture/0J6941.1200.jpg)
- [Pololu mechanical drawing](https://www.pololu.com/file/0J1104/big-mosfet-slide-switch-with-reverse-voltage-protection-dimension-diagram.pdf)
