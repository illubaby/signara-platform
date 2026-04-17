**UCIe**** ****PHY ****Voltage Regulator**

Databook

e 2.0

Library: dwc_ucie2phy_vreg

Cell:

- dwc_ucie2phy_vregll
- dwc_ucie2phy_vregml
- dwc_ucie2phy_vreghl
- dwc_ucie2phy_vregvdd
Copyright Notice and Proprietary Information Notice

Copyright © 2025 Synopsys, Inc. All rights reserved. This software and documentation contain confidential and proprietary information that is the property of Synopsys, Inc. The software and documentation are furnished under a license agreement and may be used or copied only in accordance with the terms of the license agreement. No part of the software and documentation may be reproduced, transmitted, or translated, in any form or by any means, electronic, mechanical, manual, optical, or otherwise, without prior written permission of Synopsys, Inc., or as expressly provided by the license agreement.

Destination Control Statement

All technical data contained in this publication is subject to the export control laws of the United States of America. Disclosure to nationals of other countries contrary to United States law is prohibited. It is the reader's responsibility to determine the applicable regulations and to comply with them.

Disclaimer

SYNOPSYS, INC., AND ITS LICENSORS MAKE NO WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, WITH REGARD TO THIS MATERIAL, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.

Trademarks

Synopsys and certain Synopsys product names are trademarks of Synopsys, as set forth at

All other product or company names may be trademarks of their respective owners.

Synopsys, Inc.690 E. Middlefield RoadMountain View, CA 94043

# Revision History

| Date | Owner | Revision | Approve by | Description |
| --- | --- | --- | --- | --- |
| **Dec 29, 2025** | Tri Vo | 0.81 | Tri Vo | Change Vref_bg/VregVddAnalogTestOut_VIO related power from VPH to VDD () |
| **Jul 19, 2025** | Anh Vu | 0.8 | Tri Vo | Update internal circuit to support VDD voltage reference (). Update Table 34 Update Analog testout implementation with voltage divider. |
| **May 09, 2025** | Tri Vo | 0.76 | Tri Vo | Remove _a/_s in cell name |
| **Apr 1****1****, 2025** | Tri Vo | 0.75 | Tri Vo | Change cell name following the new conventional name (UCIe-A/S, EW/NS PHY orientation Add new RTL requirement (When PHY operates at the fixed 4Gbps, user must configure all VREGs into the bypass mode) |
| **Mar**** 19, 2025** | Anh Vu | 0.7 | Tri Vo | Update block diagram of dwc_ucie2phy_vreg Update Settling time 1 = 50ns Update Settling time 2 = 5ns |
| **Dec 17, 2024** | Tri Vo | 0.6 | Tri Vo | Add pin VregFeedbackIn Change pin name VregVddStandBy to VregVddBleederEn Update truth table to clarify the function of Iddq and BleederEn Update setting for DFT, Burn-in test and Aging |
| **Oct 28, 2024** | Tri Vo | 0.51 | Tri Vo | Add note of vref settling time Update anti-aging setting |
| **Sep 05, 2024** | Tri Vo | 0.5 | Tri Vo | Add new cell dwc_ucie2phy_vreg_vdd |
| **Aug 30, 2024** | Tri Vo | 0.41 | Tri Vo | Change direction of VregVddAnalogTestOut_VIO from input to inout. Correct table 3-5 |
| **Aug 18, 2024** | Tri Vo | 0.4 | Tri Vo | Change cell name dwc_ucie2phy_vreg_6/15/56ma to dwc_ucie2phy_vreg_ll/ml/hl Change scale factor in table Table 34 Change pin name: IDDQ_mode to IddqMode VREF_BG to Vref_bg csrVregVDDAnalogTestOutSel[4:0] to csrVregVddAnalogTestOutSel[1:0] VIO_VregVDDAnalogTestOut to VregVddAnalogTestOut_VIO Remove pin scan_mode Add pin VregVddCurrAdj[1:0] |
| **Aug 01****, 2024** | Tri Vo | 0.3 | Tri Vo | Change pin VDD_REG to VDDREG Add DFT and Burn-in test recommendation |
| **Jul 22, 2024** | Tri Vo | 0.2 | Tri Vo | Change power pin VDDQ to VPH Add vreg 6ma Change name vreg_12ma to vreg_ml |
| **Apr 24, 2024** | Cuong Le | 0.1 | Tri Vo | Initial version for pin list and functional diagram only |

# Introduction

The Voltage Regulator block generates a voltage supply that is independent of power source and load variations. Hence, it is used to overcome the loading effect and enhance PSRR. By utilizing both Bandgap (as the reference voltage) and Vreg blocks a voltage reference which is independent of power supply, loading and temperature variations is produced.

# Operating Conditions

## RECOMMENDED OPERATING CONDITIONS

Table 21: Recommended operating conditions

| Parameter | Description | Min | Typ | Max | Unit |
| --- | --- | --- | --- | --- | --- |
| VPH | 1.2V supply Voltage | 1.08 | 1.2 | 1.32 | V |
| VDD | Core supply Voltage | 0.713 | 0.75 | 0.788 | V |
| VCCAON | Always on power supply | 0.713 | 0.75 | 0.788 | V |
| VSS | Core ground Voltage | 0 | 0 | 0 | V |
| Tj | Junction Temperature | -40 | 25 | 125 | oC |

## CELL LIST

Table 22: List of instances

| **Cell name** | **Description** |
| --- | --- |
| dwc_ucie2phy_vregll_ns | 6mA max load Programmable output voltage with the referent voltage is from bandgap cell. Support UCIe-A/S, NS PHY orientation |
| dwc_ucie2phy_vregll_ew | 6mA max load Programmable output voltage with the referent voltage is from bandgap cell. Support UCIe-A/S, EW PHY orientation |
| dwc_ucie2phy_vregml_ns | 15mA max load Programmable output voltage with the referent voltage is from bandgap cell. Support UCIe-A/S, NS PHY orientation |
| dwc_ucie2phy_vregml_ew | 15mA max load Programmable output voltage with the referent voltage is from bandgap cell. Support UCIe-A/S, EW PHY orientation |
| dwc_ucie2phy_vreghl_ns | 30mA max load Programmable output voltage with the referent voltage is from bandgap cell. Support UCIe-A/S, NS PHY orientation |
| dwc_ucie2phy_vreghl_ew | 30mA max load Programmable output voltage with the referent voltage is from bandgap cell. Support UCIe-A/S, EW PHY orientation |
| dwc_ucie2phy_vregvdd_ns | 8mA max load Fixed output voltage to be VDD level. The referent voltage is core VDD (through RC filter). Support UCIe-A/S, NS PHY orientation |
| dwc_ucie2phy_vregvdd_ew | 8mA max load Fixed output voltage to be VDD level. The referent voltage is core VDD (through RC filter) Support UCIe-A/S, EW PHY orientation |

## LIBRARY CHARACTERIZATION CORNERS

Table 23: Corners for library characterization

| Process | Core Voltage (V) | Temperature (C) | RC Corner |
| --- | --- | --- | --- |
| SSG | 0.675 | -40 | typical |
| SSG | 0.675 | 125 | typical |
| FFG | 0.825 | -40 | typical |
| FFG | 0.825 | 125 | typical |
| SSG | 0.675 | 0 | typical |
| FFG | 0.825 | 0 | typical |
| TT | 0.75 | 25 | typical |

# dwc_ucie2phy_vreg*

## FEATURES

The regulator generates the regulated VDD supply with good power noise rejection ratio. The output is used to provide power for the critical analog hard macros.

Powered under VPH domain, the regulator uses the referent voltage from a bandgap or core VDD (through RC filter) as input reference. Refer to Table 22 for more information.

## PINS DESCRIPTION

Table 31: Pin Description of dwc_ucie2phy_vregll/ml/hl_*

| **Pin** | **Direction** | **Type** | **Domain** | **Clock** | **Description** |
| --- | --- | --- | --- | --- | --- |
| VPH | Input | Power | VPH | - | 1.2v IO supply |
| VCCAON | Input | Power | VCCAON | - | supply |
| VDD | Input | Power | VDD | - | Core supply |
| VSS | Input | Ground | VSS | - | Common ground |
| PwrOk_VAON | Input | Digital | VCCAON | Async | Indicates VDD is not ready when not asserted |
| VregVddByPass | Input | Digital | VDD | Async | Used to Bypass the regulator |
| VregVddBleederEn | Input | Digital | VDD | Async | Enable bleeder current when VREG is in low load condition or no load condition |
| VregVddPowerDown | Input | Digital | VDD | Async | Power Down the regulator |
| VregVddCurrAdj[1:0] | Input | Digital | VDD | Async | Adjust bias current, can share across all vreg macro Default value: 00 |
| VregFeedbackIn | Input | Analog | VPH | Async | Feedback voltage, connect to VDDREG mesh next to the loading |
| csrVregVddProg[2:0] | Input | Digital | VDD | Async | VDDREG Programmable bits Used to program either reference VDD or Output VDDREG. Default value: 010 |
| IddqMode | Input | Digital | VDD | Async | IDDQ Test Mode Select. It has the same function as VregVddPowerDown |
| Vref_bg | Input | Analog | VDD | Async | Voltage Reference |
| csrVregVddAnalogTestOutSel[1:0] | Input | Digital | VDD | Async | Selection analog test. Default value: 00 |
| VDDREG | Output | Analog | VPH | Async | Regulator Output voltage |
| VregVddAnalogTestOut_VIO | Inout | Analog | VDD | Async | Analog observability output. Short to master analog test signal. It has 5kohm connected in series |

Table 32 Pin Description of dwc_ucie2phy_vregvdd_*

| **Pin** | **Direction** | **Type** | **Domain** | **Clock** | **Description** |
| --- | --- | --- | --- | --- | --- |
| VPH | Input | Power | VPH | - | 1.2v IO supply |
| VCCAON | Input | Power | VCCAON | - | supply |
| VDD | Input | Power | VDD | - | Core supply |
| VSS | Input | Ground | VSS | - | Common ground |
| PwrOk_VAON | Input | Digital | VCCAON | Async | Indicates VDD is not ready when not asserted |
| VregVddByPass | Input | Digital | VDD | Async | Used to Bypass the regulator |
| VregVddBleederEn | Input | Digital | VDD | Async | Enable bleeder current when VREG is in low load condition or no load condition |
| VregVddPowerDown | Input | Digital | VDD | Async | Power Down the regulator |
| VregVddCurrAdj[1:0] | Input | Digital | VDD | Async | Adjust bias current, can share across all vreg macro Default value: 00 |
| IddqMode | Input | Digital | VDD | Async | IDDQ Test Mode Select, it has the same function as VregVddPowerDown |
| VregFeedbackIn | Input | Analog | VPH | Async | Feedback voltage, connect to VDDREG mesh next to the loading |
| csrVregVddAnalogTestOutSel[1:0] | Input | Digital | VDD | Async | Selection analog test Default value: 00 |
| VDDREG | Output | Analog | VPH | Async | Regulator Output voltage |
| VregVddAnalogTestOut_VIO | Inout | Analog | VDD | Async | Analog observability output. Short to master analog test signal. It has 5kohm connected in series |

## FUNCTIONAL DESCRIPTION

### Block diagram

Figure 31 Block diagram of dwc_ucie2phy_vregll/ml/hl

Figure 32 Block diagram of dwc_ucie2phy_vregvdd

### Operation mode

Table 33: Regulator function mode

| Mode | VIO Supply | Core Supply | PwrOk _VAON | VregVdd ByPassMode | VregVdd PowerDown | IddqMode | VregVddBleederEn | VREG status | ByPass Switch | VDDREG Load Cond. | VDDREG at I/O pins |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Power-Up | 0 | 0 | 0 | 0 | 0 | 0 | 0 | OFF | OFF | - | VSS |
| Reverse L3 | 0 | VDD | 1 | 0 | 0 | 0 | 0 | OFF | OFF | - | VSS |
| L3 | VPH | 0 | 0 | 0 | 0 | 0 | 0 | OFF | OFF | - | VSS |
| ByPass | VPH | VDD | 1 | 1 | - | **-** | 0 | OFF | ON | Low* | VDDREG = VDD |
| Power Down | VPH | VDD | 1 | 0 | 1 | 0 | - | OFF | OFF | Low* | VSS |
| Iddq | VPH | VDD | 1 | 0 | 0 | 1 | 0 | OFF | ON | Low* | VDDREG = VDD |
| Mission | VPH | VDD | 1 | 0 | 0 | 0 | 1 | ON | OFF | No or very Low* | VDDREG |
| Mission | VPH | VDD | 1 | 0 | 0 | 0 | 0 | ON | OFF | High/Low | VDDREG |

‘-‘ is don’t care.

* PowerDown/StandBy/ByPass exit in low load condition

### VDDREG programmability truth table

The regulator output voltage can be programmed as Table 34. csrVregVddProg[2] is used to select the voltage reference, Vref_bg or internal core supply. And csrVregVddProg[1:0] is used to select the feedback ratio.

Table 34: Truth table for Regulator programmability

| csrVregVddProg[2:0] | Vref | VDDREG |
| --- | --- | --- |
| 000 | VDD | VDD |
| 001 | VDD | 0.95*vddreg_target |
| 010 | VDD | 1.00*vddreg_target |
| 011 | VDD | 1.02*vddreg_target |
| 100 | Vreg_bg | 0.90*vddreg_target |
| 101 | Vreg_bg | 0.95*vddreg_target |
| 110 | Vreg_bg | 1.00*vddreg_target |
| 111 | Vreg_bg | 1.02*vddreg_target |

Note:

- Only applicable for vregll/ml/hl
- vddreg_target is a desired VREG output voltage. The feedback ratio is calculated from the target level and the referent voltage. Example:
- Target output voltage: 0.85v
- Referent voltage: VDD = 0.75v
- Feedback ratio = 0.85 / 0.75 = 1.133
- 0.9/0.95/1.00/1.02 are scale options which can be used for Silicon debug or power optimization. The factor may vary depending on technology. User must ensure that the max VREG output are less than the allowed voltage by technology.
### Bias generator

Table 35 Bias output current adjustment

| VregVddCurrAdj[1:0] | Description |
| --- | --- |
| 00 | Typical output current |
| 01 | Higher than VregVddCurrAdj[1:0] = 00 |
| 11 | Higher than VregVddCurrAdj[1:0] = 01 |

### Analog test-out truth table

Table 36: Truth table for Analog test-out

| csrVregVddAnalogTestOutSel [1:0] | VregVddAnalogTestOut_VIO |
| --- | --- |
| 00 | High-z |
| 01 | Regulator output voltage |
| 10 | High-z |
| 11 | High-z |

There is voltage divider inside analog test block, so the actual voltage at VregVddAnalogTestOut_VIO is a half of VDDREG.

Figure 33 Analog test implementation

### Feedback voltage connection

The voltage drop may be large due to the wire connection from VREG output to the loading. To compensate for this drop, the feedback voltage to VREG error amplifier can be hooked up at a point that close to the loading (sense point).

The feedback voltage needs to be shielded, and the resistance of the connection must be less than 100ohm.

Figure 34 Example of VrefFeedbackIn connection when voltage drop is concerned

Figure 35 Example of VrefFeedbackIn connection when voltage drop is NOT concerned

### Bleeder current usage

Bleeder current is used to improve VREG stability when it is in mission mode but:

- No load
- Low load: current consumption is less than 1mA (TBU)
- Mixed between No load and High/Low load: Phy initialization, PHY data rate negotiation
When PHY has done all initialization, training and data rate negotiation (clock frequency is stable), VregVddBleederEn can be kept asserting and then deassert but before data transaction. Minimum allowed time is “settling time 2”. VregVddBleederEn can be asserted before stopping clock but after stopping data transaction (t1). Minimum allowed time is “settling time 2”.

## ELECTRICAL PARAMETERS

### DC/TRAN specification

| Specification | Description | Min | Max | Unit | Notes |
| --- | --- | --- | --- | --- | --- |
| Vreg Voltage | Vreg output voltage | 780 | 860 | mV | vreg_ll/ml/hl +/- 5 % of nominal 820mV (PVT) |
|  |  | VDD | mV | vreg_vdd |  |
| Vreg Voltage Error | Percentage error of nominal voltage | -3 | +3 | % | MC variation |
| Load Regulation | The change in vreg output voltage with respect to load current variation. | none | none | uV/A |  |
| Line Regulation | The change in vreg output voltage with respect to supply voltage variation. | none | none | uV/V |  |
| Current Consumption VPH | Current drawing from vph supply (excluding Iout). | 0.2 | 2 | mA |  |
| Current Consumption VDD | Current drawing from vp supply. | 5 | 100 | uA |  |
| Output Ripple Voltage | Peak to Peak output voltage ripple | none | none | V |  |
| Overshoot | Overshoot measured during load transition |  | 120 | mV |  |
| Undershoot | Undershoot measured during load transition |  | 120 | mV |  |
| Startup time | Time from power down/bypass mode to mission mode (Vout reaches 95% its final value) |  | 100ns | ns | No load and with bleeder ON |
| Settling time 1 | Settling time from Low Load to High Load Transition (Vout reaches 95% its final value) |  | 50 | ns |  |
| Settling time 2 | Settling time of bleeder current enable/disable to Vout valid (Vout reaches 95% its final value) |  | 5 | ns |  |

### AC specification

| Specification | Description | Min | Max | Unit | Notes |
| --- | --- | --- | --- | --- | --- |
| DC gain | DC gain Slow/Fast loop @ Low/High load | 20 | none | dB |  |
| Phase margin |  | 50 |  | deg | Both load conditions standby low load |
| PSRR Mean @1KHz | VPH supply rejection ratio output voltage @ 1KHz | -20 | none | dB |  |
| PSRR Mean @1MHz | VPH supply rejection ratio output voltage @ 1MHz | -20 | none | dB |  |
| PSRR Mean @400MHz | VPH supply rejection ratio output voltage @ 400MHz | -20 | none | dB |  |

### INTEGRATION GUIDELINE

### DFT

| Pin | Value |
| --- | --- |
| VregVddByPass | 1 |
| VregVddPowerDown | 0 |
| VregVddBleederEn | 0 |
| IddqMode | 0 |
| csrVregVddAnalogTestOutSel[1:0] | 2’b00 |

### IDDQ MODE

Table 37 IDDQ setting

| Pin | Value |
| --- | --- |
| IddqMode | 1 |

### REFERENT VOLTAGE SETTLING TIME

For reliability, user only enable the regulator when and only when the referent voltage (Vref_bg) is settled. For example, if Vref_bg is provided by a bandgap, user must wait for the bandgap settled.

### BURN-IN TEST RECOMMENDATION

The recommendation is to configure VREG into Mission mode. The reference voltage is VDD level and adjust the feedback factor to 1 so that the Vreg output voltage is followed VDD.

Table 38 Burn-in test and Anti-aging setting

| Pin | Value |
| --- | --- |
| csrVregVddProg[2:0] | 000 |

### ANTI-AGING RECOMMENDATION

The recommendation is to configure the VREG into bypass mode

Figure 36 Anti-aging setting

| Pin | Value |
| --- | --- |
| VregVddByPass | 1 |

### EMIR CONDITION

Table 39 EMIR condition

| **Parameter** | **EM (*)** | **IR** |  |
| --- | --- | --- | --- |
| Process | FF | FF | SS |
| Voltage supply | Vtyp + 5% | Vtyp + 5% | Vtyp – 10% for VDD Vtyp – 5% for VCCIO |
| Temperature | 105C | 105C | -40C/105C |
| RC extraction | Typical with temperature sensitivity | Typical with temperature sensitivity | Typical with temperature sensitivity |
| Operation mode | Full mode operation, max data rate | Full mode operation, max data rate | Full mode operation, max data rate |
| Time step (ratau) | 3ps | 3ps | 3ps |
| Pass condition | [1 (iavg, irms, acpc) | [15mV for each (VDD-VSS) [8mV for (VCCIO-VSS) [15mV for (VCCAON-VSS) | [15mV for each (VDD-VSS) [8mV for (VCCIO-VSS) [15mV for (VCCAON-VSS) |

### RDIE and CDIE

TBU

### RTL AND TIMING REQUIREMENTS

When PHY operates at the fixed 4Gbps, user must configure all VREGs into the bypass mode.

## TESTBENCHES

| **No** | **Testbench** | **Description ** |
| --- | --- | --- |
| 1 |  |  |
| 2 |  |  |
| 3 |  |  |
| 4 |  |  |
| 5 |  |  |
| 6 |  |  |
| 7 |  |  |
| 9 |  |  |
| 10 |  |  |
| 11 |  |  |
| 12 |  |  |
| 14 |  |  |
